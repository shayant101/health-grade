from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RestaurantCategory(str, Enum):
    """
    Enumeration of restaurant categories for standardized classification.
    """
    FAST_FOOD = "fast_food"
    FINE_DINING = "fine_dining"
    CAFE = "cafe"
    BISTRO = "bistro"
    PIZZA = "pizza"
    SUSHI = "sushi"
    STEAKHOUSE = "steakhouse"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    OTHER = "other"

class GeoLocation(BaseModel):
    """
    Represents geographical coordinates for a restaurant.
    """
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class ContactInfo(BaseModel):
    """
    Contact information for a restaurant.
    """
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{10,14}$')
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

class RestaurantBase(BaseModel):
    """
    Base model for restaurant information.
    """
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=200)
    category: RestaurantCategory = RestaurantCategory.OTHER
    geo_location: Optional[GeoLocation] = None
    contact_info: Optional[ContactInfo] = None

class RestaurantCreate(RestaurantBase):
    """
    Model for creating a new restaurant entry.
    """
    @validator('name')
    def validate_name(cls, v):
        """
        Validate restaurant name to prevent empty or overly generic names.
        """
        if len(v.strip()) < 2:
            raise ValueError('Restaurant name must be at least 2 characters long')
        return v.strip()

class RestaurantInDB(RestaurantBase):
    """
    Model representing a restaurant stored in the database.
    """
    id: str = Field(alias='_id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """
        Pydantic configuration for database model.
        """
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RestaurantSearchResult(RestaurantInDB):
    """
    Model for search results, potentially with additional scoring or relevance information.
    """
    relevance_score: Optional[float] = Field(None, ge=0, le=100)
    matched_keywords: Optional[List[str]] = None