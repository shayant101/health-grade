from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LeadSource(str, Enum):
    """
    Enumeration of possible lead sources.
    """
    WEBSITE = "website"
    SCAN_RESULT = "scan_result"
    DIRECT_CONTACT = "direct_contact"
    REFERRAL = "referral"
    MARKETING_CAMPAIGN = "marketing_campaign"
    OTHER = "other"

class LeadStatus(str, Enum):
    """
    Enumeration of lead processing statuses.
    """
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    UNQUALIFIED = "unqualified"

class LeadBase(BaseModel):
    """
    Base model for lead information.
    """
    email: EmailStr
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    restaurant_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{10,14}$')
    source: LeadSource = LeadSource.OTHER

class LeadCreate(LeadBase):
    """
    Model for creating a new lead entry.
    """
    @validator('name')
    def validate_name(cls, v):
        """
        Validate lead name if provided.
        """
        if v and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v

class LeadInDB(LeadBase):
    """
    Model representing a lead stored in the database.
    """
    id: str = Field(alias='_id')
    
    # Lead tracking and processing
    status: LeadStatus = LeadStatus.NEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Associated scan or restaurant if applicable
    associated_scan_id: Optional[str] = None
    associated_restaurant_id: Optional[str] = None
    
    # Additional metadata and tracking
    metadata: Optional[Dict[str, Any]] = None
    
    # Marketing and communication tracking
    last_contacted_at: Optional[datetime] = None
    communication_log: Optional[List[Dict[str, Any]]] = None

    class Config:
        """
        Pydantic configuration for database model.
        """
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LeadSummary(BaseModel):
    """
    Lightweight summary of a lead for listing or quick overview.
    """
    id: str
    name: Optional[str]
    email: EmailStr
    status: LeadStatus
    source: LeadSource
    created_at: datetime
    restaurant_name: Optional[str] = None