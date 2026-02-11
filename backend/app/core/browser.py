import asyncio
import logging
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from urllib.parse import urlparse

class BrowserManager:
    """
    Manages Playwright browser lifecycle for website analysis and order button detection.
    
    Provides an async context manager for browser initialization, page creation,
    and comprehensive website analysis capabilities with proper resource cleanup.
    """
    
    def __init__(self,
                 headless: bool = True,
                 viewport: Dict[str, int] = {"width": 375, "height": 667},
                 timeout: int = 30000):
        """
        Initialize BrowserManager with configurable settings.
        
        Args:
            headless (bool): Run browser in headless mode. Defaults to True.
            viewport (Dict[str, int]): Mobile viewport size. Defaults to 375x667.
            timeout (int): Navigation and interaction timeout in milliseconds.
        """
        self._headless = headless
        self._viewport = viewport
        self._timeout = timeout
        self._playwright = None
        self._browser = None
        self._context = None
        self._logger = logging.getLogger(__name__)
        self._active_pages = set()  # Track active pages for cleanup

    async def __aenter__(self):
        """
        Async context manager entry point.
        Initializes Playwright and launches browser.
        
        Returns:
            BrowserManager: Configured browser manager instance.
        """
        try:
            self._logger.info("Initializing Playwright browser...")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self._headless,
                timeout=self._timeout
            )
            self._context = await self._browser.new_context(
                viewport=self._viewport,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            )
            self._logger.info("Browser initialized successfully")
            return self
        except Exception as e:
            self._logger.error(f"Failed to initialize browser: {e}")
            await self.close()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        Ensures all resources are properly cleaned up even on exceptions.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if exc_type:
            self._logger.warning(f"Exiting browser context due to exception: {exc_type.__name__}: {exc_val}")
        await self.close()
        return False  # Don't suppress exceptions

    @asynccontextmanager
    async def get_page(self):
        """
        Context manager for creating and automatically cleaning up a page.
        This is the recommended way to use pages to prevent memory leaks.
        
        Usage:
            async with browser_manager.get_page() as page:
                await page.goto(url)
                # ... work with page ...
            # Page is automatically closed
        
        Yields:
            Page: Configured Playwright page that will be automatically closed.
        """
        page = None
        try:
            if not self._context:
                raise RuntimeError("Browser context not initialized. Use 'async with BrowserManager()' first.")
            
            page = await self._context.new_page()
            page.set_default_timeout(self._timeout)
            self._active_pages.add(page)
            self._logger.debug(f"Created new page. Active pages: {len(self._active_pages)}")
            yield page
        except Exception as e:
            self._logger.error(f"Error in page context: {e}")
            raise
        finally:
            if page:
                try:
                    await page.close()
                    self._active_pages.discard(page)
                    self._logger.debug(f"Closed page. Active pages: {len(self._active_pages)}")
                except Exception as e:
                    self._logger.error(f"Error closing page: {e}")

    async def create_page(self) -> Page:
        """
        Create a new page with configured settings.
        
        WARNING: When using this method directly, you MUST manually close the page
        to prevent memory leaks. Consider using get_page() context manager instead.
        
        Returns:
            Page: Configured Playwright page.
        """
        try:
            if not self._context:
                raise RuntimeError("Browser context not initialized. Use 'async with BrowserManager()' first.")
            
            page = await self._context.new_page()
            page.set_default_timeout(self._timeout)
            self._active_pages.add(page)
            self._logger.debug(f"Created new page (manual). Active pages: {len(self._active_pages)}")
            return page
        except Exception as e:
            self._logger.error(f"Failed to create page: {e}")
            raise

    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Comprehensive website analysis function with proper resource cleanup.
        
        Args:
            url (str): Website URL to analyze.
        
        Returns:
            Dict[str, Any]: Analysis results including SSL, responsiveness, title, etc.
        """
        analysis = {
            "url": url,
            "has_ssl": False,
            "mobile_responsive": False,
            "page_title": "",
            "meta_description": "",
            "order_button_detected": False,
            "screenshot_path": "",
            "error": None
        }

        page = None
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL")

            # Check SSL
            analysis["has_ssl"] = parsed_url.scheme == "https"

            # Create page with tracking
            page = await self.create_page()

            # Navigate to page
            await page.goto(url, wait_until="networkidle", timeout=self._timeout)

            # Capture screenshot
            screenshot_path = f"/tmp/screenshots/{parsed_url.netloc}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            analysis["screenshot_path"] = screenshot_path

            # Page title
            analysis["page_title"] = await page.title()

            # Meta description
            meta_desc_element = await page.query_selector('meta[name="description"]')
            if meta_desc_element:
                analysis["meta_description"] = await meta_desc_element.get_attribute('content') or ""

            # Mobile responsiveness check
            viewport_width = await page.evaluate('() => window.innerWidth')
            analysis["mobile_responsive"] = viewport_width <= 480

            # Order button detection
            order_button = await self.detect_order_button(page)
            analysis.update(order_button)

        except asyncio.TimeoutError as e:
            self._logger.error(f"Timeout analyzing {url}: {e}")
            analysis["error"] = f"Timeout: {str(e)}"
        except Exception as e:
            self._logger.error(f"Website analysis error for {url}: {e}")
            analysis["error"] = str(e)
        finally:
            # CRITICAL: Always close the page to prevent memory leaks
            if page:
                try:
                    await page.close()
                    self._active_pages.discard(page)
                    self._logger.debug(f"Closed analysis page. Active pages: {len(self._active_pages)}")
                except Exception as e:
                    self._logger.error(f"Error closing page in analyze_website: {e}")

        return analysis

    async def detect_order_button(self, page: Page) -> Dict[str, Any]:
        """
        Detect order buttons on a webpage.
        
        Args:
            page (Page): Playwright page to analyze.
        
        Returns:
            Dict[str, Any]: Order button detection results.
        """
        order_patterns = [
            'order', 'order now', 'order online', 
            'delivery', 'pickup', 'menu', 'food'
        ]
        order_selectors = [
            'a.order', '.order-button', 'button.order', 
            'a[href*="order"]', 'button[data-testid*="order"]'
        ]
        third_party_platforms = [
            'doordash', 'ubereats', 'grubhub', 
            'postmates', 'seamless', 'chownow'
        ]

        results = {
            "order_button_detected": False,
            "button_text": "",
            "button_selector": "",
            "platforms": []
        }

        try:
            # Check text-based order buttons
            for pattern in order_patterns:
                button = await page.query_selector(f'text="{pattern}"')
                if button:
                    results["order_button_detected"] = True
                    results["button_text"] = await button.inner_text()
                    results["button_selector"] = await self._get_selector(button)
                    break

            # Check selector-based order buttons
            if not results["order_button_detected"]:
                for selector in order_selectors:
                    button = await page.query_selector(selector)
                    if button:
                        results["order_button_detected"] = True
                        results["button_text"] = await button.inner_text() or selector
                        results["button_selector"] = selector
                        break

            # Detect third-party platforms
            page_text = await page.content()
            results["platforms"] = [
                platform for platform in third_party_platforms 
                if platform in page_text.lower()
            ]

        except Exception as e:
            self._logger.warning(f"Order button detection error: {e}")

        return results

    async def _get_selector(self, element) -> str:
        """
        Get a unique selector for a Playwright element.
        
        Args:
            element: Playwright element handle.
        
        Returns:
            str: A unique selector for the element.
        """
        try:
            return await element.evaluate('el => {\
                if (el.id) return `#${el.id}`;\
                if (el.className) return `.${el.className.split(" ").join(".")}`;\
                return el.tagName.toLowerCase();\
            }')
        except Exception:
            return 'unknown'

    async def close(self):
        """
        Close browser resources and stop Playwright with comprehensive cleanup.
        Ensures all resources are freed even if individual cleanup steps fail.
        """
        self._logger.info("Starting browser cleanup...")
        
        # Close all active pages first
        if self._active_pages:
            self._logger.warning(f"Closing {len(self._active_pages)} active pages that weren't properly closed")
            for page in list(self._active_pages):
                try:
                    await page.close()
                except Exception as e:
                    self._logger.error(f"Error closing active page: {e}")
            self._active_pages.clear()
        
        # Close context
        if self._context:
            try:
                await self._context.close()
                self._logger.info("Browser context closed successfully")
            except Exception as e:
                self._logger.error(f"Error closing browser context: {e}")
            finally:
                self._context = None
        
        # Close browser
        if self._browser:
            try:
                await self._browser.close()
                self._logger.info("Browser closed successfully")
            except Exception as e:
                self._logger.error(f"Error closing browser: {e}")
            finally:
                self._browser = None
        
        # Stop Playwright
        if self._playwright:
            try:
                await self._playwright.stop()
                self._logger.info("Playwright stopped successfully")
            except Exception as e:
                self._logger.error(f"Error stopping Playwright: {e}")
            finally:
                self._playwright = None
        
        self._logger.info("Browser cleanup completed")

# Global browser manager instance
browser_manager = BrowserManager()