# QA Automation Notes

Running notes from the study plan — concepts as I actually learn them, in my own project.
Updated as I go, not written all at once.

## Testing fundamentals

- **Manual vs automated testing:** manual = a person clicking through the app checking things by eye (slow, doesn't scale, flexible). Automated = code that drives the app and asserts on the result (fast, repeatable, runs in CI, but only checks what you told it to check).
- **Test pyramid:** lots of fast unit tests at the bottom, fewer integration tests in the middle, small number of slow end-to-end/UI tests at the top. Playwright lives at the top layer (UI), but can also do API testing (lower layer).
- **What makes a "good" automated test:**
  - Independent — doesn't depend on other tests having run first
  - Deterministic — same result every run, no flakiness
  - Asserts one clear thing — so a failure is easy to diagnose

## Python environment

- `python -m venv .venv` creates an isolated environment so project dependencies don't collide with other projects/global Python.
- Activate with `.venv\Scripts\Activate.ps1` (PowerShell). Everything installed after activating goes into `.venv`, not system-wide.
- `requirements.txt` lists dependencies; `pip install -r requirements.txt` installs them all.
- `playwright install` (separate from pip install) downloads the actual browser binaries Playwright drives — not part of the pip package itself.

## Playwright core concepts

- Hierarchy: **browser** (the whole Chromium/Firefox/WebKit process) → **context** (an isolated profile — its own cookies/storage, like an incognito session) → **page** (a single tab).
- **Locators:** how you find an element. `[data-test="..."]` attribute selectors are the gold standard when a site provides them — stable, not tied to CSS classes or visible text that changes on redesign. Prefer them over generic tag/text-based locators (e.g. `page.locator("div").filter(has_text=...)`), which are fragile — brittle to layout changes.
- **Actions:** `.click()`, `.fill()`, `.press()` — self-explanatory, drive the page like a real user.
- **`expect()` vs plain `assert`:**
  - Plain `assert some_locator.text_content() == "foo"` checks the DOM at that *exact instant* — fails if the page hasn't finished rendering yet, even if it would be true half a second later. Classic source of flaky tests.
  - `expect(locator).to_have_text("foo")` **auto-retries** for a few seconds until true or timeout. This is Playwright's core selling point over older tools like Selenium.
  - **Correct shape:** locator goes *inside* `expect()`, the assertion method (`.to_be_visible()`, `.to_have_text(...)`, `.to_have_value(...)`, `.to_have_url(...)`, `.to_have_count(n)`) is chained *after*.
  - **Common mistake I made:** `expect(locator.is_visible)` — passing a bare method reference (no `()`, and not even called) does nothing. It's not a check, not a boolean, and nothing is chained onto the `expect(...)` result either. Silent no-op — no error, no assertion.

## Playwright Codegen

- `playwright codegen <url>` opens a real browser + an Inspector panel that writes Python code live as you click around. Good for a first draft / discovering locators, **not** a finished test.
- Codegen records literally what happened in that one session — including one-time, non-repeatable stuff (e.g. it recorded a randomly-generated download ID from Chrome's downloads page, which broke on the very next run since the ID is different every time).
- Codegen output has zero assertions by default — it performs actions but verifies nothing. A script with no assertions can run against a broken page and still "pass" by simply not crashing.
- Codegen output also uses the raw `sync_playwright()` / manual `browser`/`context`/`.close()` script style — not the pytest style actually used for real tests (see below).

## pytest fundamentals

- Test discovery: files named `test_*.py`, functions named `test_*` inside them. Pytest finds these automatically — no manual registration.
- **`pytest-playwright` gives a `page` fixture for free** — no need to manually call `sync_playwright()`, launch a browser, create a context, or close anything. Just take `page` as a parameter in a test function and pytest hands you a ready-to-use page, cleaned up automatically afterward.
  - **Common mistake I made:** confusing `Page` (the *type*, imported for type hints only — not usable on its own) with `page` (the actual fixture instance). `Page.goto(...)` fails because `Page` is a blueprint, not a real object. Must declare `def test_x(page: Page):` and then use lowercase `page` in the body.
- **Fixtures & `conftest.py`:**
  - A fixture is reusable setup code pytest injects into any test that asks for it by parameter name — avoids repeating the same setup (e.g. login) in every test.
  - `conftest.py` is a special filename pytest auto-discovers with no import needed. Fixtures defined there are available to every test file in that folder (and subfolders).
  - `yield` instead of `return` inside a fixture lets you run teardown code *after* the test — everything after `yield` runs during cleanup, even if the test fails.
  - Default fixture scope is `function` — fresh setup for every single test, avoiding state leaking between tests. `module`/`session` scope shares setup across tests for speed, at the cost of more risk of one test's leftover state affecting another.
  - Built in project: `logged_in_page` fixture in `tests/conftest.py` — navigates to the site and logs in, `yield`s the page. Any test that takes `logged_in_page` as a parameter starts already logged in.

## How pytest actually calls your tests

You never call `test_login_attempt(...)` yourself — `pytest` does, via introspection, not by running your file top to bottom:

1. **Collection:** pytest imports the file as a module (this just defines the function, doesn't call it)
2. **Discovery:** pytest scans the module's namespace for anything named `test_*` — pure naming convention, it doesn't inspect what the function does
3. **Fixture resolution:** for each parameter in the function signature, pytest figures out where the value comes from — `page` resolves to a fixture registered under that name (from `pytest-playwright` or `conftest.py`); parametrize-supplied params come from the decorator's data
4. **Execution:** pytest itself calls the function with the resolved arguments

Same "framework calls your code by naming convention" pattern shows up elsewhere (Flask routes, Django views) — worth recognizing generally, not just for pytest.

## `@pytest.mark.parametrize`

Runs the same test function multiple times with different inputs — one definition, many test cases, each shows up as a separate result so a failure tells you exactly which input broke it.

```python
@pytest.mark.parametrize(
    "username, expected_error",
    [
        ("standard_user", None),
        ("locked_out_user", "Epic sadface: Sorry, this user has been locked out."),
    ],
)
def test_login_attempt(page: Page, username, expected_error):
    ...
```

- First arg: comma-separated string of parameter names. Second arg: list of tuples, one tuple = one test case, values map positionally to those names.
- Those names become real parameters on the function, alongside fixtures like `page`. pytest calls the function once per tuple — `expected_error` isn't computed from anything happening on the page, it's just whatever value came from the current tuple.
- Each case shows up separately in output, e.g. `test_login_attempt[chromium-locked_out_user-...]` — makes failures unambiguous about which input broke.

**`to_have_text()` is an exact match** — my first attempt at the locked-out case failed because the real page text was `"Epic sadface: Sorry, this user has been locked out."` and I'd only expected the part after the colon. `to_contain_text()` exists for substring matches when you don't care about exact wording/prefixes.

**DAMP over DRY in tests:** when the same setup steps (e.g. filling in login fields) are needed in a fixture *and* in a test that's specifically testing variations of that same flow, it's often fine — even preferable — to duplicate a few lines rather than force a shared fixture that doesn't really fit. Tests that read top-to-bottom in isolation are safer to change than tests wired together through shared abstractions. (Page Object Model, later, is the proper long-term fix for locator-heavy duplication — not a fixture.)

## Running tests

- `pytest -v tests/test_checkout.py` — verbose run of one file. Path is relative to wherever the terminal's current directory is (a common gotcha: running `pytest tests/test_checkout.py` while your terminal is already *inside* `tests/` looks for a nonexistent nested `tests/tests/...` path).
- `pytest --headed` — runs with a real visible browser window instead of headless, useful for watching what the test actually does.

## Page Object Model (POM)

- Instead of tests calling `page.locator(...)` directly, wrap each page of the app in a class that owns its locators and exposes methods for actions (`.login(username, password)` instead of three raw fill/click calls). Tests say *what* they want to happen; the page class knows *how*.
- Payoff: if a `data-test` attribute changes, fix it in one place (the page class) instead of hunting through every test file that touched that element.
- **Use the class's public methods, don't reach into its internals.** My first pass at refactoring `conftest.py` called `login_page.username_input.fill(...)` etc. directly instead of `login_page.login(...)` — technically worked, but defeats the purpose: any future change to the login sequence would then need updating in two places again. The whole point of POM is that callers never need to know the sequence exists.

## Cross-folder imports in pytest (`pages/` + `tests/` as siblings)

- `pages/` and `tests/` sit as sibling folders under the project root — Python doesn't automatically know to look in `pages/` when importing from a test file in `tests/`, since pytest doesn't add the project root to the import path by default.
- Fix: a `pytest.ini` at the project root with:
  ```ini
  [pytest]
  pythonpath = .
  ```
  This adds the project root to Python's import path for the whole test session, regardless of which directory `pytest` is run from. No `__init__.py` files or relative-import tricks needed. Then `from pages.login_page import LoginPage` just works from any test file.
- This exact structure (`pages/` + `tests/` + `pythonpath = .`) is a normal, real pattern in production Playwright frameworks, not a workaround.

## Committing credentials to git

- The `standard_user` / `secret_sauce` / etc. test accounts hardcoded in `test_login.py` are fine to commit — SauceDemo publishes them openly specifically for automation practice, they aren't secrets.
- General principle for real projects: never commit real credentials/API keys/tokens to git, even in a private repo (history persists, repos leak). Standard fix: load them from environment variables at runtime via a `.env` file, and keep `.env` itself git-ignored (already set up in `.gitignore` from day one). CI systems (e.g. GitHub Actions "Secrets") provide the same values at pipeline runtime without ever putting them in code. This is Week 6 territory — not needed yet since nothing here is a real secret.

## `if/else` branches and code that runs after them

- Code placed *after* an `if/else` block (not indented into either branch) runs **regardless of which branch executed** — it's not tied to either path.
- Real bug I hit: in the checkout form validation test, the "click finish" + "assert order complete" steps were written after the `if/else` instead of inside the `else`. So even when checkout correctly failed validation (`if` branch), execution still fell through to code that assumed checkout had succeeded — clicking a "finish" button that only exists on a screen you never reached because validation blocked you. Symptom was the same kind of hang/timeout as the f-string bug — the locator for that button just never matched anything on the page actually shown.
- Also hit a **`NameError`** variant of this same shape earlier: a variable only assigned inside one branch (`else`) being referenced by code that runs for the other branch (`if`) too. Fix in both cases is the same: identify what should *actually* only happen for one specific branch, and move it inside that branch's indentation rather than leaving it to run unconditionally after.

## Don't call one test from another

- Tempting shortcut: reuse a parametrized test (`test_cart_count`) by calling it directly from inside a different test (`test_checkout`). Wrong move — it wouldn't even work correctly (parametrize's extra arguments aren't supplied on a manual call, and pytest's fixture injection only happens when *pytest* calls the function, not when your own code does).
- More importantly, tests calling tests couples them — a change to one silently breaks the other for unrelated reasons, and failures stop pointing at one clear cause.
- Correct reuse target: the **page object** the test itself calls (`InventoryPage.add_to_cart(...)`), not the test function. Rule of thumb: tests call page objects/helpers; page objects/helpers never call tests.

## Network mocking

- `page.route(pattern, handler)` intercepts a matching request before it hits the real network. Inside the handler: `route.continue_()` (let it through), `route.fulfill(...)` (fake a response), or `route.abort()` (simulate it failing).
- `**` in the pattern matches anything including slashes (any depth of path); a single `*` doesn't cross `/`.
- Must call `page.route(...)` *before* the request actually happens — it only catches requests made after it's registered, so an already-loaded page may need a `page.reload()` to trigger a fresh (interceptable) request.
- `.evaluate(js)` runs real JavaScript in the browser and returns the result to Python — the escape hatch for anything Playwright's Python API doesn't wrap directly, like `el.naturalWidth` (a real browser property, `0` if an image never loaded).
- Real reasons to mock: test how the UI handles failure conditions you can't trigger for real (broken image, dead server), and block third-party calls (analytics beacons) during test runs so they don't pollute real data or make the suite depend on a third party's uptime.
- Checked what SauceDemo actually requests over the network before picking what to mock, instead of guessing — turned out there's no real backend API, but there are real image and analytics requests worth intercepting.
- `context.set_offline(True)` simulates the *whole* connection dropping (not just one request) — a real navigation like `page.reload()` then raises an actual exception (`net::ERR_INTERNET_DISCONNECTED`), verified directly rather than assumed.
- `pytest.raises(ExceptionType)` — a test that only passes if the code inside the `with` block actually raises that exception; no exception means the test fails. Useful when the correct behavior *is* an error.

## Externalizing test data

- Inline literal lists in `parametrize` are fine for a small suite — no need to "fix" them just because a bigger project might do it differently. The real trigger to externalize is scale: data shared across files, or data a non-engineer (QA lead, PM) should be able to edit without touching Python.
- Real teams move data into JSON/YAML/CSV files, loaded **at collection time** (module import, before any test runs) into a plain Python variable, which then feeds `parametrize` exactly like a literal list would — `parametrize` doesn't care where its list came from.
- Same anchored-path trick as `storage_state.json`: `Path(__file__).parent / "data" / "login_cases.json"`, so it resolves the same regardless of which directory `pytest` is invoked from.
- Python's `None` becomes JSON's `null` and back again automatically through `json.loads`/`json.dumps` — no special handling needed for the "no error expected" case.
- For *generated* (not just externalized) data — avoiding hardcoded values that collide on reruns, like a signup email that already exists the second time — the `Faker` library is the standard real-world tool (`fake.email()`, `fake.first_name()`, etc.), though not something this project needs yet.

## API testing with Playwright's `request` context

- Playwright can make raw HTTP calls without launching a browser at all — much faster, useful for testing the shape of data (status codes, JSON bodies) rather than the rendered UI. Matches the test pyramid idea: API tests are cheaper/faster than UI tests, so they're worth having more of.
- Built via the session-scoped `playwright` fixture (the raw driver object, provided by `pytest-playwright`): `playwright.request.new_context(base_url=...)`. `base_url` lets tests use short paths (`/posts/1`) instead of full URLs.
- **Plain `assert`, not `expect()`, for API responses.** `expect()` exists to auto-retry while something is still rendering — a UI-specific problem. An API response has already fully arrived by the time `.get()`/`.post()` returns; there's nothing left to wait for, so reaching for `expect()` here solves a problem that doesn't exist.
- `response.ok` (bool, true for any 2xx), `response.status` (numeric code), `response.json()` (parses body into a Python dict) — the core things to assert on.
- `POST` needs a request body: pass a plain dict as `data=`, Playwright serializes it to JSON and sets the content-type header automatically. `201` is the conventional status for "created something" (vs. generic `200`).
- **Don't hedge with `if/else` on behavior you haven't actually confirmed.** First version of a "nonexistent resource" test branched on `if response.status == 404: ... else: ...` — but a real request showed the API *always* returns `404` with an empty body `{}` for a bad id; that's one guaranteed fact, not two possibilities. A test that accepts multiple different outcomes as equally "correct" can't actually detect when real behavior changes. Same principle as verifying exact UI error text instead of guessing: hit the real endpoint once, see what it actually does, then assert that directly — no branching.

## Storage state — reusing a login session

- A login session is really just a cookie the site checks for. Playwright can save that cookie to a file after one real login (`context.storage_state(path=...)`) and load it straight into a fresh browser context for later tests (`browser.new_context(storage_state=path)`) — skipping the UI login form entirely.
- Needed the `browser` fixture (not `page`) to implement this, since it requires manually building the context (to control what goes into it) rather than letting the automatic `page` fixture do it invisibly.
- Two fixtures, two different frequencies: `storage_state_path` (`scope="session"`) does the one real login and returns the saved file's path — runs once for the whole test run. `logged_in_page` (default `scope="function"`) builds a *fresh* context per test from that saved file — keeps every test isolated, same as before, just without repeating the slow part.
- **Bug I hit:** after loading storage state into a new context, the resulting page still started at `about:blank` — the cookie was valid, but nothing had actually navigated anywhere yet, so the site never got a chance to use it. Fix: explicitly `page.goto(...)` after creating the page. A saved session isn't useful until you load a page that checks for it.
- **Relative file paths are fragile:** `"storage_state.json"` (a plain relative string) resolves against whatever directory `pytest` happens to be run *from*, not against where the code lives — same class of bug as the earlier `pytest tests/test_checkout.py` path mixup. Fixed by anchoring to the file's own location: `str(Path(__file__).parent / "storage_state.json")`.
- **Result: correctness fixed, but total suite time barely changed** (13.86s vs 13.91s) — and that's expected, not a sign something's wrong. Only `test_checkout.py`/`test_inventory.py` (9 of 16 tests) even use `logged_in_page`; `test_login.py`'s 7 tests intentionally still do a real login every time since login itself is what they're testing. And what storage state skips (typing two fields + one click) was never the slow part — Playwright does that near-instantly; the real cost per test is the network page load, which still has to happen either way. The technique is correctly implemented; it just isn't this suite's bottleneck. Would matter far more at hundreds of tests or a slower/multi-step login flow.

## Dynamic locators from a parameter

- Some `data-test` attributes follow a predictable pattern (`add-to-cart-<product-slug>`), so instead of one hardcoded locator per product, build it dynamically with an **f-string**: `page.locator(f'[data-test="add-to-cart-{item_slug}"]')`. One method then works for any product.
- **Common mistake I made:** forgot the `f` prefix — `page.locator('[data-test="add-to-cart-{item_slug}"]')` (no `f`) is a plain string, so `{item_slug}` is treated as literal text instead of being substituted. The locator then searches for an element with the literal attribute value `add-to-cart-{item_slug}`, which doesn't exist on the real page.
- The symptom wasn't a clean error — it was a **hang/timeout** (Playwright kept retrying for 30s waiting for an element that will never appear), not an immediate crash. Worth remembering: a test that hangs instead of failing fast is often a locator that will never match, not a slow page.

## Where assertions belong in Page Object Model

- Page objects expose **locators** as attributes (e.g. `self.cart_badge = page.locator(...)`); they don't decide what the "correct" value is. The **test** does the asserting (`expect(inventory_page.cart_badge).to_have_text("2")`), not the page class.
- Reasoning: different tests may want to assert different things about the same element. If the page class hardcoded the assertion, every test would be forced to agree on the same expected value.

## Splitting expensive vs. cheap tests (test pyramid in practice)

- `test_checkout.py` is a full end-to-end flow (login -> add items -> checkout form -> confirmation) — the most expensive kind of test. Kept it as a single, fixed, representative happy path rather than parametrizing it, since parametrizing an e2e test multiplies its cost every run for questions that don't need the whole flow to answer.
- Pulled the "does the cart badge show the right count after adding N items" check into its own separate, cheaper, more heavily parametrized test (`test_inventory.py`) that stops right after adding items — no checkout, no confirmation screen. Matches the test pyramid idea from Week 1: cheap/narrow checks get parametrized freely, expensive e2e flows stay few and deliberate.

## Project progress so far

- `tests/test_checkout.py` — login → add 2 items to cart → checkout → assert order confirmation, against saucedemo.com
- `tests/conftest.py` — `logged_in_page` fixture shared across future tests
- `tests/test_login.py` — parametrized login test covering 7 cases: success, locked-out account, blank username, blank password, blank username with valid password, wrong password, and unknown username — asserting exact error text for each
- `pages/login_page.py` — `LoginPage` class (Page Object Model) wrapping login locators/actions; used by both `test_login.py` and the `logged_in_page` fixture in `conftest.py`
- `pages/inventory_page.py` — `InventoryPage` class with a dynamic `add_to_cart(item_slug)` and exposed `cart_badge`/`inventory_container` locators
- `tests/test_inventory.py` — parametrized cart-count test using `InventoryPage`, separate from the full checkout e2e flow
- `pages/checkout_page.py`, `checkout_info_page.py`, `checkout_overview.py`, `checkout_complete_page.py` — POM classes covering the full checkout flow (cart -> info form -> overview -> confirmation)
- `tests/test_checkout.py` — fully refactored to use the page object classes above; parametrized over 7 cases covering required-field validation (first name / last name / postal code, in different combinations) plus the full happy-path checkout
- `pytest.ini` — sets `pythonpath = .` so `pages/` is importable from `tests/`
- `tests/test_api.py` — API-only tests (no browser) against `jsonplaceholder.typicode.com` via Playwright's `request` context: a verified-404 case, a parametrized multi-id GET, and a POST test
- `tests/data/login_cases.json` — login test cases externalized from `test_login.py`, loaded at collection time into `parametrize`

## Required-field / negative testing

- Testing that a form's validation actually blocks submission when required data is missing — a very common real-world QA task, since devs usually test the happy path and skip edge cases.
- Extended `test_login_attempt`'s parametrize to include `password` as its own parameter (not hardcoded) so blank-password cases could be tested too, alongside blank-username cases.
- Verified the exact validation error text (`"Epic sadface: Username is required"` / `"Epic sadface: Password is required"`) by triggering it on the real site first — same lesson as before: don't guess expected text, confirm it.
