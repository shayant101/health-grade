from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
import logging

from ..models.lead import LeadCreate, LeadInDB, LeadStatus
from ..services.email_service import EmailService
from ..database import database

router = APIRouter(prefix="/api/leads", tags=["Leads"])

@router.post("/", response_model=LeadInDB)
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks
) -> LeadInDB:
    """
    Capture a new lead and initiate follow-up process.
    
    Args:
        lead_data (LeadCreate): Lead information
        background_tasks (BackgroundTasks): FastAPI background tasks
    
    Returns:
        LeadInDB: Created lead details
    """
    try:
        # Validate email uniqueness
        existing_lead = await database.find_lead_by_email(lead_data.email)
        if existing_lead:
            raise HTTPException(
                status_code=400, 
                detail="A lead with this email already exists"
            )
        
        # Create lead record
        lead = LeadInDB(
            **lead_data.dict(),
            status=LeadStatus.NEW
        )
        
        # Save lead to database
        await database.create_lead(lead)
        
        # Send confirmation email in background
        background_tasks.add_task(
            _send_lead_confirmation_email, 
            lead
        )
        
        return lead
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lead creation error: {str(e)}"
        )

@router.get("/{lead_id}", response_model=LeadInDB)
async def get_lead_details(
    lead_id: str
) -> LeadInDB:
    """
    Retrieve lead details.
    
    Args:
        lead_id (str): Unique lead identifier
    
    Returns:
        LeadInDB: Detailed lead information
    """
    try:
        lead = await database.get_lead_by_id(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return lead
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lead retrieval error: {str(e)}"
        )

@router.patch("/{lead_id}/status", response_model=LeadInDB)
async def update_lead_status(
    lead_id: str,
    new_status: LeadStatus
) -> LeadInDB:
    """
    Update the status of a lead.
    
    Args:
        lead_id (str): Unique lead identifier
        new_status (LeadStatus): New status for the lead
    
    Returns:
        LeadInDB: Updated lead details
    """
    try:
        # Retrieve existing lead
        lead = await database.get_lead_by_id(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update lead status
        lead.status = new_status
        
        # Save updated lead
        await database.update_lead(lead)
        
        return lead
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lead status update error: {str(e)}"
        )

async def _send_lead_confirmation_email(lead: LeadInDB):
    """
    Send confirmation email to lead.
    
    Args:
        lead (LeadInDB): Lead details
    """
    try:
        email_service = EmailService()
        await email_service.send_lead_confirmation_email(lead)
    
    except Exception as e:
        # Log error but don't raise exception to prevent blocking
        logging.error(f"Lead confirmation email error: {e}")

@router.get("/", response_model=List[LeadInDB])
async def list_leads(
    status: Optional[LeadStatus] = None,
    limit: int = 10,
    offset: int = 0
) -> List[LeadInDB]:
    """
    List leads with optional filtering.
    
    Args:
        status (Optional[LeadStatus]): Filter by lead status
        limit (int): Maximum number of results
        offset (int): Pagination offset
    
    Returns:
        List[LeadInDB]: List of leads
    """
    try:
        leads = await database.list_leads(
            status=status, 
            limit=limit, 
            offset=offset
        )
        
        return leads
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Leads list retrieval error: {str(e)}"
        )