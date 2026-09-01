from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
import pytest, os


def test_login_page_visual(page: Page, assert_snapshot, browser_name):
    device = os.getenv("DEVICE")
    is_mobile_run = browser_name == "webkit" and device

    if browser_name != "chromium" and not is_mobile_run:
        pytest.skip(f"Visual testing is not supported on {browser_name}")

    login_page = LoginPage(page)
    login_page.goto()

    snapshot_name = f"login-page--{device}.png" if device else "login-page.png"
    assert_snapshot(page, name=snapshot_name)
