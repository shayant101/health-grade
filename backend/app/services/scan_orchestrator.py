import asyncio
from datetime import datetime
from typing import Dict, Any
from ..database import update_scan
from ..core.browser import BrowserManager
from ..core.scoring import RestaurantScorer
from ..utils.logger import logger

async def run_restaurant_scan(scan_id: str, restaurant_data: dict):
    """
    Orchestrates complete restaurant scan workflow
    Runs in background via FastAPI BackgroundTasks
    """
    try:
        logger.info(f"Starting scan {scan_id} for {restaurant_data.get('name')}")
        
        # Update status to in_progress
        await update_scan(scan_id, {
            "status": "in_progress",
            "started_at": datetime.utcnow()
        })
        
        # Run website analysis (browser automation)
        website_url = restaurant_data.get("website", "")
        website_data = {}
        if website_url:
            logger.info(f"Analyzing website: {website_url}")
            async with BrowserManager() as browser:
                website_data = await browser.analyze_website(website_url)
        
        # Mock other analyzers for now (Phase 5 will add real APIs)
        google_data = {
            "has_photos": True,
            "has_hours": True,
            "has_description": True,
            "is_verified": True,
            "response_rate": 0.8,
            "posts_per_month": 4
        }
        
        reviews_data = {
            "average_rating": 4.2,
            "total_reviews": 150,
            "recent_reviews_count": 30,
            "positive_sentiment": 0.75
        }
        
        ordering_data = {
            "has_ordering": website_data.get("order_button", {}).get("found", False),
            "platforms_count": len(website_data.get("order_button", {}).get("platforms", [])),
            "has_direct_ordering": website_data.get("order_button", {}).get("found", False),
            "order_button_found": website_data.get("order_button", {}).get("found", False)
        }
        
        # Calculate scores
        scorer = RestaurantScorer()
        
        website_score = scorer.calculate_website_score(website_data)
        google_score = scorer.calculate_google_score(google_data)
        reviews_score = scorer.calculate_reviews_score(reviews_data)
        ordering_score = scorer.calculate_ordering_score(ordering_data)
        
        overall_scores = scorer.calculate_overall_score({
            "website": website_score,
            "google": google_score,
            "reviews": reviews_score,
            "ordering": ordering_score
        })
        
        # Update scan with results
        await update_scan(scan_id, {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "overall_score": overall_scores['overall_score'],  # Flatten for frontend
            "letter_grade": overall_scores['letter_grade'],
            "results": overall_scores,  # Keep full results for reference
            "analysis_data": {
                "website": website_data,
                "google": google_data,
                "reviews": reviews_data,
                "ordering": ordering_data
            }
        })
        
        logger.info(f"Scan {scan_id} completed successfully. Score: {overall_scores['overall_score']}")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {str(e)}")
        await update_scan(scan_id, {
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow()
        })

# Legacy class-based orchestrator (kept for backward compatibility)
import logging
from typing import Dict, Any, Optional

from ..models.restaurant import RestaurantCreate
from ..models.scan import ScanStatus, ScanInDB
from .restaurant_search import RestaurantSearchService
from .website_analyzer import WebsiteAnalyzer
from .google_analyzer import GoogleBusinessAnalyzer
from .reviews_analyzer import ReviewsAnalyzer
from .ordering_analyzer import OrderingAnalyzer

class ScanOrchestrator:
    """
    Coordinates the entire restaurant scanning process.
    Manages the workflow of collecting and analyzing restaurant data from multiple sources.
    """
    
    @classmethod
    async def perform_comprehensive_scan(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Perform a comprehensive scan of a restaurant across multiple dimensions.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to scan
        
        Returns:
            Dict[str, Any]: Comprehensive scan results
        """
        try:
            # Validate input
            if not restaurant.contact_info or not restaurant.contact_info.website:
                logging.warning("No website provided for scanning")
                return cls._empty_scan_result(restaurant)
            
            # Parallel analysis of different aspects
            tasks = [
                cls._analyze_website(restaurant),
                cls._analyze_google_business(restaurant),
                cls._analyze_reviews(restaurant),
                cls._analyze_ordering(restaurant)
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            
            # Combine results
            scan_result = {
                'website_analysis': results[0],
                'google_business_analysis': results[1],
                'reviews_analysis': results[2],
                'ordering_analysis': results[3]
            }
            
            # Calculate comprehensive score
            scan_result['comprehensive_score'] = RestaurantScorer.calculate_comprehensive_score(
                website_data=scan_result['website_analysis'],
                google_data=scan_result['google_business_analysis'],
                reviews_data=scan_result['reviews_analysis'],
                ordering_data=scan_result['ordering_analysis']
            )
            
            return scan_result
        
        except Exception as e:
            logging.error(f"Comprehensive scan error: {e}")
            return cls._empty_scan_result(restaurant)
    
    @classmethod
    async def _analyze_website(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Analyze restaurant's website.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to analyze
        
        Returns:
            Dict[str, Any]: Website analysis results
        """
        try:
            website_url = restaurant.contact_info.website
            return await WebsiteAnalyzer.analyze_website(website_url)
        
        except Exception as e:
            logging.warning(f"Website analysis error: {e}")
            return {}
    
    @classmethod
    async def _analyze_google_business(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Analyze Google Business Profile.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to analyze
        
        Returns:
            Dict[str, Any]: Google Business analysis results
        """
        try:
            return await GoogleBusinessAnalyzer.get_business_profile(restaurant)
        
        except Exception as e:
            logging.warning(f"Google Business analysis error: {e}")
            return {}
    
    @classmethod
    async def _analyze_reviews(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Analyze restaurant reviews.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to analyze
        
        Returns:
            Dict[str, Any]: Reviews analysis results
        """
        try:
            # Fetch reviews from multiple sources
            reviews = await ReviewsAnalyzer.fetch_reviews(restaurant.id)
            return await ReviewsAnalyzer.analyze_reviews(reviews)
        
        except Exception as e:
            logging.warning(f"Reviews analysis error: {e}")
            return {}
    
    @classmethod
    async def _analyze_ordering(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Analyze online ordering capabilities.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to analyze
        
        Returns:
            Dict[str, Any]: Ordering analysis results
        """
        try:
            website_url = restaurant.contact_info.website
            return await OrderingAnalyzer.analyze_ordering_capabilities(website_url)
        
        except Exception as e:
            logging.warning(f"Ordering analysis error: {e}")
            return {}
    
    @staticmethod
    def _empty_scan_result(
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Generate an empty scan result when analysis fails.
        
        Args:
            restaurant (RestaurantCreate): Restaurant details
        
        Returns:
            Dict[str, Any]: Empty scan result structure
        """
        return {
            'restaurant_id': restaurant.id,
            'status': ScanStatus.FAILED,
            'website_analysis': {},
            'google_business_analysis': {},
            'reviews_analysis': {},
            'ordering_analysis': {},
            'comprehensive_score': 0.0
        }
    
    @classmethod
    async def update_scan_status(
        cls, 
        scan: ScanInDB, 
        status: ScanStatus
    ) -> ScanInDB:
        """
        Update the status of an ongoing scan.
        
        Args:
            scan (ScanInDB): Scan to update
            status (ScanStatus): New scan status
        
        Returns:
            ScanInDB: Updated scan object
        """
        try:
            # In a real implementation, this would update the database
            scan.status = status
            return scan
        
        except Exception as e:
            logging.error(f"Scan status update error: {e}")
            return scan