#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
final_decision_agent.py — Final Decision Agent
Merge Macro Analysis Report + Company Analysis Report to produce
an actionable stock investment recommendation (Markdown).

Architecture:
1) Macro Agent (make_macro_report.py)  →  Macro Environment Report
2) Company Agent (make_company_report.py)  →  Company Fundamentals Report
3) Final Agent (this file)  →  Combine macro + company to produce a concrete recommendation
"""

from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from io import StringIO
from contextlib import redirect_stdout

def build_llm_config(model: str, oai_config_path: str | None):
    """Build the LLM configuration dict for FinRobot/Autogen."""
    import autogen
    if oai_config_path:
        try:
            cfg_list = autogen.config_list_from_json(
                oai_config_path, filter_dict={"model": [model]}
            )
        except TypeError:
            # For older autogen versions that use `filter=` instead of `filter_dict=`
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

def _sanitize_markdown(s: str) -> str:
    """Remove fenced code blocks, trim whitespace, and prevent 'None' from leaking into output."""
    if not s:
        return ""
    s = str(s).strip()
    if s.lower() == "none":
        return ""
    # Strip fenced code blocks ```...```
    if s.startswith("```") and s.endswith("```"):
        s = re.sub(r"^```[^\n]*\n", "", s, count=1, flags=re.S)
        s = re.sub(r"\n```$", "", s, count=1)
    return s.strip()

def _read_text(p: Path, limit_chars=30000) -> str:
    """Read a text file and truncate to a maximum number of characters."""
    return p.read_text(encoding="utf-8", errors="ignore")[:limit_chars]

def _score_markdown(text: str) -> int:
    """Heuristic scorer: estimate whether text looks like a complete report."""
    score = len(text)
    if re.search(r'(?m)^\s*#', text): score += 1500
    if re.search(r'(?m)^\s*##', text): score += 800
    if re.search(r'(?m)^\s*[-*]\s+\*\*.+?\*\*', text): score += 300
    if "Bullish" in text or "Bearish" in text or "Neutral" in text: score += 500
    if "Recommendation" in text: score += 300
    return score

def harvest_from_buffers(sa_obj) -> str | None:
    """Extract the 'best assistant text' from Autogen/FinRobot chat buffers rather than the last message only."""
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

    # 1) Inspect assistant object's chat_messages
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

    # 2) Fallback
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

    best = max(candidates, key=_score_markdown)
    return best

def parse_report_from_stdout(stdout_text: str) -> str | None:
    """Parse console logs to extract the Markdown block produced by Expert_Investor."""
    blocks = []
    pattern = r"Expert_Investor \(to User_Proxy\):\s*\n(.*?)(?:\n[-]{5,}|\nTERMINATE|\Z)"
    for m in re.finditer(pattern, stdout_text, flags=re.S):
        chunk = m.group(1).strip()
        if chunk:
            blocks.append(chunk)
    if not blocks:
        return None
    best = max(blocks, key=_score_markdown)
    return best

class _TeeStdout:
    """A tee for redirected stdout that writes to both the real terminal and a buffer."""
    def __init__(self, original, buffer):
        self._orig = original
        self._buf = buffer
    def write(self, s):
        self._orig.write(s)
        self._buf.write(s)
    def flush(self):
        self._orig.flush()
        self._buf.flush()

def main():
    ap = argparse.ArgumentParser(
        description="Final Decision Agent: Combine macro + company reports → stock investment recommendation"
    )
    ap.add_argument("--macro-report", required=True, help="Path to macro analysis report (Markdown)")
    ap.add_argument("--company-report", required=True, help="Path to company analysis report (Markdown)")
    ap.add_argument("--ticker", required=True, help="Stock ticker, e.g., NVDA")
    ap.add_argument("--oai-config", default="./OAI_CONFIG_LIST.json", help="Path to OpenAI config list JSON")
    ap.add_argument("--keys-config", default="./config_api_keys.json", help="Path to data-source API keys JSON")
    ap.add_argument("--model", default="gpt-4-0125-preview", help="LLM model name")
    ap.add_argument("--outdir", default="./reports", help="Output directory for generated reports")
    ap.add_argument("--max-chars", type=int, default=30000, help="Truncate length for each input document")
    args = ap.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    macro_md = Path(args.macro_report).expanduser().resolve()
    company_md = Path(args.company_report).expanduser().resolve()

    if not macro_md.exists():
        raise FileNotFoundError(f"Macro report not found: {macro_md}")
    if not company_md.exists():
        raise FileNotFoundError(f"Company report not found: {company_md}")

    # 0) LLM config & keys
    llm_config = build_llm_config(args.model, args.oai_config)
    try:
        from finrobot.utils import register_keys_from_json
        if Path(args.keys_config).exists():
            register_keys_from_json(args.keys_config)
    except Exception:
        pass

    # 1) Read both reports
    print(f"[1/3] Reading macro report: {macro_md.name}")
    macro_text = _read_text(macro_md, limit_chars=args.max_chars)
    print(f"      Loaded {len(macro_text)} characters")

    print(f"[2/3] Reading company report: {company_md.name}")
    company_text = _read_text(company_md, limit_chars=args.max_chars)
    print(f"      Loaded {len(company_text)} characters")

    # 2) Compose materials and task
    material = (
        "You are an investment strategist. Use ONLY the following two reports to answer the TASK.\n\n"
        "========== MACRO ANALYSIS REPORT START ==========\n"
        + macro_text + "\n"
        + "========== MACRO ANALYSIS REPORT END ==========\n\n"
        + "========== COMPANY ANALYSIS REPORT START ==========\n"
        + company_text + "\n"
        + "========== COMPANY ANALYSIS REPORT END ==========\n\n"
    )

    question = (
        f"Based on the provided Macro Report and Company Report for {args.ticker}, synthesize a comprehensive investment recommendation:\n\n"
        f"1. **Macro Context Summary** (3-5 bullet points):\n"
        f"   - Fed policy stance, rate outlook, inflation/employment trends\n"
        f"   - How current macro conditions favor/hurt {args.ticker}'s sector\n\n"
        f"2. **Company-Specific Analysis** (3-5 positives, 3-5 risks):\n"
        f"   - Key strengths from fundamentals, news, earnings\n"
        f"   - Key risks or headwinds\n\n"
        f"3. **Tactical View (1 Week)**: Expected price movement with probability\n"
        f"   - Catalysts for upside/downside\n\n"
        f"4. **Strategic View (1-3 Months)**: Directional outlook with probability\n"
        f"   - Key drivers and inflection points\n\n"
        f"5. **Final Recommendation**:\n"
        f"   - **BULLISH** / **NEUTRAL** / **BEARISH** (choose ONE)\n"
        f"   - Entry/exit levels or position sizing guidance\n"
        f"   - Stop-loss and profit target suggestions\n"
        f"   - Key risk triggers to monitor\n\n"
        f"Return a clean, well-structured Markdown report with H1/H2 headings and bullet points.\n"
        f"Quote short evidence snippets from the reports when useful.\n"
        f"If any external tool call fails, rely solely on the provided reports."
    )

    # 3) Generate final decision using FinRobot SingleAssistant
    from finrobot.agents.workflow import SingleAssistant
    system_msg = (
        "You are an expert investment strategist. "
        "ONLY use the MACRO REPORT and COMPANY REPORT provided above. "
        "Do not use external tools unless absolutely necessary. "
        "If any tool fails, continue with the provided materials. "
        "Return pure Markdown prose (no fenced code blocks). "
        "Be decisive and actionable in your recommendation."
    )

    # Use the Expert_Investor agent from the FinRobot library (appropriate for investment decisions)
    agent = SingleAssistant(
        "Expert_Investor",
        llm_config,
        human_input_mode="NEVER",
        system_message=system_msg
    )

    prompt = material + "TASK:\n" + question

    print(f"[3/3] Generating final investment recommendation (LLM call)...")
    # Tee: print to terminal and capture stdout simultaneously
    log_buf = StringIO()
    tee = _TeeStdout(sys.__stdout__, log_buf)
    with redirect_stdout(tee):
        resp = agent.chat(prompt)
    stdout_text = log_buf.getvalue()

    # 4) Extract & sanitize
    text = None
    try:
        text = harvest_from_buffers(agent)
    except Exception:
        text = None

    if not text:
        try:
            text = parse_report_from_stdout(stdout_text)
        except Exception:
            text = None

    if not text:
        if isinstance(resp, str):
            text = resp
        elif resp:
            text = (
                getattr(resp, "content", None)
                or getattr(resp, "text", None)
                or getattr(resp, "message", None)
            )
        else:
            text = ""

    text = _sanitize_markdown(text)

    # Debug preview
    snippet = (text[:200] + "…") if text and len(text) > 200 else (text or "")
    print(f"\n[debug] Extracted content preview: {snippet}\n")

    # 5) Save Markdown
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    header = (
        f"# {args.ticker} — Final Investment Decision\n\n"
        f"_Generated: {ts}_\n\n"
        f"**Input Reports:**\n"
        f"- Macro: {macro_md.name}\n"
        f"- Company: {company_md.name}\n\n"
        f"---\n\n"
    )

    if not text:
        # Fallback for empty result
        log_path = outdir / f"{args.ticker}_final_runlog_{ts}.txt"
        log_path.write_text(stdout_text, encoding="utf-8")
        text = (
            "_(no result)_\n\n"
            "> Possible causes: tools disabled / content printed only to stdout / failed to parse chat buffers.\n"
            f"> Full runtime logs saved to: {log_path.name}\n"
        )

    out_md = outdir / f"{args.ticker}_FINAL_decision_{ts}.md"
    out_md.write_text(header + text + "\n", encoding="utf-8")
    print(f"[ok] Final decision report saved: {out_md}")

    # Console preview
    print("\n===== PREVIEW (first 50 lines) =====")
    for line in (header + text).splitlines()[:50]:
        print(line)
    print("===== END PREVIEW =====")

if __name__ == "__main__":
    main()
