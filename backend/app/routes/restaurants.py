from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..services.restaurant_search import RestaurantSearchService
from ..models.restaurant import RestaurantCreate, RestaurantSearchResult, GeoLocation

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])

@router.post("/search", response_model=List[RestaurantSearchResult])
async def search_restaurants(
    query: str = Query(..., min_length=2, max_length=100),
    location: Optional[GeoLocation] = None,
    radius: int = Query(5000, ge=1000, le=50000)
) -> List[RestaurantSearchResult]:
    """
    Search for restaurants based on query and optional location.
    
    Args:
        query (str): Search query for restaurants
        location (Optional[GeoLocation]): Geographical location to center search
        radius (int): Search radius in meters (default: 5000m)
    
    Returns:
        List[RestaurantSearchResult]: List of matching restaurants
    """
    try:
        # Perform search using multiple sources
        google_results = await RestaurantSearchService.search_google_places(
            query, 
            location, 
            radius
        )
        
        overpass_results = await RestaurantSearchService.search_overpass(
            query, 
            location, 
            radius
        )
        
        # Combine and deduplicate results
        combined_results = _deduplicate_results(google_results + overpass_results)
        
        return combined_results
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Restaurant search error: {str(e)}"
        )

def _deduplicate_results(
    results: List[RestaurantCreate]
) -> List[RestaurantSearchResult]:
    """
    Deduplicate restaurant search results.
    
    Args:
        results (List[RestaurantCreate]): List of restaurant results
    
    Returns:
        List[RestaurantSearchResult]: Deduplicated and scored results
    """
    # Use a dictionary to track unique restaurants
    unique_restaurants = {}
    
    for restaurant in results:
        # Create a unique key based on name and address
        key = f"{restaurant.name.lower()}_{restaurant.address.lower()}"
        
        # Add or update restaurant in unique dictionary
        if key not in unique_restaurants:
            unique_restaurants[key] = restaurant
    
    # Convert to search results with relevance scoring
    search_results = []
    for i, restaurant in enumerate(unique_restaurants.values(), 1):
        search_result = RestaurantSearchResult(
            **restaurant.dict(),
            relevance_score=100 - (i * 5),  # Simple relevance scoring
            matched_keywords=[restaurant.name, restaurant.category]
        )
        search_results.append(search_result)
    
    # Sort by relevance score
    return sorted(
        search_results, 
        key=lambda r: r.relevance_score or 0, 
        reverse=True
    )