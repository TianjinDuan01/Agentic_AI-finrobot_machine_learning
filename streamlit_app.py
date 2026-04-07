#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Chen Tong
"""
FinRobot Three-Layer Investment Decision System — Streamlit Frontend
Provides a visual interface for three Agents: Macro Analysis, Company Analysis, Final Decision
"""

import streamlit as st
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="FinRobot Investment Decision System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# 📊 FinRobot System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Agent",
    ["🏠 Home", "🌍 Macro Analysis", "🏢 Company Analysis", "🎯 Final Decision"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Global Settings")

# Global settings
config_dir = Path(__file__).parent
oai_config = st.sidebar.text_input(
    "OAI Config Path",
    value=str(config_dir / "OAI_CONFIG_LIST.json")
)
keys_config = st.sidebar.text_input(
    "Keys Config Path",
    value=str(config_dir / "config_api_keys.json")
)
model = st.sidebar.selectbox(
    "LLM Model",
    ["gpt-5", "gpt-5-mini"],
    index=0
)
outdir = st.sidebar.text_input(
    "Output Directory",
    value=str(config_dir / "reports")
)

# Ensure output directory exists
Path(outdir).mkdir(parents=True, exist_ok=True)

# Home
if page == "🏠 Home":
    st.markdown('<div class="main-header">📈 FinRobot Three-Layer Investment Decision System</div>', unsafe_allow_html=True)

    st.markdown("## Welcome to the FinRobot Investment Decision System")
    st.markdown("This is an AI-powered three-layer investment analysis framework that combines macroeconomic analysis and company fundamentals to provide professional investment recommendations.")

    st.markdown("### 🎯 System Architecture")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🌍 Macro Analysis Agent</h3>
            <p><b>Function:</b> Analyze the macroeconomic environment</p>
            <ul>
                <li>Parse FOMC meeting transcript PDF</li>
                <li>Fetch the latest macro news</li>
                <li>Analyze monetary policy, inflation, employment</li>
            </ul>
            <p><b>Uses:</b> Market_Analyst</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🏢 Company Analysis Agent</h3>
            <p><b>Function:</b> Analyze company fundamentals</p>
            <ul>
                <li>Query financial data</li>
                <li>Fetch company news</li>
                <li>Assess opportunities and risks</li>
            </ul>
            <p><b>Uses:</b> Market_Analyst</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 Final Decision Agent</h3>
            <p><b>Function:</b> Produce a synthesized investment view</p>
            <ul>
                <li>Combine macro + company reports</li>
                <li>Top-down + bottom-up</li>
                <li>Provide a clear recommendation</li>
            </ul>
            <p><b>Uses:</b> Expert_Investor</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    ### 🚀 Quick Start

    1. **Configure API Keys**: Set OpenAI API and data-source keys in the left sidebar
    2. **Macro Analysis**: Upload the FOMC PDF and generate the macro report
    3. **Company Analysis**: Enter a stock ticker and generate the company report
    4. **Final Decision**: Select generated reports and get a recommendation (Bullish/Neutral/Bearish)

    ### 📝 Tips

    - All generated reports are saved to the configured output directory
    - Recommended order: Macro → Company → Final Decision
    - One macro report can be reused for multiple tickers
    """)

# Macro Analysis page
elif page == "🌍 Macro Analysis":
    st.markdown('<div class="main-header">🌍 Macro Analysis Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <b>Description:</b> Read the FOMC meeting transcript PDF and, combined with recent macro news, generate a macroeconomic environment report.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        fomc_pdf = st.file_uploader(
            "Upload FOMC Meeting Transcript PDF",
            type=['pdf'],
            help="PDF format is supported. File size < 10MB is recommended."
        )

    with col2:
        news_days = st.number_input(
            "Macro News Lookback (days)",
            min_value=1,
            max_value=30,
            value=14,
            help="Fetch macro news from the last N days"
        )

    if st.button("🚀 Generate Macro Analysis Report", type="primary", use_container_width=True):
        if not fomc_pdf:
            st.error("Please upload an FOMC PDF first!")
        else:
            # Save uploaded PDF
            pdf_path = Path(outdir) / fomc_pdf.name
            with open(pdf_path, "wb") as f:
                f.write(fomc_pdf.getbuffer())

            st.success("✅ PDF uploaded. Generating report...")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Build command
            cmd = [
                sys.executable,
                str(Path(__file__).parent / "make_macro_report.py"),
                "--fomc-pdf", str(pdf_path),
                "--oai-config", oai_config,
                "--keys-config", keys_config,
                "--model", model,
                "--outdir", outdir,
                "--news-days", str(news_days)
            ]

            # Run
            try:
                status_text.text("📥 [1/3] Extracting FOMC PDF...")
                progress_bar.progress(33)

                with st.spinner("Calling LLM to generate report..."):
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                progress_bar.progress(100)

                if result.returncode == 0:
                    st.success("✅ Macro report generated successfully!")

                    # Find latest report
                    reports = sorted(Path(outdir).glob("MACRO_report_*.md"), key=os.path.getmtime, reverse=True)
                    if reports:
                        latest_report = reports[0]
                        st.markdown(f"**Report Path:** `{latest_report}`")

                        # Preview
                        st.markdown("### 📄 Report Preview")
                        with open(latest_report, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')[:50]
                            preview = '\n'.join(lines).replace("$", "\\$")
                            st.markdown(preview)

                        # Download button
                        st.download_button(
                            label="📥 Download Full Report",
                            data=content,
                            file_name=latest_report.name,
                            mime="text/markdown"
                        )
                else:
                    st.error(f"❌ Generation failed!\n\n**Error Output:**\n```\n{result.stderr}\n```")

            except subprocess.TimeoutExpired:
                st.error("❌ Timed out (5 minutes). Please check your configuration or network.")
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

# Company Analysis page
elif page == "🏢 Company Analysis":
    st.markdown('<div class="main-header">🏢 Company Analysis Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <b>Description:</b> Analyze a stock's financials, recent news, and fundamentals to generate a company report.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        ticker = st.text_input(
            "Stock Ticker",
            placeholder="e.g., NVDA, MSFT, AAPL",
            help="Enter a U.S. stock ticker"
        ).upper()

    with col2:
        company_news_days = st.number_input(
            "Company News Lookback (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="Fetch company news from the last N days"
        )

    if st.button("🚀 Generate Company Analysis Report", type="primary", use_container_width=True):
        if not ticker:
            st.error("Please enter a stock ticker!")
        else:
            st.success(f"✅ Starting analysis for {ticker}...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            cmd = [
                sys.executable,
                str(Path(__file__).parent / "make_company_report.py"),
                "--ticker", ticker,
                "--oai-config", oai_config,
                "--keys-config", keys_config,
                "--model", model,
                "--outdir", outdir,
                "--news-days", str(company_news_days)
            ]

            try:
                status_text.text(f"📊 Fetching financials and news for {ticker}...")
                progress_bar.progress(50)

                with st.spinner("Calling LLM to generate report..."):
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                progress_bar.progress(100)

                if result.returncode == 0:
                    st.success(f"✅ {ticker} company report generated successfully!")

                    reports = sorted(Path(outdir).glob(f"{ticker}_company_report_*.md"), key=os.path.getmtime, reverse=True)
                    if reports:
                        latest_report = reports[0]
                        st.markdown(f"**Report Path:** `{latest_report}`")

                        st.markdown("### 📄 Report Preview")
                        with open(latest_report, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')[:50]
                            preview = '\n'.join(lines).replace("$", "\\$")
                            st.markdown(preview)


                        st.download_button(
                            label="📥 Download Full Report",
                            data=content,
                            file_name=latest_report.name,
                            mime="text/markdown"
                        )
                else:
                    st.error(f"❌ Generation failed!\n\n**Error Output:**\n```\n{result.stderr}\n```")

            except subprocess.TimeoutExpired:
                st.error("❌ Timed out (5 minutes). Please check your configuration or network.")
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

# Final Decision page
elif page == "🎯 Final Decision":
    st.markdown('<div class="main-header">🎯 Final Decision Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <b>Description:</b> Combine the macro and company reports to produce a concrete investment recommendation (Bullish/Neutral/Bearish).
    </div>
    """, unsafe_allow_html=True)

    # List existing reports
    reports_dir = Path(outdir)
    macro_reports = sorted(reports_dir.glob("MACRO_report_*.md"), key=os.path.getmtime, reverse=True)
    company_reports = sorted(reports_dir.glob("*_company_report_*.md"), key=os.path.getmtime, reverse=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Select Macro Report")
        if macro_reports:
            macro_options = [f"{r.name} ({datetime.fromtimestamp(r.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})"
                           for r in macro_reports]
            selected_macro_idx = st.selectbox(
                "Available Macro Reports",
                range(len(macro_options)),
                format_func=lambda i: macro_options[i]
            )
            selected_macro = macro_reports[selected_macro_idx]
        else:
            st.warning("⚠️ No macro reports found. Please generate one first!")
            selected_macro = None

    with col2:
        st.markdown("### Select Company Report")
        if company_reports:
            company_options = [f"{r.name} ({datetime.fromtimestamp(r.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})"
                             for r in company_reports]
            selected_company_idx = st.selectbox(
                "Available Company Reports",
                range(len(company_options)),
                format_func=lambda i: company_options[i]
            )
            selected_company = company_reports[selected_company_idx]

            # Extract ticker from filename
            ticker_match = selected_company.name.split('_')[0]
            ticker = st.text_input("Stock Ticker", value=ticker_match)
        else:
            st.warning("⚠️ No company reports found. Please generate one first!")
            selected_company = None
            ticker = st.text_input("Stock Ticker", placeholder="e.g., NVDA")

    if st.button("🚀 Generate Final Investment Decision", type="primary", use_container_width=True):
        if not selected_macro or not selected_company:
            st.error("Please generate both a macro report and a company report first!")
        elif not ticker:
            st.error("Please enter a stock ticker!")
        else:
            st.success(f"✅ Generating final investment decision for {ticker}...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            cmd = [
                sys.executable,
                str(Path(__file__).parent / "final_decision_agent.py"),
                "--macro-report", str(selected_macro),
                "--company-report", str(selected_company),
                "--ticker", ticker,
                "--oai-config", oai_config,
                "--keys-config", keys_config,
                "--model", model,
                "--outdir", outdir
            ]

            try:
                status_text.text("📖 Reading macro and company reports...")
                progress_bar.progress(30)

                status_text.text("🤔 LLM is synthesizing...")
                progress_bar.progress(60)

                with st.spinner("Generating final investment recommendation..."):
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                progress_bar.progress(100)

                if result.returncode == 0:
                    st.success(f"✅ Final investment decision for {ticker} generated successfully!")

                    reports = sorted(Path(outdir).glob(f"{ticker}_FINAL_decision_*.md"), key=os.path.getmtime, reverse=True)
                    if reports:
                        latest_report = reports[0]
                        st.markdown(f"**Report Path:** `{latest_report}`")

                        st.markdown("### 📄 Final Decision Report")
                        with open(latest_report, 'r', encoding='utf-8') as f:
                            content = f.read()
                            safe_content = content.replace("$", "\\$")
                            st.markdown(safe_content)

                        st.download_button(
                            label="📥 Download Full Report",
                            data=content,
                            file_name=latest_report.name,
                            mime="text/markdown"
                        )
                else:
                    st.error(f"❌ Generation failed!\n\n**Error Output:**\n```\n{result.stderr}\n```")

            except subprocess.TimeoutExpired:
                st.error("❌ Timed out (5 minutes). Please check your configuration or network.")
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📚 Instructions
- Run Macro Analysis first
- Then run Company Analysis
- Finally generate the investment decision

### 💡 Notes
- Reports are automatically saved to the output directory
- You can download them in Markdown format
""")
