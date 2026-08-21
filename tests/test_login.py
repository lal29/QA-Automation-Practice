import pytest, json
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pathlib import Path

RAW_CASES = json.loads(
    (Path(__file__).parent / "data" / "login_cases.json").read_text()
)

LOGIN_CASES = [
    pytest.param(
        *case, marks=pytest.mark.smoke if case[2] is None else pytest.mark.regression
    )
    for case in RAW_CASES
]


@pytest.mark.parametrize("username, password, expected_error", LOGIN_CASES)
def test_login_attempt(page: Page, username, password, expected_error):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(username, password)

    if expected_error:
        expect(login_page.error_message).to_have_text(expected_error)
    else:
        expect(page.locator('[data-test="inventory-container"]')).to_be_visible()
