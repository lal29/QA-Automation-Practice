from playwright.sync_api import Page


class CheckoutInfoPage:
    def __init__(self, page: Page):
        self.page = page
        self.checkout_info_container = page.locator(
            '[data-test="checkout-info-container"]'
        )
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.error_message = page.locator('[data-test="error"]')
        self.continue_button = page.locator('[data-test="continue"]')
