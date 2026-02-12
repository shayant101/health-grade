"""
Detailed Panera debug - check if "start an order" exists
"""
import asyncio
from app.core.browser import BrowserManager

async def debug_panera_detailed():
    """Check specifically for 'start an order' text"""
    url = "https://www.panerabread.com"
    
    print(f"Analyzing: {url}\n")
    
    async with BrowserManager(headless=True) as browser:
        page = await browser.create_page()
        await page.goto(url, wait_until="networkidle")
        
        # Check if "start an order" text exists anywhere
        print("=== Checking for 'start an order' text ===")
        has_text = await page.evaluate('''() => {
            const bodyText = document.body.innerText.toLowerCase();
            return bodyText.includes('start an order');
        }''')
        print(f"Page contains 'start an order': {has_text}")
        
        # Find all elements with "start" in text
        print("\n=== Elements containing 'start' ===")
        start_elements = await page.evaluate('''() => {
            const elements = Array.from(document.querySelectorAll('button, a'));
            return elements
                .filter(el => el.innerText && el.innerText.toLowerCase().includes('start'))
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText.substring(0, 100),
                    id: el.id,
                    className: el.className
                }));
        }''')
        
        for i, el in enumerate(start_elements[:10]):
            print(f"{i+1}. {el['tag']}: '{el['text']}' (id={el['id']}, class={el['className'][:50]})")
        
        # Find all elements with "order" in text
        print("\n=== Elements containing 'order' ===")
        order_elements = await page.evaluate('''() => {
            const elements = Array.from(document.querySelectorAll('button, a'));
            return elements
                .filter(el => el.innerText && el.innerText.toLowerCase().includes('order'))
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText.substring(0, 100),
                    id: el.id,
                    className: el.className
                }));
        }''')
        
        for i, el in enumerate(order_elements[:10]):
            print(f"{i+1}. {el['tag']}: '{el['text']}' (id={el['id']}, class={el['className'][:50]})")
        
        await page.close()

if __name__ == "__main__":
    asyncio.run(debug_panera_detailed())
