from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_list = page.locator('[data-test="cart-list"]')
        self.checkout_button = page.locator('[data-test="checkout"]')
