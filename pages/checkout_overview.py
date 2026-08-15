from playwright.sync_api import Page


class CheckoutOverview:
    def __init__(self, page: Page):
        self.page = page
        self.checkout_ov_cartlist = page.locator('[data-test="cart-list"]')
        self.checkout_ov_finish_btn = page.locator('[data-test="finish"]')
