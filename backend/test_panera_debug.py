"""
Debug Panera Bread specifically to find the order button
"""
import asyncio
from app.core.browser import BrowserManager

async def debug_panera():
    """Find all buttons and links on Panera to identify the order button"""
    url = "https://www.panerabread.com"
    
    print(f"Analyzing: {url}\n")
    
    async with BrowserManager(headless=True) as browser:
        page = await browser.create_page()
        await page.goto(url, wait_until="networkidle")
        
        # Find all buttons
        print("=== ALL BUTTONS ===")
        buttons = await page.query_selector_all('button')
        for i, button in enumerate(buttons[:15]):  # First 15 buttons
            try:
                text = await button.inner_text()
                if text and len(text) < 100:  # Skip very long text
                    print(f"{i+1}. Button: '{text.strip()}'")
            except:
                pass
        
        # Find all links
        print("\n=== ALL LINKS (with 'order' or 'start') ===")
        links = await page.query_selector_all('a')
        for i, link in enumerate(links):
            try:
                text = await link.inner_text()
                if text and ('order' in text.lower() or 'start' in text.lower()):
                    href = await link.get_attribute('href')
                    print(f"{i+1}. Link: '{text.strip()}' -> {href}")
            except:
                pass
        
        await page.close()

if __name__ == "__main__":
    asyncio.run(debug_panera())
