import asyncio
import os
from app.core.browser import BrowserManager

async def test_browser():
    # Test with a real restaurant website
    test_url = "https://www.chipotle.com"
    
    print(f"Testing browser automation with: {test_url}")
    print("=" * 50)
    
    # Create screenshots directory if it doesn't exist
    os.makedirs("/tmp/screenshots", exist_ok=True)
    
    try:
        # Use BrowserManager as async context manager
        async with BrowserManager(headless=True) as browser:
            result = await browser.analyze_website(test_url)
        
        print("\n✅ Analysis Results:")
        print(f"URL: {result.get('url')}")
        print(f"Has SSL: {result.get('has_ssl')}")
        print(f"Mobile Responsive: {result.get('mobile_responsive')}")
        print(f"Title: {result.get('page_title')}")
        print(f"\nOrder Button Detection:")
        print(f"  Found: {result.get('order_button_detected')}")
        print(f"  Text: {result.get('button_text')}")
        print(f"  Selector: {result.get('button_selector')}")
        print(f"  Platforms: {result.get('platforms')}")
        print(f"\nScreenshot: {result.get('screenshot_path')}")
        print(f"Error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_browser())
