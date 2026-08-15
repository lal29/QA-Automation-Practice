import pytest
from playwright.sync_api import expect
from pages.inventory_page import InventoryPage


@pytest.mark.parametrize("items", [["sauce-labs-backpack"], ["sauce-labs-bike-light"]])
def test_cart_count(logged_in_page, items):
    ##Inventory list
    inventory_page = InventoryPage(logged_in_page)

    expect(inventory_page.inventory_container).to_be_visible()
    for item in items:
        inventory_page.add_to_cart(item)

    expect(inventory_page.cart_badge).to_have_text(str(len(items)))
    inventory_page.cart_badge.click()
