import pytest, os
from pages.login_page import LoginPage
from pathlib import Path
from pages.inventory_page import InventoryPage
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def storage_state_path(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(os.getenv("STANDARD_USER"), os.getenv("STANDARD_PASSWORD"))
    STORAGE_STATE_PATH = str(Path(__file__).parent / "storage_state.json")
    context.storage_state(path=STORAGE_STATE_PATH)
    context.close()
    return STORAGE_STATE_PATH


@pytest.fixture
def logged_in_page(browser, storage_state_path, browser_context_args):
    context = browser.new_context(
        storage_state=storage_state_path, **browser_context_args
    )
    page = context.new_page()
    InventoryPage(page).goto()
    yield page
    context.close()


@pytest.fixture
def api_request_context(playwright):
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    device_name = os.getenv("DEVICE")
    if device_name:
        return {**browser_context_args, **playwright.devices[device_name]}
    return browser_context_args
