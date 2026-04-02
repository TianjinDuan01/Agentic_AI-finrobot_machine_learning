Guidelines of VSCode Installment, API Keys Setup and FinRobot Agent Installation

Please see more details of the guidelines (including screenshots) in the google doc below: 
https://docs.google.com/document/d/1-2_rlkH4eOP3_Na67-kBQHEyCka5fxoihty8r4wOd5Q/edit?usp=sharing

# VSCode Installment

## Guidelines of VSCode Installment:
Feel free to skip these steps if you have already installed the tools.

### Step 1. Install Visual Studio Code (VSCode)
1. Go to the VSCode download page
2. Download the appropriate version for your operating system (Windows, macOS, or Linux)
3. Follow the installation instructions for your platform
4. Launch VSCode after installation

### Step 2. Download ZIP File and Open This Repository
1. Download the Github repository you need by clicking the green "Code" button on the GitHub page and selecting "Download ZIP"
2. Extract the ZIP file to a location on your computer
3. In VSCode, go to File > Open Folder and select the extracted folder

### Step 3. Opening the Terminal in VSCode
1. In VSCode, press Ctrl+` (Windows/Linux) or Cmd+` (macOS) to open the integrated terminal
2. Alternatively, go to View > Terminal > New Terminal from the menu bar

---

# Create own APIs Keys

## Guidelines of Setup own API Key:

### Overview
This guide explains step-by-step how to obtain and configure all required API keys for the FinRobot Investment Decision System. It is designed for users with no prior experience using APIs.

Platform | Purpose | URL
---|---|---
OpenAI | LLM model access (e.g., GPT-4) | https://platform.openai.com
Finnhub | Stock & market data | https://finnhub.io
Financial Modeling Prep (FMP) | Company fundamentals & ratios | https://financialmodelingprep.com
SEC API | Public company filings | https://sec-api.io

### Step 1. Get an OpenAI API Key
1. Visit https://platform.openai.com and sign up or log in.
2. Navigate to API Keys.
3. Click '+ Create new secret key'.
4. Copy the key and store it securely.
5. Add it to OAI_CONFIG_LIST.json.

[
  {
    "model": "gpt-4-0125-preview",
    "api_key": "sk-REPLACE_WITH_YOUR_KEY"
  }
]

### Step 2. Get a Finnhub API Key
1. Go to https://finnhub.io.
2. Click 'Get free API key'.
3. Sign up and log in.
4. Copy your API key from the dashboard.
5. Add it to config_api_keys.json.

{
  "finnhub_api_key": "FINNHUB_REPLACE_ME"
}

### Step 3. Get a Financial Modeling Prep (FMP) API Key
1. Visit https://financialmodelingprep.com.
2. Sign up and verify your email.
3. Copy your API key from the dashboard.
4. Add it to config_api_keys.json.

{
  "fmp_api_key": "FMP_REPLACE_ME"
}

### Step 4. Configure SEC API Access
1. Go to https://sec-api.io.
2. Sign up and verify your email.
3. Copy your API key.
4. Add it to config_api_keys.json.

{
  "sec_api_key": "SECAPI_REPLACE_ME"
}

### Step 5. Combine All Keys into One File
{
  "finnhub_api_key": "FINNHUB_REPLACE_ME",
  "fmp_api_key": "FMP_REPLACE_ME",
  "sec_user_agent": "Your Name (your.email@example.com)"
}

---

# FinRobot Agent Installation Guide

## What you need before you start
- macOS terminal access
- Anaconda or Miniconda already installed (recommended)
- The project folder extracted
- API keys

### Step 1 — Open the project folder
Confirm files:
README.md, requirements_finrobot.txt, run_streamlit.sh, streamlit_app.py, OAI_CONFIG_LIST.json, config_api_keys.json

### Step 2 — Open Terminal
Open project in VSCode → Terminal → New Terminal

### Step 3 — Create and activate the Conda environment
conda --version
conda create -n finrobot-web python=3.10 -y
conda activate finrobot-web

### Step 4 — Install dependencies
python -m pip install -U pip
python -m pip install -r requirements_finrobot.txt

### Step 5 — Add your API keys
OAI_CONFIG_LIST.json → OpenAI key  
config_api_keys.json → Finnhub, FMP, SEC keys

### Step 6 — Start the Streamlit interface
./run_streamlit.sh
or
streamlit run streamlit_app.py

### Step 7 — Open browser
http://localhost:8501

---

## Quick troubleshooting
- Conda path error: source ~/anaconda3/etc/profile.d/conda.sh
- Missing package: reinstall requirements
- Port already in use: stop previous session

---

## Alternative (venv)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_finrobot.txt
