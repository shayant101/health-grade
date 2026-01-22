from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum, auto

class ScanStatus(str, Enum):
    """
    Enumeration of possible scan statuses.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class ScanCategory(str, Enum):
    """
    Categories of scans performed on a restaurant.
    """
    WEBSITE = "website"
    GOOGLE_BUSINESS = "google_business"
    REVIEWS = "reviews"
    ORDERING = "ordering"
    COMPREHENSIVE = "comprehensive"

class WebsiteAnalysis(BaseModel):
    """
    Detailed analysis of a restaurant's website.
    """
    url: Optional[HttpUrl] = None
    performance_score: Optional[float] = Field(None, ge=0, le=100)
    mobile_friendly: Optional[bool] = None
    https_enabled: Optional[bool] = None
    loading_time_ms: Optional[int] = None
    evidence_urls: List[HttpUrl] = []

class GoogleBusinessAnalysis(BaseModel):
    """
    Analysis of Google Business Profile.
    """
    profile_exists: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = None
    photos_count: Optional[int] = None
    posts_frequency: Optional[str] = None

class ReviewsAnalysis(BaseModel):
    """
    Comprehensive review analysis.
    """
    total_reviews: Optional[int] = None
    average_rating: Optional[float] = Field(None, ge=0, le=5)
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    key_themes: List[str] = []

class OrderingAnalysis(BaseModel):
    """
    Online ordering capabilities analysis.
    """
    online_ordering_available: Optional[bool] = None
    platforms: List[str] = []
    integration_quality: Optional[float] = Field(None, ge=0, le=100)

class ScanBase(BaseModel):
    """
    Base model for restaurant scans.
    """
    restaurant_id: str
    category: ScanCategory = ScanCategory.COMPREHENSIVE
    status: ScanStatus = ScanStatus.PENDING

class ScanCreate(ScanBase):
    """
    Model for initiating a new scan.
    """
    pass

class ScanInDB(ScanBase):
    """
    Model representing a scan stored in the database.
    """
    id: str = Field(alias='_id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Detailed analysis results
    website_analysis: Optional[WebsiteAnalysis] = None
    google_business_analysis: Optional[GoogleBusinessAnalysis] = None
    reviews_analysis: Optional[ReviewsAnalysis] = None
    ordering_analysis: Optional[OrderingAnalysis] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    # Evidence storage
    evidence_urls: List[HttpUrl] = []
    
    # AI-generated narrative
    ai_narrative: Optional[str] = None

    class Config:
        """
        Pydantic configuration for database model.
        """
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScanSummary(BaseModel):
    """
    Lightweight summary of a scan for listing or quick overview.
    """
    id: str
    restaurant_id: str
    category: ScanCategory
    status: ScanStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = Field(None, ge=0, le=100)