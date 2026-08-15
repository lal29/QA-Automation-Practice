# QA Automation Practice Project (Playwright + Python)

[![Tests](https://github.com/lal29/Automation/actions/workflows/tests.yml/badge.svg)](https://github.com/lal29/Automation/actions/workflows/tests.yml)

Following a self-directed study plan to go from Python basics to job-ready QA automation skills.

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

## Project layout

```
Automation/
  .github/workflows/tests.yml   # CI: runs the suite on every push/PR
  requirements.txt              # Python dependencies
  pytest.ini                    # pytest config (makes pages/ importable from tests/)
  .gitignore
  README.md
  pages/                        # Page Object Model classes
    login_page.py
    inventory_page.py
    checkout_page.py
    checkout_info_page.py
    checkout_overview.py
    checkout_complete_page.py
  tests/                        # pytest test files
    conftest.py                 # shared fixtures (login, storage state, API context)
    test_login.py
    test_inventory.py
    test_checkout.py
    test_api.py
    test_network_mocking.py
    data/                       # externalized test case data (JSON)
```
