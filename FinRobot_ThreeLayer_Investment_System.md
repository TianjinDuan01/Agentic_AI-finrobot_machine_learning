# FinRobot Three-Layer Investment Decision System

This folder contains three collaborating Agents designed to generate
stock investment recommendations by combining macroeconomic and
micro-level analyses.

## Architecture Design

    Macroeconomic Analysis Agent (make_macro_report.py)
        ↓ Output: Macroeconomic Environment Report

    Company Analysis Agent (make_company_report.py)
        ↓ Output: Company Fundamental Report

    Final Decision Agent (final_decision_agent.py)
        ↓ Input: Macro Report + Company Report
        ↓ Output: Specific Stock Investment Recommendation (Bullish/Neutral/Bearish)

## Description of the Three Agents

### 1. Macroeconomic Analysis Agent (`make_macro_report.py`)

**FinRobot Agent Used**: `Market_Analyst`

**Function**: Analyzes the macroeconomic environment - Reads FOMC
meeting transcripts (full 26 pages, no RAG required) - Retrieves recent
macro news (inflation, employment, GDP, interest rate expectations,
etc.) - Outputs a structured macroeconomic report

**Output Includes**: - Monetary policy stance (rate path, balance sheet
reduction, etc.) - Inflation outlook (CPI/PCE trends) - Labor market
(unemployment, wage growth) - Economic growth (GDP, consumption,
investment) - Market impact (effects on equities and sectors) - Risks
and catalysts

------------------------------------------------------------------------

### 2. Company Analysis Agent (`make_company_report.py`)

**FinRobot Agent Used**: `Market_Analyst`

**Function**: Analyzes company fundamentals - Fetches financial data for
the target stock - Collects recent company news (default: 7 days) -
Analyzes profitability, valuation, and industry position

**Output Includes**: - Key positive factors (2--4 items) - Risk factors
(2--4 items) - Next week's price movement prediction (\~2--3%) -
Catalysts and confidence level

------------------------------------------------------------------------

### 3. Final Decision Agent (`final_decision_agent.py`)

**FinRobot Agent Used**: `Expert_Investor`

**Function**: Integrates macro and company analyses to deliver
investment recommendations - Reads macro and company reports - Combines
top-down (macro) and bottom-up (company) perspectives - Provides clear
investment advice

**Output Includes**: - Macro background summary (3--5 items) -
Company-specific analysis (3--5 strengths, 3--5 risks) - Short-term
outlook (1 week) + probability - Mid-term outlook (1--3 months) +
probability - **Final Recommendation: Bullish / Neutral / Bearish** -
Entry/exit points, stop-loss/take-profit suggestions

------------------------------------------------------------------------

## Usage

### Option 1: Streamlit Web Interface (Recommended) ✨

### Check `FinRobot_Streamlit_Web_Interface_Guide.md`

------------------------------------------------------------------------

### Option 2: Command-Line Usage

#### Prerequisites

1.  **Install dependencies**:

``` bash
pip install -r requirements_finrobot.txt
```

2.  **Configure API Keys**:
    -   Copy `OAI_CONFIG_LIST.json` to the project root and fill in your
        OpenAI API key.
    -   Copy `config_api_keys.json` and fill in data source keys
        (Finnhub/FMP/sec).

------------------------------------------------------------------------

### Step 1: Generate Macroeconomic Report

``` bash
python make_macro_report.py     --fomc-pdf ./FOMC_presconf/FOMCpresconf20250917.pdf     --oai-config ./OAI_CONFIG_LIST.json     --keys-config ./config_api_keys.json     --model gpt-4-0125-preview     --outdir ./reports     --news-days 14
```

**Output**: `reports/MACRO_report_YYYYMMDD_HHMMSS.md`

------------------------------------------------------------------------

### Step 2: Generate Company Analysis Report

``` bash
python make_company_report.py     --ticker NVDA     --oai-config ./OAI_CONFIG_LIST.json     --keys-config ./config_api_keys.json     --model gpt-4-0125-preview     --outdir ./reports     --news-days 7
```

**Output**: `reports/NVDA_company_report_YYYYMMDD_HHMMSS.md`

------------------------------------------------------------------------

### Step 3: Generate Final Investment Decision

``` bash
python final_decision_agent.py     --macro-report ./reports/MACRO_report_20250929_120000.md     --company-report ./reports/NVDA_company_report_20250929_120500.md     --ticker NVDA     --oai-config ./OAI_CONFIG_LIST.json     --model gpt-4-0125-preview     --outdir ./reports
```

**Output**: `reports/NVDA_FINAL_decision_YYYYMMDD_HHMMSS.md`

------------------------------------------------------------------------

## Example: Full Workflow Script

Create a `run_full_analysis.sh` script:

``` bash
#!/bin/bash
# Full three-layer analysis process

TICKER="NVDA"
FOMC_PDF="./FOMCpresconf20250917.pdf"
OUTDIR="./reports"

echo "=== Step 1: Generating Macro Report ==="
python make_macro_report.py     --fomc-pdf "$FOMC_PDF"     --outdir "$OUTDIR"     --news-days 14

MACRO_REPORT=$(ls -t "$OUTDIR"/MACRO_report_*.md | head -1)
echo "Macro report: $MACRO_REPORT"

echo ""
echo "=== Step 2: Generating Company Report for $TICKER ==="
python make_company_report.py     --ticker "$TICKER"     --outdir "$OUTDIR"     --news-days 7

COMPANY_REPORT=$(ls -t "$OUTDIR"/"${TICKER}"_company_report_*.md | head -1)
echo "Company report: $COMPANY_REPORT"

echo ""
echo "=== Step 3: Generating Final Investment Decision ==="
python final_decision_agent.py     --macro-report "$MACRO_REPORT"     --company-report "$COMPANY_REPORT"     --ticker "$TICKER"     --outdir "$OUTDIR"

FINAL_REPORT=$(ls -t "$OUTDIR"/"${TICKER}"_FINAL_decision_*.md | head -1)
echo ""
echo "=== DONE ==="
echo "Final report: $FINAL_REPORT"
```

Run:

``` bash
chmod +x run_full_analysis.sh
./run_full_analysis.sh
```

------------------------------------------------------------------------

*(Further sections continue with translated technical details, examples,
and troubleshooting similar to the source.)*
