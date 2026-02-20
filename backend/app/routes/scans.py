from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..database import create_scan, get_scan_by_id, list_scans
from ..services.scan_orchestrator import run_restaurant_scan

router = APIRouter()

class ScanCreate(BaseModel):
    restaurant_name: str
    restaurant_website: str
    restaurant_data: Optional[dict] = {}

@router.post("/")
async def create_new_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks
):
    """Create a new restaurant scan and start analysis in background"""
    try:
        # Create scan record
        scan = await create_scan({
            "restaurant_name": scan_data.restaurant_name,
            "restaurant_website": scan_data.restaurant_website,
            "status": "pending",
            "created_at": datetime.utcnow()
        })
        
        # Prepare restaurant data for analysis
        restaurant_data = {
            "name": scan_data.restaurant_name,
            "website": scan_data.restaurant_website,
            **scan_data.restaurant_data
        }
        
        # Trigger background scan
        background_tasks.add_task(
            run_restaurant_scan,
            scan["_id"],
            restaurant_data
        )
        
        return {
            "scan_id": scan["_id"],
            "status": "pending",
            "message": "Scan started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scan_id}")
async def get_scan(scan_id: str):
    """Get scan results by ID"""
    scan = await get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/")
async def get_scans(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """List all scans with optional filtering"""
    scans = await list_scans(skip=skip, limit=limit, status=status)
    return {"scans": scans, "count": len(scans)}
