from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.inventory_container = page.locator('[data-test="inventory-container"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-link"]')

    def add_to_cart(self, item_slug: str):
        self.page.locator(f'[data-test="add-to-cart-{item_slug}"]').click()

    def goto(self):
        self.page.goto("https://www.saucedemo.com/inventory.html")
