from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any

from ..models.scan import ScanCreate, ScanInDB, ScanSummary, ScanStatus
from ..models.restaurant import RestaurantCreate
from ..services.scan_orchestrator import ScanOrchestrator
from ..tasks.scan_task import perform_restaurant_scan
from ..services.evidence_storage import EvidenceStorageService
from ..database import database

router = APIRouter(prefix="/api/scans", tags=["Scans"])

@router.post("/", response_model=ScanInDB)
async def create_scan(
    scan_data: ScanCreate, 
    background_tasks: BackgroundTasks
) -> ScanInDB:
    """
    Create a new restaurant scan.
    
    Args:
        scan_data (ScanCreate): Scan creation details
        background_tasks (BackgroundTasks): FastAPI background tasks
    
    Returns:
        ScanInDB: Created scan details
    """
    try:
        # Validate and prepare restaurant data
        restaurant = RestaurantCreate(**scan_data.dict())
        
        # Create initial scan record
        scan = ScanInDB(
            restaurant_id=restaurant.id,
            category=scan_data.category,
            status=ScanStatus.PENDING
        )
        
        # Enqueue scan task
        background_tasks.add_task(
            perform_restaurant_scan.delay, 
            restaurant_data=restaurant.dict()
        )
        
        return scan
    
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Scan creation error: {str(e)}"
        )

@router.get("/{scan_id}", response_model=ScanInDB)
async def get_scan_details(
    scan_id: str
) -> ScanInDB:
    """
    Retrieve detailed scan results.
    
    Args:
        scan_id (str): Unique scan identifier
    
    Returns:
        ScanInDB: Detailed scan information
    """
    try:
        # Retrieve scan details from database
        # Note: In a real implementation, this would use an async database method
        scan = await database.get_scan_by_id(scan_id)
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return scan
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Scan retrieval error: {str(e)}"
        )

@router.get("/", response_model=List[ScanSummary])
async def list_scans(
    status: Optional[ScanStatus] = None,
    limit: int = 10,
    offset: int = 0
) -> List[ScanSummary]:
    """
    List recent scans with optional filtering.
    
    Args:
        status (Optional[ScanStatus]): Filter by scan status
        limit (int): Maximum number of results
        offset (int): Pagination offset
    
    Returns:
        List[ScanSummary]: List of scan summaries
    """
    try:
        # Retrieve scan summaries from database
        # Note: In a real implementation, this would use an async database method
        scans = await database.list_scans(
            status=status, 
            limit=limit, 
            offset=offset
        )
        
        return scans
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Scan list retrieval error: {str(e)}"
        )

@router.get("/{scan_id}/evidence", response_model=List[Dict[str, Any]])
async def get_scan_evidence(
    scan_id: str
) -> List[Dict[str, Any]]:
    """
    Retrieve evidence files for a specific scan.
    
    Args:
        scan_id (str): Unique scan identifier
    
    Returns:
        List[Dict[str, Any]]: List of evidence file details
    """
    try:
        # Use evidence storage service to list evidence
        evidence_storage = EvidenceStorageService()
        evidence_list = await evidence_storage.list_evidence(scan_id)
        
        return evidence_list
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Evidence retrieval error: {str(e)}"
        )

@router.post("/{scan_id}/retry", response_model=ScanInDB)
async def retry_scan(
    scan_id: str, 
    background_tasks: BackgroundTasks
) -> ScanInDB:
    """
    Retry a failed scan.
    
    Args:
        scan_id (str): Unique scan identifier
        background_tasks (BackgroundTasks): FastAPI background tasks
    
    Returns:
        ScanInDB: Updated scan details
    """
    try:
        # Retrieve original scan details
        original_scan = await database.get_scan_by_id(scan_id)
        
        if not original_scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Retrieve associated restaurant
        restaurant = await database.get_restaurant_by_id(original_scan.restaurant_id)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Associated restaurant not found")
        
        # Create new scan record
        new_scan = ScanInDB(
            restaurant_id=restaurant.id,
            category=original_scan.category,
            status=ScanStatus.PENDING
        )
        
        # Enqueue scan task
        background_tasks.add_task(
            perform_restaurant_scan.delay, 
            restaurant_data=restaurant.dict()
        )
        
        return new_scan
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Scan retry error: {str(e)}"
        )