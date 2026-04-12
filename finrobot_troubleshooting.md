# FinRobot Troubleshooting Summary (Continued)

You may find the key issues encountered during setup and execution, along with their targeted solutions, documented here. This section provides a concise reference for diagnosing common problems related to environment configuration, API usage, and report generation within the FinRobot system.

---

## 1. Broken Python Interpreter in VS Code

### i) Symptom
VS Code showed errors like:
```
Error spawning python .../bin/python ENOENT
```

### ii) Cause
VS Code was still pointing to a deleted or broken virtual environment. `ENOENT` means the file path did not exist.

### iii) Fix
Delete the broken environment folder:
```bash
rm -rf <your_virtual_env_folder>
```

In VS Code, choose the correct interpreter:
- `Cmd + Shift + P`
- **Python: Select Interpreter**
- Choose a working environment (e.g., a conda or venv environment such as `finrobot-web`)

Reload VS Code:
- `Cmd + Shift + P`
- **Developer: Reload Window**

Check `.vscode/settings.json` and remove any old interpreter path like:
```json
"python.defaultInterpreterPath": "<invalid_path>/bin/python"
```

### iv) Notes
This issue commonly occurs after deleting or renaming a virtual environment. VS Code may cache old interpreter paths and continue to reference them until manually updated.

---

## 2. Failed Attempt to Recreate `.financerobot`

### i) Symptom
Running:
```bash
python3 -m venv .financerobot
```
gave an error.

### ii) Cause
The local venv path or interpreter setup was not healthy, and you were already using a working conda environment.

### iii) Fix
Do not recreate that broken venv. Use the existing conda environment instead:
```bash
conda activate finrobot-web
```
Then make sure VS Code also uses that same environment.

---

## 3. OpenAI Calls Did Not Work Until Billing Was Added

### i) Symptom
The app did not generate reports at first, then started working after adding $5 to OpenAI.

### ii) Cause
This was a separate issue from Python. The OpenAI API account needed usable credit / billing.

### iii) Fix
1. Add billing/credit to the OpenAI account.
2. Retry the report generation.

### iv) Result
After that, report generation succeeded.

---

## 4. No Module Named `autogen`

### i) Symptom
Some students got:
```
No module named autogen
```

### ii) Cause
Usually one of these:
1. `pyautogen` was not installed
2. It was installed in the wrong Python environment
3. VS Code was using a different interpreter

### iii) Fix
1. Activate the correct environment:
   ```bash
   conda activate finrobot-web
   ```
2. Check Python path:
   ```bash
   which python
   python --version
   ```
3. Install the package in that environment:
   ```bash
   pip install pyautogen
   ```
4. Verify:
   ```bash
   python -c "import autogen; print(autogen.__version__)"
   ```

---

## 5. Most Common Root Causes

Most issues come from:
1. Using the wrong environment (`base` instead of `finrobot-web`)
2. `pyautogen` version mismatch or not installed
3. Streamlit using the wrong Python path
4. Project not installed correctly (`finrobot` not found)

### Solutions

#### 1. Activate the Correct Environment
Many students are still in `base`, which will cause issues. Always run:
```bash
conda activate finrobot-web
```
Then verify:
```bash
which python
```
It should look like:
```
.../anaconda3/envs/finrobot-web/bin/python
```

#### 2. Install Dependencies
After activating the environment:
```bash
pip install -r requirements_finrobot.txt
```

#### 3. Install `pyautogen` (IMPORTANT)
Most issues come from this step:
```bash
pip install pyautogen==0.2.35
```

#### 4. Verify Installation
```bash
python -c "import autogen; print(autogen.__version__)"
```
Expected output:
```
0.2.x
```

#### 5. (If Needed) Install Project as a Package
If you see:
```
No module named finrobot
```
Run:
```bash
pip install -e .
```
