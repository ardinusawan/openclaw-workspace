from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=30000)
    
    # Extract text
    text = page.inner_text("body")
    
    # Extract structured data if needed
    try:
        title = page.title()
        print(f"Title: {title}")
        print(f"\nContent:\n{text[:5000]}")
    except:
        print(text)
    
    browser.close()
