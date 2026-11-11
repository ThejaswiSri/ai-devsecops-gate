# AI DevSecOps Review Gate

An automated security review gate built with FastAPI, static code analysis tools (`bandit`, `ruff`), and Google Gemini AI. It inspects incoming GitHub Pull Requests, detects potential security vulnerabilities, generates AI-driven code remediation reports, and posts review comments back to GitHub.

## Architecture

- **`app/main.py`**: Webhook listener handling GitHub PR events and background processing pipeline.
- **`app/diff_parser.py`**: Extracts added code snippets and modified lines from Git diff patches.
- **`app/scanner.py`**: Executes static security analysis checks using `bandit` and `ruff`.
- **`app/ai_engine.py`**: Interacts with the Google GenAI SDK to generate vulnerability explanations, code fixes, and PR gate verdicts.
- **`app/github_client.py`**: Posts review summary comments directly to GitHub PR threads.

## Quick Start

### 1. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1