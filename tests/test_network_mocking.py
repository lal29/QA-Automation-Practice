import pytest
from playwright.sync_api import Page, Error


def test_broken_product_image(logged_in_page: Page):
    page = logged_in_page
    page.route("**/sauce-backpack*.jpg", lambda route: route.abort())
    page.reload()

    img = page.locator('[data-test="inventory-item-sauce-labs-backpack-img"]')
    width = img.evaluate("el => el.naturalWidth")
    assert width == 0


def test_offline_reload_fails(logged_in_page: Page):
    page = logged_in_page
    page.context.set_offline(True)

    with pytest.raises(Error):
        page.reload()
