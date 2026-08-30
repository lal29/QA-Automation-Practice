from playwright.sync_api import Page, expect
from pages.login_page import LoginPage


def test_login_page_visual(page: Page, assert_snapshot):
    login_page = LoginPage(page)
    login_page.goto()
    assert_snapshot(page)
