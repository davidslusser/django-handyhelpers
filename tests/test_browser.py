import pytest
from playwright.sync_api import expect, sync_playwright

pytestmark = [pytest.mark.browser, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def browser_page(live_server):
    # Start Playwright after Django creates the test database and stop its event
    # loop before Django tears it down; no async-safety bypass is needed.
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(live_server.url + "/browser/")
        page.wait_for_function(
            "Boolean(window.htmx && window.bootstrap && window.Chart && window.jQuery?.fn.bootstrapTable)"
        )
        page.wait_for_function(
            'Chart.getChart(document.getElementById("example-chart")) && document.querySelectorAll("#custom-table tbody tr").length===12'
        )
        yield page
        browser.close()
        assert errors == []


def test_modal_validation_upload_and_repeated_swaps(browser_page):
    page = browser_page
    page.locator("#open-modal").click()
    expect(page.locator("#modal_wrapper")).to_be_visible()
    expect(page.locator('#modal_wrapper input[name="name"]')).to_be_visible()
    # Disable browser constraint validation to exercise the server's 422 response.
    page.locator("#modal_wrapper form").evaluate("form => form.noValidate=true")
    page.locator('#modal_wrapper button[type="submit"]').click()
    expect(page.locator("#modal_wrapper .invalid-feedback").first).to_be_visible()
    expect(page.locator("#modal_wrapper")).to_be_visible()
    page.locator('#modal_wrapper input[name="name"]').fill("Browser created")
    page.locator('#modal_wrapper input[name="number"]').fill("3")
    page.locator('#modal_wrapper input[type="file"]').set_input_files(
        {"name": "sample.txt", "mimeType": "text/plain", "buffer": b"upload-data"}
    )
    page.locator('#modal_wrapper button[type="submit"]').click()
    expect(page.locator("#modal_wrapper")).to_be_hidden()
    expect(page.locator(".toast-body")).to_contain_text("11 bytes")
    page.locator("#open-modal").click()
    expect(page.locator('#modal_wrapper input[name="name"]')).to_be_visible()
    expect(page.locator('#modal_wrapper input[name="name"]')).to_have_value("")
    page.locator("#modal_wrapper .btn-close").click()
    expect(page.locator("#modal_wrapper")).to_be_hidden()


def test_tables_charts_and_partial_lifecycle(browser_page):
    page = browser_page
    expect(page.locator("#custom-table tbody tr")).to_have_count(12)
    page.locator("#partial .page-link").nth(1).click()
    expect(page.locator("#custom-table tbody tr").first).to_contain_text("12")
    page.locator("#custom-table th").click()
    page.locator("#custom-table th").click()
    expect(page.locator("#custom-table tbody tr").first).to_contain_text("24")
    for _ in range(2):
        page.locator("#load-partial").click()
        expect(page.locator("#custom-table tbody tr")).to_have_count(12)
        page.locator("#partial .page-link").nth(1).click()
        expect(page.locator("#custom-table tbody tr").first).to_contain_text("12")
    expect(page.locator(".bootstrap-table")).to_have_count(1)
    assert page.evaluate("Object.keys(Chart.instances).length") == 1
    for name in ["table_js", "chart", "clipboard"]:
        expect(page.locator(f'script[data-hh-asset="{name}"]')).to_have_count(1)


def test_bootstrap_controls_and_inline_form(browser_page):
    page = browser_page
    page.locator("#tooltip").hover()
    expect(page.locator(".tooltip")).to_be_visible()
    page.locator("#popover").click()
    expect(page.locator(".popover")).to_be_visible()
    page.locator("#alert .btn-close").click()
    expect(page.locator("#alert")).to_have_count(0)
    page.locator("#sidebar-toggle").click()
    expect(page.locator("#sidebar")).to_have_class("collapsed")
    page.locator(".theme-toggle").click()
    expect(page.locator("html")).to_have_attribute("data-bs-theme", "dark")
    page.locator('#inline-form input[name="name"]').fill("Inline created")
    page.locator('#inline-form input[name="number"]').fill("0")
    page.locator('#inline-form button[type="submit"]').click()
    expect(page.locator("#inline-form")).to_contain_text("Saved inline")
    expect(page.locator('#inline-form button[type="submit"]')).to_be_disabled()
