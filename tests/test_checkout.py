import pytest, json
from playwright.sync_api import Page, expect
from pages.checkout_page import CheckoutPage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview import CheckoutOverview
from pages.checkout_complete_page import CheckoutCompletePage
from pages.inventory_page import InventoryPage
from pathlib import Path

CHECKOUT_CASES = json.loads(
    (Path(__file__).parent / "data" / "checkout_cases.json").read_text()
)


@pytest.mark.parametrize(
    "first_name,last_name,postal_code,expected_error", CHECKOUT_CASES
)
def test_checkout(logged_in_page, first_name, last_name, postal_code, expected_error):
    inventory_page = InventoryPage(logged_in_page)
    inventory_page.add_to_cart("sauce-labs-backpack")
    inventory_page.cart_badge.click()

    checkout_page = CheckoutPage(logged_in_page)
    ##Checkout
    expect(checkout_page.cart_list).to_be_visible()
    checkout_page.checkout_button.click()

    ##Checkout Info
    checkout_info = CheckoutInfoPage(logged_in_page)
    expect(checkout_info.checkout_info_container).to_be_visible()
    checkout_info.first_name.fill(first_name)
    checkout_info.last_name.fill(last_name)
    checkout_info.postal_code.fill(postal_code)
    checkout_info.continue_button.click()

    checkout_overview = CheckoutOverview(logged_in_page)
    if expected_error:
        expect(checkout_info.error_message).to_have_text(expected_error)
    else:
        expect(checkout_overview.checkout_ov_cartlist).to_be_visible()
        checkout_overview.checkout_ov_finish_btn.click()
        checkout_complete_page = CheckoutCompletePage(logged_in_page)
        expect(checkout_complete_page.complete_header).to_be_visible()
