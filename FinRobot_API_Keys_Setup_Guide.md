# 🔑 FinRobot API Keys Setup Guide

This guide explains step-by-step how to **obtain and configure all required API keys** for the FinRobot Investment Decision System.  
It’s written for users **with no prior experience** using APIs.

---

## 📋 Overview

You’ll need credentials from four data providers:

| Platform | Purpose | URL |
|-----------|----------|-----|
| **OpenAI** | LLM model access (e.g., GPT-4) | [https://platform.openai.com](https://platform.openai.com) |
| **Finnhub** | Stock & market data | [https://finnhub.io](https://finnhub.io) |
| **Financial Modeling Prep (FMP)** | Company fundamentals & ratios | [https://financialmodelingprep.com](https://financialmodelingprep.com) |
| **SEC** | Public company filings | [https://sec-api.io](https://sec-api.io) |

---

## 🧠 Step 1. Get an OpenAI API Key

**Website:** [https://platform.openai.com](https://platform.openai.com)

1. Visit the site and sign up (or log in).  
2. Navigate to [**API Keys**](https://platform.openai.com/account/api-keys).  
3. Click **“+ Create new secret key.”**  
4. Copy the generated key (it begins with `sk-`).  
5. Copy your key and add it to `OAI_CONFIG_LIST.json`.

**Example File:**
```json
[
  {
    "model": "gpt-4-0125-preview",
    "api_key": "sk-REPLACE_WITH_YOUR_KEY"
  }
]
```


> 💡 Keep your key private. Never upload this file to GitHub or share it publicly.

---

## 📊 Step 2. Get a Finnhub API Key

**Website:** [https://finnhub.io](https://finnhub.io)

1. Go to the Finnhub homepage.  
2. Click **“Get free API key”** in the top right corner.  
3. Sign up with your email, Google, or GitHub account.  
4. After logging in, your API key appears on the dashboard.  
5. Copy it and paste it into your configuration file.

**Add to `config_api_keys.json`:**
```json
{
  "finnhub_api_key": "FINNHUB_REPLACE_ME"
}
```



---

## 💰 Step 3. Get a Financial Modeling Prep (FMP) API Key

**Website:** [https://financialmodelingprep.com](https://financialmodelingprep.com)

1. Go to the website and click **“Get your API key.”**  
2. Sign up for a free developer account: [FMP Docs → Get API Key](https://financialmodelingprep.com/developer/docs).  
3. Verify your email and log in.  
4. Open **Dashboard → API Key**.  
5. Copy the key and paste it into `config_api_keys.json`.

**Example:**
```json
{
  "fmp_api_key": "FMP_REPLACE_ME"
}
```



---

## 🧾 Step 4. Configure SEC Filings Access

### Using sec-api.io 
**Website:** [https://sec-api.io](https://sec-api.io)

1. Go to sec-api.io and click **“Get Free API Key.”**  
2. Sign up and verify your email.  
3. Copy your key and add it to `config_api_keys.json`:

```json
{
  "sec_api_key": "SECAPI_REPLACE_ME"
}
```

---

## 🗂 Step 5. Combine All Keys into One File

You can merge everything into one file, `config_api_keys.json`:

```json
{
  "finnhub_api_key": "FINNHUB_REPLACE_ME",
  "fmp_api_key": "FMP_REPLACE_ME",
  "sec_user_agent": "Your Name (your.email@example.com)"
}
```

Keep both:
- `OAI_CONFIG_LIST.json` (for OpenAI)
- `config_api_keys.json` (for market data)

in your project root.

---
