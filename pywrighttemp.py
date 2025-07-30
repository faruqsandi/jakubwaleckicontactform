from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Set headless=True to run without UI
    page = browser.new_page()

    # Open Google
    page.goto("https://www.google.com")

    # Accept cookies if the consent form appears
    try:
        page.click("text=I agree")  # For English
    except:
        pass

    # Fill search input and hit Enter
    page.fill("input[name='q']", "OpenAI ChatGPT")
    page.keyboard.press("Enter")

    # Wait for results to load
    page.wait_for_selector("h3")

    # Click the first result
    page.click("h3")

    # Keep browser open for a while
    page.wait_for_timeout(5000)
    print(page.title())
    browser.close()
