import httpx
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from ..config import settings
from ..models.restaurant import RestaurantCreate, RestaurantCategory, GeoLocation

class RestaurantSearchService:
    """
    Service for searching restaurants using multiple sources:
    - Google Places API
    - Overpass API (OpenStreetMap)
    """
    
    GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"
    
    @classmethod
    async def search_google_places(
        cls, 
        query: str, 
        location: Optional[GeoLocation] = None, 
        radius: int = 5000
    ) -> List[RestaurantCreate]:
        """
        Search for restaurants using Google Places API.
        
        Args:
            query (str): Search query (e.g., "restaurants in San Francisco")
            location (Optional[GeoLocation]): Geographical location to center search
            radius (int): Search radius in meters
        
        Returns:
            List[RestaurantCreate]: List of found restaurants
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'query': quote_plus(query),
                    'key': settings.GOOGLE_PLACES_API_KEY,
                    'type': 'restaurant'
                }
                
                # Add location if provided
                if location:
                    params['location'] = f"{location.latitude},{location.longitude}"
                    params['radius'] = radius
                
                response = await client.get(cls.GOOGLE_PLACES_BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                restaurants = []
                
                for result in data.get('results', []):
                    try:
                        restaurant = RestaurantCreate(
                            name=result.get('name', ''),
                            address=result.get('formatted_address', ''),
                            category=cls._map_google_type(result.get('types', [])),
                            geo_location=GeoLocation(
                                latitude=result.get('geometry', {}).get('location', {}).get('lat', 0),
                                longitude=result.get('geometry', {}).get('location', {}).get('lng', 0)
                            ),
                            contact_info={
                                'phone': result.get('international_phone_number')
                            }
                        )
                        restaurants.append(restaurant)
                    except Exception as e:
                        logging.warning(f"Could not parse restaurant: {e}")
                
                return restaurants
        
        except Exception as e:
            logging.error(f"Google Places search error: {e}")
            return []
    
    @classmethod
    async def search_overpass(
        cls, 
        query: str, 
        location: Optional[GeoLocation] = None, 
        radius: int = 5000
    ) -> List[RestaurantCreate]:
        """
        Search for restaurants using Overpass API (OpenStreetMap).
        
        Args:
            query (str): Search query
            location (Optional[GeoLocation]): Geographical location to center search
            radius (int): Search radius in meters
        
        Returns:
            List[RestaurantCreate]: List of found restaurants
        """
        try:
            async with httpx.AsyncClient() as client:
                # Construct Overpass QL query
                if location:
                    overpass_query = f"""
                    [out:json][timeout:25];
                    (
                      node["amenity"="restaurant"]
                        (around:{radius},{location.latitude},{location.longitude});
                      way["amenity"="restaurant"]
                        (around:{radius},{location.latitude},{location.longitude});
                      relation["amenity"="restaurant"]
                        (around:{radius},{location.latitude},{location.longitude});
                    );
                    out center;
                    """
                else:
                    overpass_query = f"""
                    [out:json][timeout:25];
                    (
                      node["amenity"="restaurant"]["name"~"{quote_plus(query)}",i];
                      way["amenity"="restaurant"]["name"~"{quote_plus(query)}",i];
                      relation["amenity"="restaurant"]["name"~"{quote_plus(query)}",i];
                    );
                    out center;
                    """
                
                response = await client.post(
                    cls.OVERPASS_BASE_URL, 
                    data={'data': overpass_query}
                )
                response.raise_for_status()
                
                data = response.json()
                restaurants = []
                
                for element in data.get('elements', []):
                    try:
                        restaurant = RestaurantCreate(
                            name=element.get('tags', {}).get('name', ''),
                            address=cls._build_overpass_address(element),
                            category=cls._map_osm_type(element.get('tags', {})),
                            geo_location=GeoLocation(
                                latitude=element.get('lat', 0),
                                longitude=element.get('lon', 0)
                            )
                        )
                        restaurants.append(restaurant)
                    except Exception as e:
                        logging.warning(f"Could not parse Overpass restaurant: {e}")
                
                return restaurants
        
        except Exception as e:
            logging.error(f"Overpass search error: {e}")
            return []
    
    @staticmethod
    def _map_google_type(types: List[str]) -> RestaurantCategory:
        """
        Map Google Places types to RestaurantCategory.
        
        Args:
            types (List[str]): Google Places types
        
        Returns:
            RestaurantCategory: Mapped restaurant category
        """
        type_mapping = {
            'fast_food': RestaurantCategory.FAST_FOOD,
            'cafe': RestaurantCategory.CAFE,
            'bar': RestaurantCategory.BISTRO,
            'pizza': RestaurantCategory.PIZZA,
            'sushi': RestaurantCategory.SUSHI,
            'steakhouse': RestaurantCategory.STEAKHOUSE,
            'vegetarian': RestaurantCategory.VEGETARIAN,
            'vegan': RestaurantCategory.VEGAN
        }
        
        for type_key, category in type_mapping.items():
            if any(type_key in t.lower() for t in types):
                return category
        
        return RestaurantCategory.OTHER
    
    @staticmethod
    def _map_osm_type(tags: Dict[str, str]) -> RestaurantCategory:
        """
        Map OpenStreetMap tags to RestaurantCategory.
        
        Args:
            tags (Dict[str, str]): OpenStreetMap tags
        
        Returns:
            RestaurantCategory: Mapped restaurant category
        """
        cuisine = tags.get('cuisine', '').lower()
        type_mapping = {
            'fast_food': RestaurantCategory.FAST_FOOD,
            'pizza': RestaurantCategory.PIZZA,
            'sushi': RestaurantCategory.SUSHI,
            'steak': RestaurantCategory.STEAKHOUSE,
            'vegetarian': RestaurantCategory.VEGETARIAN,
            'vegan': RestaurantCategory.VEGAN,
            'cafe': RestaurantCategory.CAFE
        }
        
        for type_key, category in type_mapping.items():
            if type_key in cuisine:
                return category
        
        return RestaurantCategory.OTHER
    
    @staticmethod
    def _build_overpass_address(element: Dict[str, Any]) -> str:
        """
        Build an address from Overpass API element tags.
        
        Args:
            element (Dict[str, Any]): Overpass API element
        
        Returns:
            str: Constructed address
        """
        tags = element.get('tags', {})
        address_parts = [
            tags.get('addr:street', ''),
            tags.get('addr:housenumber', ''),
            tags.get('addr:city', ''),
            tags.get('addr:postcode', '')
        ]
        
        return ' '.join(filter(bool, address_parts)).strip() or 'Address not available'