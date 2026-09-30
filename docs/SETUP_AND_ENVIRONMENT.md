# ENVIRONMENT SETUP & LOCAL QUICKSTART GUIDE
## Zero-Friction Setup for Linux, macOS, and Windows

**Audience:** Ken, Chester, and Integrator  
**Prerequisites:** Python 3.12+ and Git installed on your system.

---

## 1. Fast Setup (3 Commands)

Open your terminal in the project root directory and execute the commands for your operating system:

### Linux / macOS
```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip and install all project dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Verify installation
python -c "import PySide6, pytest, ruff; print(' Environment configured successfully!')"
```

### Windows (PowerShell)
```powershell
# 1. Allow script execution in current session (if restricted)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python -c "import PySide6, pytest, ruff; print(' Environment configured successfully!')"
```

### Windows (Command Prompt - cmd.exe)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
python -c "import PySide6, pytest, ruff; print(' Environment configured successfully!')"
```

---

## 2. Common Setup Gotchas & Instant Fixes

### Gotcha A: Linux GUI Crash (`Could not load Qt platform plugin "xcb"`)
* **Symptom:** When running PySide6, you see: `qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.`
* **Fix (Ubuntu/Debian):** Install the required X11/xcb libraries:
  ```bash
  sudo apt update
  sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 libxcb-xinerama0
  ```
* **Alternative (force X11 platform):**
  ```bash
  export QT_QPA_PLATFORM=xcb
  ```

### Gotcha B: Windows PowerShell Script Execution Blocked
* **Symptom:** `.\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Fix:** Run this one-liner in PowerShell before activating:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

### Gotcha C: macOS Architecture Mismatch (arm64 vs x86_64)
* **Symptom:** PySide6 fails to import or crashes with dynamic loader errors on Apple Silicon (M1/M2/M3).
* **Fix:** Ensure you are using native arm64 Python from `python.org` or Homebrew (`brew install python@3.12`), not an Intel x86_64 version running through Rosetta.

---

## 3. How to Run Tests & Linters

### Run Automated Unit & Integration Tests
```bash
# Run all tests in the repository
pytest -v

# Run only backend automata tests (Ken)
pytest tests/core tests/services -v

# Run only frontend interaction tests (Chester)
pytest tests/gui -v

# Run end-to-end integration tests (Integrator)
pytest tests/integration -v
```

### Run Code Linter & Formatter (Ruff)
```bash
# Check code for style, type, or syntax errors
ruff check .

# Automatically fix simple formatting issues
ruff check --fix .
```

---

## 4. How to Run the Application

```bash
python -m app.main            # from the project root (any working directory works)
python -m pytest              # unit + GUI (offscreen) tests
python scripts/gen_docs.py --check   # docs tables up to date?
```
