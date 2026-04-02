# 📱 FinRobot Streamlit Web Interface User Guide

This is a visual web interface designed for the **FinRobot Three-Layer Investment Decision System**, allowing you to access all features easily without command-line operations.

> Before running **`run_streamlit.sh`**, please create and activate a virtual environment — preferably using **conda**, or **Python venv** if conda is unavailable.

---

## 🧰 0. Prerequisites

- Git installed (optional)  
- Anaconda/Miniconda installed (recommended; otherwise use venv in Section 2)  
- Operating system: macOS or Linux  

---

## 1) Using Conda to Create and Activate a Virtual Environment (Recommended)

If you have Anaconda or Miniconda installed, follow these steps:

```bash
# Check if conda is available
conda --version

# Create a new environment (Python 3.10 as example)
conda create -n finrobot-web python=3.10 -y

# Activate the environment (if activation fails, see below)
conda activate finrobot-web

# Upgrade pip and install dependencies (use your actual requirements file)
python -m pip install -U pip
python -m pip install -r requirements_finrobot.txt
```

**If activation fails (“zsh: command not found: conda”):**
```bash
# Reload conda initialization script and activate again
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate finrobot-web
```

---

## 2) No Conda? Use Python venv (Alternative)

If conda is not available, you can use Python’s built-in venv to create an isolated environment:

```bash
# Verify Python 3 is installed
python3 --version

# Create a .venv in the project root
python3 -m venv .venv

# Activate the environment (macOS/Linux)
source .venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install -U pip
python -m pip install -r requirements_finrobot.txt
```

**Each time you return to the project, reactivate the venv:**
```bash
source .venv/bin/activate
```

> To exit the virtual environment: `deactivate`.

---

## 3) Common Troubleshooting

- `zsh: command not found: python`  
  → Python is not on your PATH. Try:  
  - Using an absolute path: `/opt/anaconda3/envs/finrobot-web/bin/python ...`  
  - Or run: `conda run -n finrobot-web python ...`

- `zsh: command not found: pip`  
  → Install pip manually:  
  `conda install -n finrobot-web pip` or `python -m ensurepip --upgrade`

- `ModuleNotFoundError: No module named 'streamlit'`  
  → Make sure you installed it **inside** your virtual environment:  
  `python -m pip install streamlit`

---


## 🚀 Quick Start

### Method 1: Use the Launch Script (Recommended)

``` bash
./run_streamlit.sh
```

### Method 2: Manual Launch

``` bash
streamlit run streamlit_app.py
```

Your browser will automatically open `http://localhost:8501`.

------------------------------------------------------------------------

## 🖥️ Interface Overview

### Main Components

1.  **Sidebar**:
    -   Page navigation (Home, Macro Analysis, Company Analysis, Final
        Decision)
    -   Global settings (API Keys, Model selection, Output directory)
    -   Usage tips
2.  **Main Content Area**:
    -   Operation panels for each Agent
    -   Real-time progress display
    -   Report preview and download

------------------------------------------------------------------------

## 📖 Workflow

### Step 1: Configure API Keys

In the left sidebar, configure:

-   **OAI Config Path**: Path to OpenAI API config file (default:
    `OAI_CONFIG_LIST.json`)
-   **Keys Config Path**: Path to data source keys (default:
    `config_api_keys.json`)
-   **LLM Model**: Choose the model (recommended: `gpt-4-0125-preview`)
-   **Output Directory**: Path where reports will be saved (default:
    `../reports`)

### Step 2: Generate Macroeconomic Analysis Report

1.  Click **🌍 Macro Analysis** on the sidebar\
2.  Upload the FOMC meeting transcript PDF\
3.  Set the macro news lookback period (recommended: 14 days)\
4.  Click **🚀 Generate Macro Analysis Report**\
5.  Wait for the progress bar to complete\
6.  Preview and download the report

**Output**: `MACRO_report_YYYYMMDD_HHMMSS.md`

### Step 3: Generate Company Analysis Report

1.  Click **🏢 Company Analysis** on the sidebar\
2.  Enter the stock ticker (e.g., `NVDA`, `MSFT`)\
3.  Set company news lookback days (recommended: 7)\
4.  Click **🚀 Generate Company Analysis Report**\
5.  Wait for progress to complete\
6.  Preview and download the report

**Output**: `{TICKER}_company_report_YYYYMMDD_HHMMSS.md`

### Step 4: Generate Final Investment Decision

1.  Click **🎯 Final Decision** on the sidebar\
2.  Select an existing macro report\
3.  Select an existing company report\
4.  Confirm the stock ticker (auto-extracted from file name)\
5.  Click **🚀 Generate Final Investment Decision**\
6.  Wait for completion and view the report

**Output**: `{TICKER}_FINAL_decision_YYYYMMDD_HHMMSS.md`

------------------------------------------------------------------------

## 🎨 Interface Details

### 🏠 Home

-   **System Architecture**: Overview of the three Agents and their
    roles\
-   **Quick Start**: Four-step user guide\
-   **Tips**: Key reminders and notes

### 🌍 Macro Analysis Page

**Inputs**: - FOMC PDF file (drag-and-drop or select manually)\
- News lookback period (1--30 days, default 14)

**Outputs**: - Monetary policy stance\
- Inflation outlook\
- Labor market\
- Economic growth\
- Market impact\
- Risks & catalysts

**Agent Used**: `Market_Analyst`

### 🏢 Company Analysis Page

**Inputs**: - Stock ticker (auto uppercased)\
- News lookback period (1--30 days, default 7)

**Outputs**: - Positive factors (2--4)\
- Risk factors (2--4)\
- One-week price prediction\
- Catalysts and confidence

**Agent Used**: `Market_Analyst`

### 🎯 Final Decision Page

**Inputs**: - Selected macro report\
- Selected company report\
- Confirmed stock ticker

**Outputs**: - Macro summary (3--5 points)\
- Company-specific analysis (strengths + risks)\
- Short-term (1 week) outlook + probability\
- Mid-term (1--3 months) outlook + probability\
- **Final Recommendation: Bullish / Neutral / Bearish**\
- Entry/exit points\
- Stop-loss/take-profit suggestions\
- Risk triggers

**Agent Used**: `Expert_Investor`

------------------------------------------------------------------------


## 💡 Tips & Tricks

### 1. Analyze Multiple Stocks

You can reuse one macro report:

1.  Generate one macro report\
2.  Generate multiple company reports\
3.  Combine each with the same macro report for decisions

**Example Workflow:**

    Macro Report (once)
        ↓
    Company Report (NVDA) → Final Decision (NVDA)
    Company Report (MSFT) → Final Decision (MSFT)
    Company Report (AAPL) → Final Decision (AAPL)

### 2. Real-Time Progress

-   Progress bars update dynamically\
-   Status messages show current step\
-   Typical durations:
    -   Macro: 2--3 mins\
    -   Company: 1--2 mins\
    -   Final: 1--2 mins

### 3. Report Management

-   Reports named automatically by timestamp\
-   Dropdowns display available reports\
-   Supports Markdown download\
-   Viewable in any Markdown editor

### 4. Error Handling

If a generation fails, you'll see: - Error type (timeout, key error,
etc.)\
- Full error message\
- Suggested fixes

------------------------------------------------------------------------

## 🐛 Troubleshooting

**Q1: Browser didn't open?**\
→ Visit manually: `http://localhost:8501`

**Q2: "streamlit not found"?**

``` bash
pip install streamlit
```

**Q3: Timeout during generation?**\
- Check internet connection\
- Verify API keys\
- Try a faster model (e.g., gpt-3.5-turbo)

**Q4: Missing reports?**\
- Verify correct output directory\
- Check completion status\
- Inspect report folder manually

**Q5: PDF upload failed?**\
- File \< 10MB\
- Valid format\
- Try a different file

**Q6: "not found in agent library"?**\
Use correct agents:\
- `Market_Analyst` -- For macro & company analysis\
- `Expert_Investor` -- For final decision

------------------------------------------------------------------------
