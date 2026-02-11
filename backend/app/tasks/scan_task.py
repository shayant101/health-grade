import logging
from typing import Dict, Any

from celery import shared_task
from celery.signals import task_success, task_failure

from ..services.restaurant_search import RestaurantSearchService
from ..services.scan_orchestrator import ScanOrchestrator
from ..services.email_service import EmailService
from ..services.ai_narrative import AInarrative
from ..services.evidence_storage import EvidenceStorageService
from ..models.restaurant import RestaurantCreate
from ..models.scan import ScanStatus, ScanInDB
from ..database import database

@shared_task(
    bind=True, 
    max_retries=3, 
    default_retry_delay=60,
    queue='scan_queue'
)
def perform_restaurant_scan(
    self, 
    restaurant_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Celery task for performing comprehensive restaurant scan.
    
    Args:
        restaurant_data (Dict[str, Any]): Restaurant details for scanning
    
    Returns:
        Dict[str, Any]: Scan results
    """
    try:
        # Convert dict to RestaurantCreate model
        restaurant = RestaurantCreate(**restaurant_data)
        
        # Perform comprehensive scan
        scan_result = ScanOrchestrator.perform_comprehensive_scan(restaurant)
        
        # Generate AI narrative
        ai_narrative = AInarrative().generate_narrative(scan_result)
        scan_result['ai_narrative'] = ai_narrative
        
        # Store evidence
        evidence_storage = EvidenceStorageService()
        evidence_result = evidence_storage.store_scan_evidence(
            scan_id=scan_result['id'], 
            evidence_data=scan_result
        )
        scan_result['evidence_urls'] = [
            evidence['url'] for evidence in evidence_result
        ]
        
        return scan_result
    
    except Exception as e:
        # Log error and retry
        logging.error(f"Restaurant scan error: {e}")
        raise self.retry(exc=e)

@task_success.connect(sender=perform_restaurant_scan)
def handle_scan_success(sender, result, **kwargs):
    """
    Handle successful scan task.
    Send results via email and update database.
    
    Args:
        result (Dict[str, Any]): Scan results
    """
    try:
        # Send email with results
        email_service = EmailService()
        email_service.send_scan_results_email(
            email=result.get('contact_email', ''),
            restaurant_name=result.get('restaurant_name', 'Unknown Restaurant'),
            scan_results=result
        )
        
        # Update scan status in database
        # Note: This would typically use an async database method
        database.update_scan_status(
            scan_id=result['id'], 
            status=ScanStatus.COMPLETED
        )
    
    except Exception as e:
        logging.error(f"Scan success handler error: {e}")

@task_failure.connect(sender=perform_restaurant_scan)
def handle_scan_failure(sender, exception, traceback, **kwargs):
    """
    Handle failed scan task.
    Log error and send failure notification.
    
    Args:
        exception (Exception): Task failure exception
        traceback (str): Traceback information
    """
    try:
        # Log detailed error
        logging.error(
            f"Restaurant scan task failed: {exception}\n{traceback}"
        )
        
        # Send error notification
        email_service = EmailService()
        email_service.send_error_notification(
            error_message=str(exception),
            traceback=traceback
        )
        
        # Update scan status in database
        # Note: This would typically use an async database method
        database.update_scan_status(
            scan_id=kwargs.get('scan_id', 'unknown'), 
            status=ScanStatus.FAILED
        )
    
    except Exception as e:
        logging.error(f"Scan failure handler error: {e}")

@shared_task
def cleanup_old_scans(days_old: int = 30):
    """
    Periodic task to clean up old scan records.
    
    Args:
        days_old (int): Number of days after which scans should be deleted
    """
    try:
        # Note: This would use an async database method in a real implementation
        database.delete_old_scans(days_old)
        logging.info(f"Cleaned up scans older than {days_old} days")
    
    except Exception as e:
        logging.error(f"Scan cleanup error: {e}")

# Commented out periodic task configuration
# perform_restaurant_scan.apply_async() should only be called with specific restaurant data