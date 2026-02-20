from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
import logging
import re

from ..database import create_scan, update_scan
from ..services.website_analyzer import WebsiteAnalyzer
from ..core.scoring import RestaurantScorer

logger = logging.getLogger(__name__)

router = APIRouter()

class WebsiteAnalyzeRequest(BaseModel):
    """Request model for website-only analysis"""
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        """Validate and normalize URL"""
        if not v:
            raise ValueError('URL is required')
        
        # Strip whitespace
        v = v.strip()
        
        # Add https:// if no scheme provided
        parsed = urlparse(v)
        if not parsed.scheme:
            v = f"https://{v}"
            parsed = urlparse(v)
        
        # Validate URL format
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format. Please provide a valid website URL.')
        
        # Validate scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValueError('URL must use http or https protocol.')
        
        # Validate domain format (basic check)
        domain = parsed.netloc
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Check for valid domain format (at least one dot, valid characters)
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', domain):
            raise ValueError('Invalid domain format. Please provide a valid website URL.')
        
        return v

class WebsiteRecommendation(BaseModel):
    """Individual recommendation for website improvement"""
    category: str
    priority: str  # "high", "medium", "low"
    title: str
    description: str

class WebsiteAnalyzeResponse(BaseModel):
    """Response model for website-only analysis"""
    scan_id: str
    url: str
    website_score: float
    status: str
    analysis_data: Dict[str, Any]
    recommendations: List[WebsiteRecommendation]
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def generate_recommendations(analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate actionable recommendations based on website analysis.
    
    Args:
        analysis_data: Website analysis results
    
    Returns:
        List of recommendations with priority and actionable advice
    """
    recommendations = []
    
    # SSL/HTTPS Check
    if not analysis_data.get('https_enabled', False):
        recommendations.append({
            "category": "Security",
            "priority": "high",
            "title": "Enable HTTPS",
            "description": "Your website is not using HTTPS. Enable SSL/TLS to secure customer data and improve SEO rankings. Most hosting providers offer free SSL certificates."
        })
    
    # Mobile Friendliness
    if not analysis_data.get('mobile_friendly', False):
        recommendations.append({
            "category": "Mobile Experience",
            "priority": "high",
            "title": "Optimize for Mobile Devices",
            "description": "Your website is not mobile-friendly. Over 60% of restaurant searches happen on mobile. Implement responsive design to improve customer experience."
        })
    
    # Performance Score
    performance_score = analysis_data.get('performance_score', 0)
    if performance_score < 50:
        recommendations.append({
            "category": "Performance",
            "priority": "high",
            "title": "Improve Website Speed",
            "description": f"Your website performance score is {performance_score:.0f}/100. Slow websites lose customers. Optimize images, enable caching, and minimize code to improve loading times."
        })
    elif performance_score < 75:
        recommendations.append({
            "category": "Performance",
            "priority": "medium",
            "title": "Enhance Website Performance",
            "description": f"Your website performance score is {performance_score:.0f}/100. Consider optimizing images and enabling browser caching for faster load times."
        })
    
    # Loading Time
    loading_time_ms = analysis_data.get('loading_time_ms', 0)
    if loading_time_ms > 5000:
        recommendations.append({
            "category": "Performance",
            "priority": "high",
            "title": "Reduce Page Load Time",
            "description": f"Your page takes {loading_time_ms/1000:.1f} seconds to become interactive. Pages that load in under 3 seconds have significantly better conversion rates. Optimize images, reduce JavaScript, and enable compression."
        })
    elif loading_time_ms > 3000:
        recommendations.append({
            "category": "Performance",
            "priority": "medium",
            "title": "Improve Page Load Time",
            "description": f"Your page takes {loading_time_ms/1000:.1f} seconds to become interactive. Consider optimizing for faster load times to improve user experience."
        })
    
    # Online Ordering
    ordering_links = analysis_data.get('online_ordering_links_count', 0)
    if ordering_links == 0:
        recommendations.append({
            "category": "Online Ordering",
            "priority": "high",
            "title": "Add Online Ordering Button",
            "description": "No online ordering links detected. Add a prominent 'Order Online' button to capture more orders and increase revenue."
        })
    
    # Best Practices Score
    best_practices_score = analysis_data.get('best_practices_score', 0)
    if best_practices_score < 80:
        recommendations.append({
            "category": "Best Practices",
            "priority": "medium",
            "title": "Follow Web Best Practices",
            "description": f"Your best practices score is {best_practices_score:.0f}/100. Ensure your site uses modern web standards, secure connections, and proper error handling."
        })
    
    # SEO Score
    seo_score = analysis_data.get('seo_score', 0)
    if seo_score < 70:
        recommendations.append({
            "category": "SEO",
            "priority": "medium",
            "title": "Improve SEO",
            "description": f"Your SEO score is {seo_score:.0f}/100. Optimize meta descriptions, titles, and content to rank higher in search results and attract more customers."
        })
    
    # Accessibility
    accessibility_score = analysis_data.get('accessibility_score', 0)
    if accessibility_score < 70:
        recommendations.append({
            "category": "Accessibility",
            "priority": "medium",
            "title": "Enhance Accessibility",
            "description": f"Your accessibility score is {accessibility_score:.0f}/100. Improve color contrast, add alt text to images, and ensure keyboard navigation works properly."
        })
    
    # Contact Form
    if not analysis_data.get('has_contact_form', False):
        recommendations.append({
            "category": "Customer Engagement",
            "priority": "low",
            "title": "Add Contact Form",
            "description": "No contact form detected. Make it easy for customers to reach you by adding a simple contact form or email signup."
        })
    
    # Meta Description
    if not analysis_data.get('meta_description'):
        recommendations.append({
            "category": "SEO",
            "priority": "low",
            "title": "Add Meta Description",
            "description": "Your website is missing a meta description. Add a compelling description to improve click-through rates from search results."
        })
    
    # Sort by priority (high -> medium -> low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    # Return top 5 recommendations
    return recommendations[:5]

@router.post("/analyze", response_model=WebsiteAnalyzeResponse)
async def analyze_website(request: WebsiteAnalyzeRequest):
    """
    Perform website-only analysis without full restaurant scan.
    
    This endpoint provides fast website analysis (2-5 seconds) including:
    - Website performance score
    - Mobile responsiveness check
    - SSL/HTTPS status
    - Online ordering button detection
    - SEO and accessibility scores
    - Actionable recommendations
    
    Results are saved to database for tracking and analytics.
    """
    try:
        logger.info(f"Starting website-only analysis for: {request.url}")
        
        # Check website availability before creating scan
        is_available = await WebsiteAnalyzer.check_website_availability(request.url)
        if not is_available:
            logger.warning(f"Website not reachable: {request.url}")
            raise HTTPException(
                status_code=422,
                detail=f"Website is not reachable. Please check the URL and try again. URL: {request.url}"
            )
        
        # Create initial scan record
        scan_data = {
            "type": "website_only",
            "url": request.url,
            "status": "in_progress",
            "created_at": datetime.utcnow()
        }
        scan = await create_scan(scan_data)
        scan_id = scan["_id"]
        
        # Perform website analysis using existing analyzer
        try:
            # Import browser_manager singleton
            from ..core.browser import browser_manager
            
            # Initialize browser manager and perform analysis
            async with browser_manager:
                # Use WebsiteAnalyzer to get comprehensive analysis
                analysis_results = await WebsiteAnalyzer.analyze_website(request.url)
                
                # Check if analysis returned empty or failed results
                if not analysis_results or len(analysis_results) == 0:
                    logger.error(f"Analysis returned empty results for {request.url}")
                    raise Exception("Website analysis returned no data. The website may be unreachable or blocking automated access.")
                
                # Calculate website score using existing scorer
                scorer = RestaurantScorer()
                
                # Prepare data for scoring
                website_data = {
                    'pagespeed_score': analysis_results.get('performance_score', 0),
                    'is_mobile_friendly': analysis_results.get('mobile_friendly', False),
                    'has_online_ordering': analysis_results.get('online_ordering_links_count', 0) > 0,
                    'has_ssl': analysis_results.get('https_enabled', False)
                }
                
                website_score = scorer.calculate_website_score(website_data)
                
                # Generate recommendations
                recommendations = generate_recommendations(analysis_results)
                
                # Update scan with results
                update_data = {
                    "status": "completed",
                    "website_score": website_score,
                    "analysis_data": analysis_results,
                    "recommendations": recommendations,
                    "completed_at": datetime.utcnow(),
                    "upgraded_to_full_scan": False
                }
                
                await update_scan(scan_id, update_data)
                
                logger.info(f"Website analysis completed for {request.url} - Score: {website_score:.1f}")
                
                return WebsiteAnalyzeResponse(
                    scan_id=scan_id,
                    url=request.url,
                    website_score=website_score,
                    status="completed",
                    analysis_data=analysis_results,
                    recommendations=[WebsiteRecommendation(**rec) for rec in recommendations],
                    created_at=scan_data["created_at"]
                )
                
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as analysis_error:
            logger.error(f"Website analysis failed for {request.url}: {analysis_error}", exc_info=True)
            
            # Update scan status to failed
            await update_scan(scan_id, {
                "status": "failed",
                "error": str(analysis_error),
                "completed_at": datetime.utcnow()
            })
            
            # Determine appropriate error message
            error_msg = str(analysis_error)
            if "timeout" in error_msg.lower():
                detail = f"Website analysis timed out. The website may be too slow or unresponsive: {error_msg}"
            else:
                detail = f"Website analysis failed: {error_msg}"
            
            raise HTTPException(
                status_code=500,
                detail=detail
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in website analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{scan_id}")
async def get_website_analysis(scan_id: str):
    """
    Retrieve a previously completed website analysis by scan ID.
    
    Args:
        scan_id: The unique identifier for the website scan
    
    Returns:
        Website analysis results including score and recommendations
    """
    from ..database import get_scan_by_id
    
    try:
        scan = await get_scan_by_id(scan_id)
        
        if not scan:
            raise HTTPException(status_code=404, detail="Website analysis not found")
        
        if scan.get("type") != "website_only":
            raise HTTPException(
                status_code=400,
                detail="This scan is not a website-only analysis"
            )
        
        return scan
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving website analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve website analysis: {str(e)}"
        )
