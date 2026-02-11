import asyncio
import os
from app.core.browser import BrowserManager

async def test_single_website(url: str):
    """Test a single website"""
    print(f"\nTesting browser automation with: {url}")
    print("=" * 70)
    
    try:
        # Use BrowserManager as async context manager
        async with BrowserManager(headless=True) as browser:
            result = await browser.analyze_website(url)
        
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
        if result.get('error'):
            print(f"Error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_browser():
    """Test browser automation with multiple restaurant websites"""
    # Create screenshots directory if it doesn't exist
    os.makedirs("/tmp/screenshots", exist_ok=True)
    
    # Test URLs
    test_urls = [
        "https://www.chipotle.com",
        "https://lakaviet.com",
        "https://www.burgertownusa.net/"
    ]
    
    results = []
    for url in test_urls:
        result = await test_single_website(url)
        results.append(result)
        print("\n" + "=" * 70)
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("=" * 70)
    for i, (url, result) in enumerate(zip(test_urls, results), 1):
        if result and not result.get('error'):
            print(f"{i}. ✅ {url}")
            print(f"   - SSL: {result.get('has_ssl')}")
            print(f"   - Order Button: {result.get('order_button_detected')}")
            print(f"   - Screenshot: {result.get('screenshot_path')}")
        else:
            print(f"{i}. ❌ {url} - FAILED")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_browser())
