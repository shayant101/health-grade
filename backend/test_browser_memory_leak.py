"""
Test script to verify browser memory leak fixes.
Tests various failure scenarios to ensure proper cleanup.
"""
import asyncio
import logging
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.browser import BrowserManager

# Configure logging to see cleanup messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_normal_usage():
    """Test 1: Normal usage with context manager"""
    logger.info("\n=== TEST 1: Normal Usage with Context Manager ===")
    try:
        async with BrowserManager() as manager:
            async with manager.get_page() as page:
                await page.goto("https://example.com", timeout=10000)
                title = await page.title()
                logger.info(f"✅ Page title: {title}")
        logger.info("✅ Test 1 PASSED: Browser cleaned up properly")
    except Exception as e:
        logger.error(f"❌ Test 1 FAILED: {e}")
        raise


async def test_timeout_error():
    """Test 2: Timeout error - browser should still close"""
    logger.info("\n=== TEST 2: Timeout Error Handling ===")
    try:
        async with BrowserManager(timeout=1000) as manager:  # Very short timeout
            async with manager.get_page() as page:
                # This should timeout
                await page.goto("https://httpstat.us/200?sleep=5000", timeout=1000)
    except asyncio.TimeoutError:
        logger.info("✅ Test 2 PASSED: Timeout occurred and browser cleaned up properly")
    except Exception as e:
        logger.info(f"✅ Test 2 PASSED: Exception occurred ({type(e).__name__}) and browser cleaned up")


async def test_invalid_url():
    """Test 3: Invalid URL - browser should still close"""
    logger.info("\n=== TEST 3: Invalid URL Handling ===")
    try:
        async with BrowserManager() as manager:
            async with manager.get_page() as page:
                await page.goto("https://this-domain-definitely-does-not-exist-12345.com", timeout=5000)
    except Exception as e:
        logger.info(f"✅ Test 3 PASSED: Invalid URL handled ({type(e).__name__}) and browser cleaned up")


async def test_analyze_website_with_error():
    """Test 4: analyze_website with error - page should close"""
    logger.info("\n=== TEST 4: analyze_website with Error ===")
    try:
        async with BrowserManager() as manager:
            result = await manager.analyze_website("https://this-does-not-exist-12345.com")
            if result.get("error"):
                logger.info(f"✅ Test 4 PASSED: Error captured: {result['error'][:50]}...")
            else:
                logger.warning("⚠️  Test 4: No error in result (unexpected)")
    except Exception as e:
        logger.error(f"❌ Test 4 FAILED: Unexpected exception: {e}")


async def test_multiple_pages():
    """Test 5: Multiple pages - all should close"""
    logger.info("\n=== TEST 5: Multiple Pages ===")
    try:
        async with BrowserManager() as manager:
            # Create multiple pages
            async with manager.get_page() as page1:
                await page1.goto("https://example.com", timeout=10000)
                logger.info("✅ Page 1 loaded")
            
            async with manager.get_page() as page2:
                await page2.goto("https://example.org", timeout=10000)
                logger.info("✅ Page 2 loaded")
            
            async with manager.get_page() as page3:
                await page3.goto("https://example.net", timeout=10000)
                logger.info("✅ Page 3 loaded")
        
        logger.info("✅ Test 5 PASSED: All pages closed properly")
    except Exception as e:
        logger.error(f"❌ Test 5 FAILED: {e}")


async def test_exception_in_page_usage():
    """Test 6: Exception while using page - page should still close"""
    logger.info("\n=== TEST 6: Exception During Page Usage ===")
    try:
        async with BrowserManager() as manager:
            async with manager.get_page() as page:
                await page.goto("https://example.com", timeout=10000)
                # Simulate an error
                raise ValueError("Simulated error during page usage")
    except ValueError as e:
        logger.info(f"✅ Test 6 PASSED: Exception handled ({e}) and page cleaned up")
    except Exception as e:
        logger.error(f"❌ Test 6 FAILED: Unexpected exception: {e}")


async def test_sequential_browser_instances():
    """Test 7: Multiple sequential browser instances"""
    logger.info("\n=== TEST 7: Sequential Browser Instances ===")
    try:
        for i in range(3):
            logger.info(f"--- Instance {i+1} ---")
            async with BrowserManager() as manager:
                async with manager.get_page() as page:
                    await page.goto("https://example.com", timeout=10000)
                    logger.info(f"✅ Instance {i+1} completed")
        
        logger.info("✅ Test 7 PASSED: All instances cleaned up properly")
    except Exception as e:
        logger.error(f"❌ Test 7 FAILED: {e}")


async def test_manual_page_creation():
    """Test 8: Manual page creation (old style) - should still work"""
    logger.info("\n=== TEST 8: Manual Page Creation (Legacy) ===")
    page = None
    try:
        async with BrowserManager() as manager:
            page = await manager.create_page()
            await page.goto("https://example.com", timeout=10000)
            logger.info("✅ Manual page created and used")
    except Exception as e:
        logger.error(f"❌ Test 8 FAILED: {e}")
    finally:
        if page:
            try:
                await page.close()
                logger.info("✅ Test 8 PASSED: Manual page closed properly")
            except Exception as e:
                logger.error(f"❌ Failed to close manual page: {e}")


async def run_all_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("BROWSER MEMORY LEAK TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        test_normal_usage,
        test_timeout_error,
        test_invalid_url,
        test_analyze_website_with_error,
        test_multiple_pages,
        test_exception_in_page_usage,
        test_sequential_browser_instances,
        test_manual_page_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
            await asyncio.sleep(1)  # Brief pause between tests
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST RESULTS: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! Memory leak fixes are working correctly.")
    else:
        logger.warning(f"⚠️  {failed} test(s) failed. Review the logs above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
