import httpx
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import quote_plus

from ..config import settings
from ..models.restaurant import RestaurantCreate, GeoLocation

class GoogleBusinessAnalyzer:
    """
    Service for analyzing Google Business Profile information.
    Provides detailed insights about restaurants from Google's API.
    """
    
    GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    GOOGLE_PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    @classmethod
    async def get_business_profile(
        cls, 
        restaurant: RestaurantCreate
    ) -> Dict[str, Any]:
        """
        Retrieve detailed Google Business Profile information.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to analyze
        
        Returns:
            Dict[str, Any]: Detailed Google Business Profile analysis
        """
        try:
            # First, search for the place to get place_id
            place_id = await cls._find_place_id(restaurant)
            
            if not place_id:
                return {}
            
            # Then get detailed information
            async with httpx.AsyncClient() as client:
                params = {
                    'place_id': place_id,
                    'key': settings.GOOGLE_PLACES_API_KEY,
                    'fields': ','.join([
                        'name', 
                        'rating', 
                        'user_ratings_total', 
                        'formatted_phone_number',
                        'website', 
                        'opening_hours', 
                        'photos',
                        'reviews'
                    ])
                }
                
                response = await client.get(cls.GOOGLE_PLACES_DETAILS_URL, params=params)
                response.raise_for_status()
                
                data = response.json().get('result', {})
                
                return {
                    'profile_exists': True,
                    'name': data.get('name'),
                    'rating': data.get('rating'),
                    'review_count': data.get('user_ratings_total', 0),
                    'phone': data.get('formatted_phone_number'),
                    'website': data.get('website'),
                    'photos_count': len(data.get('photos', [])),
                    'is_open_now': cls._check_open_status(data.get('opening_hours', {})),
                    'recent_reviews': cls._extract_recent_reviews(data.get('reviews', []))
                }
        
        except Exception as e:
            logging.error(f"Google Business Profile analysis error: {e}")
            return {}
    
    @classmethod
    async def _find_place_id(
        cls, 
        restaurant: RestaurantCreate
    ) -> Optional[str]:
        """
        Find the Google Places place_id for a restaurant.
        
        Args:
            restaurant (RestaurantCreate): Restaurant to search
        
        Returns:
            Optional[str]: Place ID if found
        """
        try:
            async with httpx.AsyncClient() as client:
                # Construct search query
                query = f"{restaurant.name} {restaurant.address}"
                
                params = {
                    'query': quote_plus(query),
                    'key': settings.GOOGLE_PLACES_API_KEY
                }
                
                # Add location if available
                if restaurant.geo_location:
                    params['location'] = (
                        f"{restaurant.geo_location.latitude},"
                        f"{restaurant.geo_location.longitude}"
                    )
                    params['radius'] = 5000  # 5 km search radius
                
                response = await client.get(cls.GOOGLE_PLACES_SEARCH_URL, params=params)
                response.raise_for_status()
                
                results = response.json().get('results', [])
                
                # Return the first place_id if found
                return results[0].get('place_id') if results else None
        
        except Exception as e:
            logging.error(f"Place ID search error: {e}")
            return None
    
    @staticmethod
    def _check_open_status(opening_hours: Dict[str, Any]) -> Optional[bool]:
        """
        Check if a business is currently open.
        
        Args:
            opening_hours (Dict[str, Any]): Opening hours data
        
        Returns:
            Optional[bool]: Open status or None if unavailable
        """
        try:
            return opening_hours.get('open_now')
        except Exception:
            return None
    
    @staticmethod
    def _extract_recent_reviews(
        reviews: List[Dict[str, Any]], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract recent reviews with key information.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews
            limit (int): Maximum number of reviews to extract
        
        Returns:
            List[Dict[str, Any]]: Processed recent reviews
        """
        try:
            # Sort reviews by time (most recent first)
            sorted_reviews = sorted(
                reviews, 
                key=lambda r: r.get('time', 0), 
                reverse=True
            )
            
            # Extract key review information
            return [
                {
                    'rating': review.get('rating'),
                    'text': review.get('text', ''),
                    'time': review.get('time')
                }
                for review in sorted_reviews[:limit]
            ]
        
        except Exception as e:
            logging.warning(f"Review extraction error: {e}")
            return []