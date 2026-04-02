#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
make_macro_report.py — Macro Analysis Agent
Read the latest FOMC meeting transcript PDF + fetch recent macro news to generate a macro environment report (Markdown).
"""

from __future__ import annotations
import argparse
import os
import re
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from datetime import datetime, timedelta

def build_llm_config(model: str, oai_config_path: str | None):
    """Build LLM configuration"""
    import autogen
    if oai_config_path:
        try:
            cfg_list = autogen.config_list_from_json(
                oai_config_path, filter_dict={"model": [model]}
            )
        except TypeError:
            cfg_list = autogen.config_list_from_json(
                oai_config_path, filter={"model": [model]}
            )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("No --oai-config provided and environment variable OPENAI_API_KEY is empty.")
        cfg_list = [{"model": model, "api_key": api_key}]
    if not cfg_list:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OAI_CONFIG_LIST did not match the model, and OPENAI_API_KEY is empty.")
        cfg_list = [{"model": model, "api_key": api_key}]
    return {"config_list": cfg_list, "timeout": 120, "temperature": 0}

def extract_fomc_pdf(pdf_path: str) -> str:
    """Extract the full FOMC PDF using pdfplumber"""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber is required: pip install pdfplumber")

    with pdfplumber.open(pdf_path) as pdf:
        pages_text = []
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Page {i} ---\n{text}")
        return "\n\n".join(pages_text)

def _score_markdown(text: str) -> int:
    """Heuristic scorer: estimate whether text looks like a complete report"""
    score = len(text)
    if re.search(r'(?m)^\s*#', text): score += 1500
    if re.search(r'(?m)^\s*##', text): score += 800
    if re.search(r'(?m)^\s*[-*]\s+\*\*.+?\*\*', text): score += 300
    if "Monetary Policy" in text or "Inflation" in text or "Labor" in text: score += 300
    if "Rates" in text or "Economic Growth" in text or "Risks" in text: score += 200
    return score

def harvest_from_buffers(sa_obj) -> str | None:
    """Fetch the 'best assistant text' from Autogen/FinRobot message buffers rather than only the last one"""
    candidates = []

    def extract_text(content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    if isinstance(p.get("text"), str):
                        parts.append(p["text"])
                    elif isinstance(p.get("content"), str):
                        parts.append(p["content"])
            if parts:
                return "\n".join(parts)
        return None

    # 1) Search within the assistant object's chat_messages
    try:
        agent = sa_obj.assistant
        cm = getattr(agent, "chat_messages", None)
        if isinstance(cm, dict):
            all_msgs = []
            for v in cm.values():
                if isinstance(v, list):
                    all_msgs.extend(v)
            for m in all_msgs:
                role = (m.get("role") or m.get("source") or "").lower()
                if role in ("assistant", "system_assistant", "ai", "bot"):
                    t = extract_text(m.get("content"))
                    if t and t.strip():
                        candidates.append(t.strip())
    except Exception:
        pass

    # 2) Fallback: search on sa_obj itself
    try:
        raw_cm = getattr(sa_obj, "chat_messages", None)
        if isinstance(raw_cm, dict) and not candidates:
            for v in raw_cm.values():
                if isinstance(v, list):
                    for m in v:
                        t = extract_text(m.get("content"))
                        if t and t.strip():
                            candidates.append(t.strip())
    except Exception:
        pass

    if not candidates:
        return None

    # Choose the most 'report-like' one
    best = max(candidates, key=_score_markdown)
    return best

def parse_report_from_stdout(stdout_text: str) -> str | None:
    """
    Parse console logs to extract the Markdown block produced by Market_Analyst
    """
    blocks = []
    pattern = r"Market_Analyst \(to User_Proxy\):\s*\n(.*?)(?:\n[-]{5,}|\nTERMINATE|\Z)"
    for m in re.finditer(pattern, stdout_text, flags=re.S):
        chunk = m.group(1).strip()
        if chunk:
            blocks.append(chunk)
    if not blocks:
        return None
    best = max(blocks, key=_score_markdown)
    return best

def main():
    ap = argparse.ArgumentParser(description="Generate macro analysis report (FOMC + macro news)")
    ap.add_argument("--fomc-pdf", required=True, help="Path to the FOMC meeting transcript PDF")
    ap.add_argument("--oai-config", default="./OAI_CONFIG_LIST.json", help="Path to OAI_CONFIG_LIST.json")
    ap.add_argument("--keys-config", default="./config_api_keys.json", help="Data source keys JSON")
    ap.add_argument("--model", default="gpt-4-0125-preview", help="Model name to use")
    ap.add_argument("--outdir", default="./reports", help="Output directory")
    ap.add_argument("--news-days", type=int, default=14, help="Macro news lookback window in days (default 14)")
    args = ap.parse_args()

    fomc_path = Path(args.fomc_pdf).expanduser().resolve()
    if not fomc_path.exists():
        raise FileNotFoundError(f"FOMC PDF not found: {fomc_path}")

    llm_config = build_llm_config(args.model, args.oai_config)

    # Register external data source keys (if present)
    try:
        from finrobot.utils import register_keys_from_json
        if args.keys_config and Path(args.keys_config).exists():
            register_keys_from_json(args.keys_config)
    except Exception:
        print("[warn] Failed to register keys; continuing to generate a text report.")

    # 1) Extract full FOMC PDF
    print(f"[1/3] Extracting FOMC PDF: {fomc_path.name} ...")
    fomc_text = extract_fomc_pdf(str(fomc_path))
    print(f"      Extracted {len(fomc_text)} characters")

    # 2) Prepare macro news window
    from finrobot.utils import get_current_date
    asof = get_current_date()
    try:
        today = datetime.strptime(asof, "%Y-%m-%d").date()
        start = (today - timedelta(days=args.news_days)).isoformat()
        end = today.isoformat()
        news_hint = f"Macro news window: {start} to {end}. Use tools to get the latest macro news (inflation, employment, GDP, Fed policy expectations)."
    except Exception:
        news_hint = "Use the most recent 14 days of macro news."

    # 3) Build prompt
    prompt = f"""
You are a macro economist. Analyze the following materials:

==== FOMC PRESS CONFERENCE TRANSCRIPT ====
{fomc_text}
==== END FOMC ====

{news_hint}

Based on the FOMC transcript and recent macro news, provide a comprehensive macro analysis report covering:

1. **Monetary Policy Stance**: Current Fed position, rate path expectations, balance sheet policy
2. **Inflation Outlook**: Latest CPI/PCE trends, Fed's inflation assessment, targets
3. **Labor Market**: Employment data, unemployment rate, wage growth, labor force participation
4. **Economic Growth**: GDP trends, consumer spending, business investment
5. **Market Impact**: How current macro conditions affect equity markets, specific sectors
6. **Risks & Catalysts**: Key upside/downside risks for the economy and markets

If any tool fails or returns empty, continue with available information. Do not abort.
Output a clean Markdown report with clear H1/H2 headings and bullet points.
"""

    from finrobot.agents.workflow import SingleAssistant
    assistant = SingleAssistant("Market_Analyst", llm_config, human_input_mode="NEVER")

    print(f"[2/3] Generating macro report (LLM call)...")
    # Capture stdout
    log_buf = StringIO()
    with redirect_stdout(log_buf):
        result = assistant.chat(prompt)
    stdout_text = log_buf.getvalue()

    # 4) Extract report
    print(f"[3/3] Extracting and saving report...")
    report_md = harvest_from_buffers(assistant)

    if not report_md:
        report_md = parse_report_from_stdout(stdout_text)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = outdir / f"MACRO_report_{ts}.md"

    # If still empty, write a placeholder and save logs
    if not report_md or not report_md.strip():
        report_md = (
            f"# Macro Analysis Report\n\n(no result)\n\n"
            f"> Possible causes:\n"
            f"> 1) Agent tool calls failed or returned empty;\n"
            f"> 2) Autogen version printed content only to stdout;\n"
            f"> 3) We failed to extract from message buffers/logs.\n"
            f"> Full runtime logs have been saved for diagnosis."
        )
        log_path = outdir / f"MACRO_runlog_{ts}.txt"
        log_path.write_text(stdout_text, encoding="utf-8")
        print(f"[warn] No report text extracted. Full log saved: {log_path}")

    md_path.write_text(report_md, encoding="utf-8")
    print(f"[ok] Macro report saved: {md_path}")

    # Preview
    print("\n===== PREVIEW (first 40 lines) =====")
    for line in report_md.splitlines()[:40]:
        print(line)
    print("===== END PREVIEW =====")

if __name__ == "__main__":
    main()
