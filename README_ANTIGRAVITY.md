# Google Antigravity Setup Guide for Another Device
> **Project:** Agro-Vision AI (Multimodal Crop Intelligence & Yield Optimization)  
> **Target Environment:** Setting up and pairing Google Antigravity (IDE / CLI / 2.0) on a secondary PC or workstation (Windows, macOS, Linux).

---

## 1. Overview

This guide explains how to migrate, clone, and configure this project on another machine so that **Google Antigravity** can seamlessly understand the architecture, enforce workspace rules, leverage project workflows, and execute code and ML pipelines.

---

## 2. Prerequisites on the New Device

Before launching Antigravity, ensure the following tools are installed on the target machine:

### A. Core Development Tools
1. **Git**: [git-scm.com](https://git-scm.com/)
2. **Python**: Python 3.11 or 3.12 (ensure `python` and `pip` are added to system `PATH`).
3. **Google Antigravity**:
   - Download and install **Antigravity IDE** or **Antigravity 2.0** desktop app from [antigravity.google](https://antigravity.google).
   - Sign in with your authorized Google Account.

---

## 3. Cloning & Environment Setup

Follow these steps in your terminal on the new device:

### Step 1: Clone or Copy the Repository
```bash
git clone <YOUR_REPOSITORY_URL> agrovision
cd agrovision
```

### Step 2: Set Up Python Virtual Environment

- **On Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **On Linux / macOS (Bash/Zsh):**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Pinned Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template configuration to create your local `.env`:
- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / macOS:**
  ```bash
  cp .env.example .env
  ```

Ensure values inside `.env` match your local device needs (e.g., `DATABASE_URL=sqlite:///agrovision.db`).

---

## 4. Antigravity Workspace Configuration

Antigravity uses both workspace-level and global customizations.

### A. Workspace-Level Customizations (Already Included in Repo)
The repository includes project-specific rules and workflows that Antigravity automatically detects:
- [`.agent/rules/agrovision.md`](file:///c:/Users/Admin/Desktop/major project/project/.agent/rules/agrovision.md): Non-negotiable ML hygiene, API validation, and security rules.
- [`.agents/rules/`](file:///c:/Users/Admin/Desktop/major project/project/.agents/rules/): Additional workspace rules.
- [`.agent/workflows/`](file:///c:/Users/Admin/Desktop/major project/project/.agent/workflows/): Automated playbooks for training (`train-disease.md`, `train-price.md`, `train-tabular.md`) and testing (`run-tests.md`, `smoke-test.md`).

When you open the folder in Antigravity IDE, these instructions are automatically active.

### B. Global Customizations (Optional / User-Level)
If your primary device had custom plugins, global skills, or MCP configurations under `~/.gemini/config`:
- **Windows:** `C:\Users\<Username>\.gemini\config\`
- **Linux/macOS:** `~/.gemini/config/`

You can mirror any custom global plugins or Model Context Protocol (MCP) server definitions (`mcp_config.json`) to that folder on the new machine.

---

## 5. Opening & Configuring in Antigravity IDE

1. **Open Workspace**: Launch Antigravity IDE and select **File > Open Folder...**, then select the project root directory.
2. **Select Python Interpreter**:
   - Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> (or <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> on macOS).
   - Type `Python: Select Interpreter`.
   - Pick the `.venv` created in Step 2 (`./.venv/Scripts/python.exe` on Windows or `./.venv/bin/python` on Linux/macOS).
3. **Verify Agent Mode**:
   - Open the **Antigravity Chat / Agent** side panel.
   - Ask: `"Verify project setup and list loaded rules"`. Antigravity will confirm that [`.agent/rules/agrovision.md`](file:///c:/Users/Admin/Desktop/major project/project/.agent/rules/agrovision.md) is active.

---

## 6. Verifying the Setup

Run test commands in the Antigravity integrated terminal or prompt the agent to run them:

### A. Run Test Suite
```bash
pytest -v tests/
```
All unit and integration tests should pass.

### B. Run the Local Flask Server
```bash
flask run --host=0.0.0.0 --port=5000
```
Visit `http://localhost:5000` in your browser to verify that the Agro-Vision AI interface loads correctly.

---

## 7. Working with Antigravity on the New Device

- **Sidebar Agent Mode**: Use for implementing features, running multi-step tasks, and debugging.
- **Slash Commands**:
  - `/plan`: Create structured implementation plans before starting major changes.
  - `/goal`: Launch thorough, long-running agent execution.
- **Inline Edits (<kbd>Ctrl</kbd>+<kbd>I</kbd> / <kbd>Cmd</kbd>+<kbd>I</kbd>)**: Highlight any code block to refactor, write docstrings, or modify logic.
- **Tab Suggestions**: Context-aware completions and multi-line suggestions.

---

## 8. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError` | Virtual environment not activated or packages missing | Run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix), then `pip install -r requirements.txt`. |
| TensorFlow / Keras warning | CPU vs GPU instruction set differences on new machine | The project runs fine on CPU by default. Verify version is pinned (`tensorflow==2.17.0`). |
| Database errors on startup | SQLite database file locked or permissions missing | Ensure read/write permissions in the root directory for [agrovision.db](file:///c:/Users/Admin/Desktop/major project/project/agrovision.db). |
| Path separators in scripts | Hardcoded `\` or `/` across OS platforms | The codebase uses `os.path` and `pathlib` for cross-platform compatibility. Always use POSIX or `pathlib.Path`. |
