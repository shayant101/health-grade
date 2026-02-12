"""
Debug script to see exactly what order buttons are being detected
"""
import asyncio
from app.core.browser import BrowserManager

async def debug_order_button(url: str, name: str):
    """Test a single website and show detailed detection info"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    try:
        async with BrowserManager(headless=True) as browser:
            result = await browser.analyze_website(url)
        
        print("\n📊 Detection Results:")
        print(f"  Order Button Detected: {result.get('order_button_detected')}")
        print(f"  Button Text: '{result.get('button_text')}'")
        print(f"  Button Selector: {result.get('button_selector')}")
        print(f"  Platforms: {result.get('platforms')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Test specific websites with issues"""
    
    # Test Burger Town USA - detecting "Menu" incorrectly
    await debug_order_button(
        "https://www.burgertownusa.net/",
        "Burger Town USA"
    )
    
    # Test La KaViet - showing "Order Now" instead of "Order Online"
    await debug_order_button(
        "https://lakaviet.com",
        "La KaViet"
    )
    
    # Test Panera - to verify what it actually found
    await debug_order_button(
        "https://www.panerabread.com",
        "Panera Bread"
    )

if __name__ == "__main__":
    asyncio.run(main())
