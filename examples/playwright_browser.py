from playwright.sync_api import sync_playwright

import styne

client = styne.Client()
with client.browsers.create() as browser, sync_playwright() as p:
    page = p.chromium.connect_over_cdp(browser.cdp_url).contexts[0].new_page()
    page.goto("https://example.com")
    print(page.title())
    print("watch live:", browser.live_view_url)
