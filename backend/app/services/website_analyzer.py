import asyncio
import httpx
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from ..core.browser import browser_manager
from ..config import settings

class WebsiteAnalyzer:
    """
    Comprehensive website analysis service using PageSpeed Insights and Playwright.
    Provides detailed insights into website performance, mobile-friendliness, and accessibility.
    """
    
    PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    @classmethod
    async def analyze_website(
        cls, 
        url: str, 
        mobile: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive website analysis.
        
        Args:
            url (str): Website URL to analyze
            mobile (bool): Whether to analyze mobile or desktop version
        
        Returns:
            Dict[str, Any]: Detailed website analysis results
        """
        # Validate and normalize URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"https://{url}"
        
        # Perform parallel analysis
        pagespeed_task = cls._analyze_pagespeed(url, mobile)
        playwright_task = cls._analyze_with_playwright(url)
        
        # Wait for both tasks
        pagespeed_results, playwright_results = await asyncio.gather(
            pagespeed_task, 
            playwright_task
        )
        
        # Combine results
        combined_results = {
            **pagespeed_results,
            **playwright_results
        }
        
        return combined_results
    
    @classmethod
    async def _analyze_pagespeed(
        cls, 
        url: str, 
        mobile: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze website using Google PageSpeed Insights.
        
        Args:
            url (str): Website URL
            mobile (bool): Mobile or desktop analysis
        
        Returns:
            Dict[str, Any]: PageSpeed analysis results
        """
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                # Build params list to include multiple categories
                params = [
                    ('url', url),
                    ('key', settings.PAGESPEED_API_KEY),
                    ('strategy', 'MOBILE' if mobile else 'DESKTOP'),
                    ('category', 'PERFORMANCE'),
                    ('category', 'ACCESSIBILITY'),
                    ('category', 'BEST_PRACTICES'),
                    ('category', 'SEO')
                ]
                
                response = await client.get(cls.PAGESPEED_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract key metrics
                lighthouse_result = data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                
                return {
                    'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                    'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                    'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100,
                    'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                    'loading_time_ms': lighthouse_result.get('audits', {}).get('interactive', {}).get('numericValue', 0)
                }
        
        except Exception as e:
            logging.error(f"PageSpeed Insights error for {url}: {e}")
            # Graceful degradation - PageSpeed is optional
            return {}
    
    @classmethod
    async def _analyze_with_playwright(cls, url: str) -> Dict[str, Any]:
        """
        Perform website analysis using Playwright.
        
        Args:
            url (str): Website URL to analyze
        
        Returns:
            Dict[str, Any]: Playwright-based analysis results
        """
        try:
            async with browser_manager.get_page() as page:
                # Navigate to the website with increased timeout (30 seconds)
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                
                # Check HTTPS
                https_enabled = page.url.startswith('https://')
                
                # Check mobile friendliness (viewport)
                await page.set_viewport_size({'width': 375, 'height': 667})
                
                # Check for responsive design
                body_width = await page.evaluate('() => document.body.clientWidth')
                mobile_friendly = body_width <= 480
                
                # Check for key elements
                has_contact_form = await page.evaluate(
                    '() => document.querySelector("form[name*=contact], input[type=email]") !== null'
                )
                
                # Check for online ordering links
                online_ordering_links = await page.evaluate(
                    '() => Array.from(document.querySelectorAll("a")).filter(a => a.href.includes("order") || a.href.includes("delivery")).length'
                )
                
                return {
                    'https_enabled': https_enabled,
                    'mobile_friendly': mobile_friendly,
                    'has_contact_form': has_contact_form,
                    'online_ordering_links_count': online_ordering_links,
                    'page_title': await page.title(),
                    'meta_description': await page.evaluate('() => document.querySelector("meta[name=description]")?.content')
                }
        
        except Exception as e:
            logging.error(f"Playwright analysis error for {url}: {e}")
            raise  # Re-raise to allow proper error handling upstream
    
    @classmethod
    async def check_website_availability(cls, url: str) -> bool:
        """
        Check if a website is available and responds correctly.
        
        Args:
            url (str): Website URL to check
        
        Returns:
            bool: Whether the website is available
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try HEAD first (faster)
                try:
                    response = await client.head(url, follow_redirects=True)
                    if response.status_code < 400:
                        return True
                except Exception:
                    # If HEAD fails, try GET (some sites block HEAD requests)
                    pass
                
                # Fallback to GET request
                response = await client.get(url, follow_redirects=True)
                return response.status_code < 400
        
        except httpx.TimeoutException:
            logging.warning(f"Website availability check timed out for {url}")
            # Don't fail on timeout - let the main analysis handle it
            return True
        except Exception as e:
            logging.warning(f"Website availability check failed for {url}: {e}")
            return False