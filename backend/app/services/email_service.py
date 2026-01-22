import logging
from typing import Dict, Any, Optional, List
import resend

from ..config import settings
from ..models.lead import LeadCreate

class EmailService:
    """
    Email delivery service using Resend for transactional and marketing emails.
    Provides methods for sending various types of emails with robust error handling.
    """
    
    def __init__(self):
        """
        Initialize Resend email service with API key.
        """
        resend.api_key = settings.RESEND_API_KEY
    
    async def send_lead_confirmation_email(
        self, 
        lead: LeadCreate, 
        scan_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a confirmation email to a new lead.
        
        Args:
            lead (LeadCreate): Lead information
            scan_url (Optional[str]): URL for restaurant scan results
        
        Returns:
            Dict[str, Any]: Email sending result
        """
        try:
            # Construct email content
            html_content = self._build_lead_confirmation_email(lead, scan_url)
            
            # Send email
            response = resend.Emails.send({
                "from": "RestaurantGrader <leads@restaurantgrader.com>",
                "to": lead.email,
                "subject": "Your Restaurant Scan Request Confirmation",
                "html": html_content
            })
            
            return {
                "success": True,
                "message_id": response.get('id'),
                "email": lead.email
            }
        
        except Exception as e:
            logging.error(f"Lead confirmation email error: {e}")
            return {
                "success": False,
                "error": str(e),
                "email": lead.email
            }
    
    async def send_scan_results_email(
        self, 
        email: str, 
        restaurant_name: str, 
        scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send restaurant scan results via email.
        
        Args:
            email (str): Recipient email address
            restaurant_name (str): Name of the restaurant
            scan_results (Dict[str, Any]): Comprehensive scan results
        
        Returns:
            Dict[str, Any]: Email sending result
        """
        try:
            # Construct email content
            html_content = self._build_scan_results_email(
                restaurant_name, 
                scan_results
            )
            
            # Send email
            response = resend.Emails.send({
                "from": "RestaurantGrader <results@restaurantgrader.com>",
                "to": email,
                "subject": f"Scan Results for {restaurant_name}",
                "html": html_content
            })
            
            return {
                "success": True,
                "message_id": response.get('id'),
                "email": email
            }
        
        except Exception as e:
            logging.error(f"Scan results email error: {e}")
            return {
                "success": False,
                "error": str(e),
                "email": email
            }
    
    def _build_lead_confirmation_email(
        self, 
        lead: LeadCreate, 
        scan_url: Optional[str] = None
    ) -> str:
        """
        Build HTML content for lead confirmation email.
        
        Args:
            lead (LeadCreate): Lead information
            scan_url (Optional[str]): URL for restaurant scan results
        
        Returns:
            str: HTML email content
        """
        return f"""
        <html>
        <body>
            <h1>Thank You for Your Restaurant Scan Request</h1>
            <p>Hello {lead.name or 'Restaurant Owner'},</p>
            
            <p>We've received your request for a comprehensive restaurant digital presence scan 
            for <strong>{lead.restaurant_name or 'your restaurant'}</strong>.</p>
            
            {f'<p>You can track your scan progress here: <a href="{scan_url}">Scan Status</a></p>' if scan_url else ''}
            
            <p>Our team will analyze your restaurant's online presence, including:</p>
            <ul>
                <li>Website Performance</li>
                <li>Google Business Profile</li>
                <li>Online Reviews</li>
                <li>Ordering Capabilities</li>
            </ul>
            
            <p>We'll email you the detailed results soon!</p>
            
            <p>Best regards,<br>RestaurantGrader Team</p>
        </body>
        </html>
        """
    
    def _build_scan_results_email(
        self, 
        restaurant_name: str, 
        scan_results: Dict[str, Any]
    ) -> str:
        """
        Build HTML content for scan results email.
        
        Args:
            restaurant_name (str): Name of the restaurant
            scan_results (Dict[str, Any]): Comprehensive scan results
        
        Returns:
            str: HTML email content
        """
        comprehensive_score = scan_results.get('comprehensive_score', 0)
        
        return f"""
        <html>
        <body>
            <h1>Restaurant Digital Presence Scan Results</h1>
            <h2>{restaurant_name}</h2>
            
            <div style="background-color: {'#4CAF50' if comprehensive_score >= 70 else '#FFC107' if comprehensive_score >= 40 else '#F44336'}; 
                        color: white; 
                        padding: 10px; 
                        text-align: center;">
                <h3>Overall Digital Presence Score: {comprehensive_score:.2f}/100</h3>
            </div>
            
            <h4>Detailed Breakdown:</h4>
            <ul>
                <li><strong>Website Analysis:</strong> {self._format_subscore(scan_results.get('website_analysis', {}))}</li>
                <li><strong>Google Business Profile:</strong> {self._format_subscore(scan_results.get('google_business_analysis', {}))}</li>
                <li><strong>Reviews Analysis:</strong> {self._format_subscore(scan_results.get('reviews_analysis', {}))}</li>
                <li><strong>Online Ordering:</strong> {self._format_subscore(scan_results.get('ordering_analysis', {}))}</li>
            </ul>
            
            <p>Want to improve your digital presence? Contact our team for a detailed consultation!</p>
            
            <p>Best regards,<br>RestaurantGrader Team</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _format_subscore(analysis: Dict[str, Any]) -> str:
        """
        Format subscore for email display.
        
        Args:
            analysis (Dict[str, Any]): Analysis results
        
        Returns:
            str: Formatted subscore description
        """
        if not analysis:
            return "No data available"
        
        # Extract key metrics for display
        if 'performance_score' in analysis:
            return f"{analysis.get('performance_score', 0):.2f}/100"
        elif 'rating' in analysis:
            return f"{analysis.get('rating', 0):.2f}/5.00"
        elif 'online_ordering_available' in analysis:
            return "Available" if analysis.get('online_ordering_available', False) else "Not Available"
        
        return "Analyzed"