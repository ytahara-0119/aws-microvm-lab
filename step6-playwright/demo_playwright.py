from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path("/root/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:

    browser = p.firefox.launch(
        headless=False,
    )
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto("https://www.google.com", wait_until="domcontentloaded")

    page.screenshot(path=str(ARTIFACT_DIR / "google.png"), full_page=True)

    page.goto("https://www.yahoo.co.jp", wait_until="domcontentloaded")
    page.screenshot(path=str(ARTIFACT_DIR / "yahoo.png"), full_page=True)

    print("Playwright demo completed.")
    print(f"Saved screenshots to: {ARTIFACT_DIR}")

    # Keep browser open so noVNC can show it.
    page.wait_for_timeout(10 * 60 * 1000)

    browser.close()
