#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_company_report.py — Generate a company report (Markdown) via FinRobot SingleAssistant
Robust extraction: prefer message buffers, then parse stdout logs; provide hints on news window and degrade gracefully on errors.
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

def _score_markdown(text: str) -> int:
    """A simple 'looks-like-a-report' scorer: checks Markdown structure and length."""
    score = len(text)
    if re.search(r'(?m)^\s*#', text): score += 1500
    if re.search(r'(?m)^\s*##', text): score += 800
    if re.search(r'(?m)^\s*[-*]\s+\*\*.+?\*\*', text): score += 300  # list items with bold
    if "Positives" in text or "Risks" in text or "Catalysts" in text: score += 300
    if "Prediction" in text or "Recommendation" in text or "Conclusion" in text: score += 200
    return score

def harvest_from_buffers(sa_obj) -> str | None:
    """Extract the 'best assistant text' from Autogen/FinRobot message buffers rather than only the last one."""
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

    # 1) Prefer searching under the assistant object's chat_messages
    try:
        agent = sa_obj.assistant
        cm = getattr(agent, "chat_messages", None)
        if isinstance(cm, dict):
            # chat_messages may be keyed by participants; merge and iterate
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

    # 2) Some versions hang messages elsewhere; do a fallback scan
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
    Parse console logs to extract the Markdown section produced by Market_Analyst.
    Rule: find blocks starting with 'Market_Analyst (to User_Proxy):' until the next separator or TERMINATE.
    """
    blocks = []
    pattern = r"Market_Analyst \(to User_Proxy\):\s*\n(.*?)(?:\n[-]{5,}|\nTERMINATE|\Z)"
    for m in re.finditer(pattern, stdout_text, flags=re.S):
        chunk = m.group(1).strip()
        if chunk:
            blocks.append(chunk)
    if not blocks:
        return None
    # Choose the most 'report-like' block
    best = max(blocks, key=_score_markdown)
    return best

def main():
    import autogen  # used only for version checking / clearer errors
    ap = argparse.ArgumentParser(description="Robustly generate a company report (Markdown)")
    ap.add_argument("--ticker", required=True, help="Stock ticker, e.g., NVDA, MSFT")
    ap.add_argument("--oai-config", default="./OAI_CONFIG_LIST.json", help="Path to OAI_CONFIG_LIST.json")
    ap.add_argument("--keys-config", default="./config_api_keys.json", help="Data-source keys JSON (e.g., Finnhub/FMP)")
    ap.add_argument("--model", default="gpt-4-0125-preview", help="Model name to use")
    ap.add_argument("--outdir", default="./reports", help="Output directory")
    ap.add_argument("--news-days", type=int, default=7, help="News lookback window in days (default 7)")
    args = ap.parse_args()

    llm_config = build_llm_config(args.model, args.oai_config)

    # Register external data-source keys (if present)
    try:
        from finrobot.utils import register_keys_from_json
        if args.keys_config and Path(args.keys_config).exists():
            register_keys_from_json(args.keys_config)
    except Exception:
        print("[warn] Failed to register keys; continuing to generate a text-only report.")

    from finrobot.utils import get_current_date
    from finrobot.agents.workflow import SingleAssistant

    assistant = SingleAssistant("Market_Analyst", llm_config, human_input_mode="NEVER")

    asof = get_current_date()
    # Explicitly specify a news window to reduce the chance of agents picking wrong dates
    try:
        # get_current_date() returns YYYY-MM-DD; compute start date string for hinting
        today = datetime.strptime(asof, "%Y-%m-%d").date()
        start = (today - timedelta(days=args.news_days)).isoformat()
        end = today.isoformat()
        news_hint = f"News window: {start} to {end}. If tooling needs dates, use this window."
    except Exception:
        news_hint = "Use the most recent 7 days of news."

    prompt = (
        f"Use all available tools for {args.ticker} as of {asof}. "
        f"{news_hint} "
        "If any tool fails or returns empty, continue with available data; do not abort. "
        "Produce 2–4 positives and 2–4 risks from recent news/financials, "
        "then a next-week move prediction (~2–3%) with catalysts and confidence. "
        "Output a clean Markdown report with clear headings (H1/H2), bullet points, and a final Recommendation."
    )

    print(f"[run] Generating report for {args.ticker} as of {asof} ...")
    # Capture stdout for fallback parsing
    log_buf = StringIO()
    with redirect_stdout(log_buf):
        result = assistant.chat(prompt)
    stdout_text = log_buf.getvalue()

    # 1) Prefer extracting from message buffers
    report_md = harvest_from_buffers(assistant)

    # 2) If buffers are empty, parse stdout
    if not report_md:
        report_md = parse_report_from_stdout(stdout_text)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = outdir / f"{args.ticker}_company_report_{ts}.md"

    # 3) Still empty — write placeholder and save full log for debugging
    if not report_md or not report_md.strip():
        report_md = (
            f"# {args.ticker} — Report\n\n(no result)\n\n"
            "> Possible causes:\n"
            "> 1) Agent tool calls failed or returned empty;\n"
            "> 2) Autogen version printed content only to stdout;\n"
            "> 3) We failed to extract from message buffers/logs.\n"
            "> Full runtime logs have been saved for diagnosis."
        )
        log_path = outdir / f"{args.ticker}_runlog_{ts}.txt"
        log_path.write_text(stdout_text, encoding="utf-8")
        print(f"[warn] No report text extracted. Full log saved: {log_path}")

    md_path.write_text(report_md, encoding="utf-8")
    print(f"[ok] Markdown saved: {md_path}")

    # Preview
    print("\n===== PREVIEW (first 40 lines) =====")
    for line in report_md.splitlines()[:40]:
        print(line)
    print("===== END PREVIEW =====")

if __name__ == "__main__":
    main()
