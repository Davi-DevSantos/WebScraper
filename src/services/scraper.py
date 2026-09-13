from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import pandas

def scrape(url):
    with sync_playwright() as client:
        browser = client.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0"
            " (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            locale="pt-BR",
            timezone_id="America/Sao_paulo",
            extra_http_headers={"Accept_Language": "pt-BR,pt;q=0.9"})

        page = context.new_page()
        stealth_sync(page)
        page.goto(url)

        page.route("**/*.{png,jpg,jpeg,woff2}", lambda route: route.abort())
        page.route("**/*", lambda route: route.continue_() if "bot-detector" not in route.request.url
                   else route.abort())
        try:
            page.wait_for_selector(".col-md-4.country")

            country_infos = page.locator(".col-md-4.country").evaluate_all("""
            els => els.map(e => ({nome: e.querySelector('.country-name')?.innerText.trim(),
            capital: e.querySelector('.country-capital')?.innerText.trim(),
            populacao: e.querySelector('.country-population')?.innerText.trim(),
            area: e.querySelector('.country-area')?.innerText.trim(),
            }))""")

            pandas.DataFrame(country_infos).to_excel("src/results/scrape.xlsx", index=False)
        finally:
            browser.close()
