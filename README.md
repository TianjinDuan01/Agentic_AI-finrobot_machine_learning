# 💼 FinRobot: Three-Layer Investment Decision System

**FinRobot** is an AI-driven investment research and decision-making framework combining **macroeconomic**, **company**, and **investment strategy** layers.  
It integrates modular backend agents with a modern Streamlit-based frontend, providing a complete workflow from raw data to final investment recommendations.

---

## 🧭 Project Overview

The system consists of three main components:

| Component | Purpose | Guide |
|------------|----------|-------|
| 🧩 **Backend: Three-Layer Agent System** | Core logic that performs macroeconomic, company, and final decision analysis using intelligent agents | [FinRobot_ThreeLayer_Investment_System.md](./FinRobot_ThreeLayer_Investment_System.md) |
| 🌐 **Frontend: Streamlit Web Interface** | Visual interface for running the FinRobot pipeline interactively | [FinRobot_Streamlit_Web_Interface_Guide.md](./FinRobot_Streamlit_Web_Interface_Guide.md) |
| 🔑 **API Key Setup Guide** | Step-by-step instructions for getting and configuring all required API keys (OpenAI, Finnhub, FMP, SEC) | [FinRobot_API_Keys_Setup_Guide.md](./FinRobot_API_Keys_Setup_Guide.md) |

---

## 🧩 Recommended Setup Order

To get FinRobot fully working, follow this order:

### 1️⃣ Set Up API Keys
- Follow the [API Setup Guide](./FinRobot_API_Keys_Setup_Guide.md).
- Obtain your API keys.
- Save them into `OAI_CONFIG_LIST.json` and `config_api_keys.json`.
- Verify they are detected using the commands in the guide.

### 2️⃣ Understand the Backend
- Read [FinRobot_ThreeLayer_Investment_System.md](./FinRobot_ThreeLayer_Investment_System.md).
- Learn how the **three intelligent agents** work:
  1. **Macroeconomic Analysis Agent** — builds FOMC-based macro reports.  
  2. **Company Analysis Agent** — extracts fundamentals and market data.  
  3. **Final Decision Agent** — merges both for actionable recommendations.


### 3️⃣ Launch the Frontend Streamlit Interface
- Refer to [FinRobot_Streamlit_Web_Interface_Guide.md](./FinRobot_Streamlit_Web_Interface_Guide.md).
- Create a virtual environment (conda or venv).
- Install dependencies using:
- Then launch:
  ```bash
  ./run_streamlit.sh
  ```
- Access the dashboard at: [http://localhost:8501](http://localhost:8501)

---

