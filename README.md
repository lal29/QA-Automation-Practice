# QA Automation Practice Project (Playwright + Python)

Following an 8-week study plan (see `Automation study plan` in Claude's plan history) to go from
Python basics to job-ready QA automation skills.

## Week 1: Environment setup

Run these yourself (this is part of the learning — venv/pip is a real QA automation job skill):

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright's browser binaries
playwright install
```

Once that's done, tell Claude and we'll write the first test together.

## Project layout (grows week by week)

```
Automation/
  requirements.txt   # Python dependencies
  .gitignore
  README.md
  tests/              # pytest test files (added Week 2+)
  pages/              # Page Object Model classes (added Week 4+)
  conftest.py         # shared pytest fixtures (added Week 2+)
```
