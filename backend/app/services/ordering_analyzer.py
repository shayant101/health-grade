import logging
from typing import List, Dict, Any, Optional
import httpx
from urllib.parse import urlparse

from ..core.browser import browser_manager

class OrderingAnalyzer:
    """
    Service for detecting and analyzing online ordering capabilities for restaurants.
    Provides comprehensive analysis of ordering platforms and integration quality.
    """
    
    # Known online ordering platforms
    ORDERING_PLATFORMS = [
        'ubereats.com',
        'doordash.com',
        'grubhub.com',
        'postmates.com',
        'seamless.com',
        'chownow.com',
        'toasttab.com',
        'resy.com',
        'opentable.com'
    ]
    
    @classmethod
    async def analyze_ordering_capabilities(
        cls, 
        website_url: str
    ) -> Dict[str, Any]:
        """
        Comprehensively analyze online ordering capabilities.
        
        Args:
            website_url (str): Restaurant website URL
        
        Returns:
            Dict[str, Any]: Detailed online ordering analysis
        """
        try:
            # Detect ordering links on the website
            ordering_links = await cls._find_ordering_links(website_url)
            
            # Check third-party platform availability
            platform_availability = await cls._check_platform_availability(website_url)
            
            # Assess ordering integration quality
            integration_quality = cls._assess_ordering_integration(
                ordering_links, 
                platform_availability
            )
            
            return {
                'online_ordering_available': bool(ordering_links or platform_availability),
                'platforms': list(set(ordering_links + platform_availability)),
                'integration_quality': integration_quality,
                'direct_ordering_links': ordering_links,
                'third_party_platforms': platform_availability
            }
        
        except Exception as e:
            logging.error(f"Ordering analysis error: {e}")
            return cls._default_ordering_analysis()
    
    @classmethod
    async def _find_ordering_links(
        cls, 
        website_url: str
    ) -> List[str]:
        """
        Find direct online ordering links on the restaurant's website.
        
        Args:
            website_url (str): Restaurant website URL
        
        Returns:
            List[str]: List of detected ordering links
        """
        try:
            async with browser_manager.get_page() as page:
                await page.goto(website_url, timeout=15000)
                
                # Look for ordering-related links
                ordering_links = await page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    const orderingKeywords = [
                        'order', 'delivery', 'takeout', 'online menu', 
                        'reserve', 'book table', 'catering'
                    ];
                    
                    return links
                        .filter(link => 
                            orderingKeywords.some(keyword => 
                                link.textContent.toLowerCase().includes(keyword) ||
                                link.href.toLowerCase().includes(keyword)
                            )
                        )
                        .map(link => link.href);
                }''')
                
                return ordering_links
        
        except Exception as e:
            logging.warning(f"Ordering link detection error: {e}")
            return []
    
    @classmethod
    async def _check_platform_availability(
        cls, 
        website_url: str
    ) -> List[str]:
        """
        Check for third-party ordering platform links.
        
        Args:
            website_url (str): Restaurant website URL
        
        Returns:
            List[str]: Detected ordering platforms
        """
        try:
            async with browser_manager.get_page() as page:
                await page.goto(website_url, timeout=15000)
                
                # Look for third-party platform links
                platform_links = await page.evaluate(f'''() => {{
                    const links = Array.from(document.querySelectorAll('a'));
                    const platforms = {cls.ORDERING_PLATFORMS};
                    
                    return links
                        .filter(link => 
                            platforms.some(platform => 
                                link.href.toLowerCase().includes(platform)
                            )
                        )
                        .map(link => link.href);
                }}''')
                
                return platform_links
        
        except Exception as e:
            logging.warning(f"Platform availability check error: {e}")
            return []
    
    @staticmethod
    def _assess_ordering_integration(
        direct_links: List[str], 
        platform_links: List[str]
    ) -> float:
        """
        Assess the quality of online ordering integration.
        
        Args:
            direct_links (List[str]): Direct ordering links
            platform_links (List[str]): Third-party platform links
        
        Returns:
            float: Integration quality score (0-100)
        """
        try:
            # Base score components
            direct_ordering_score = min(len(direct_links) * 20, 50)
            platform_score = min(len(platform_links) * 10, 50)
            
            # Bonus for diverse ordering options
            diversity_bonus = 10 if len(direct_links) > 1 or len(platform_links) > 1 else 0
            
            total_score = direct_ordering_score + platform_score + diversity_bonus
            
            return min(total_score, 100)
        
        except Exception as e:
            logging.warning(f"Integration quality assessment error: {e}")
            return 0.0
    
    @staticmethod
    def _default_ordering_analysis() -> Dict[str, Any]:
        """
        Return a default ordering analysis when detection fails.
        
        Returns:
            Dict[str, Any]: Default ordering analysis structure
        """
        return {
            'online_ordering_available': False,
            'platforms': [],
            'integration_quality': 0.0,
            'direct_ordering_links': [],
            'third_party_platforms': []
        }