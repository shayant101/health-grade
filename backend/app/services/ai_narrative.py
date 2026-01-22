import logging
from typing import Dict, Any, Optional
import openai

from ..config import settings
from ..models.scan import ScanInDB

class AInarrative:
    """
    Service for generating AI-powered narratives about restaurant digital presence.
    Uses OpenAI GPT-4o-mini to create insightful, actionable narratives.
    """
    
    def __init__(self):
        """
        Initialize OpenAI client with API key.
        """
        openai.api_key = settings.OPENAI_API_KEY
    
    async def generate_narrative(
        self, 
        scan: ScanInDB
    ) -> Optional[str]:
        """
        Generate a comprehensive narrative about the restaurant's digital presence.
        
        Args:
            scan (ScanInDB): Scan results to generate narrative for
        
        Returns:
            Optional[str]: Generated AI narrative
        """
        try:
            # Prepare context for narrative generation
            context = self._prepare_narrative_context(scan)
            
            # Generate narrative using OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a digital marketing expert specializing in restaurant online presence. "
                                   "Provide a concise, actionable narrative about the restaurant's digital performance."
                    },
                    {
                        "role": "user", 
                        "content": f"Generate a narrative based on these digital presence metrics:\n{context}"
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Extract narrative from response
            narrative = response.choices[0].message.content.strip()
            
            return narrative
        
        except Exception as e:
            logging.error(f"AI narrative generation error: {e}")
            return None
    
    def _prepare_narrative_context(
        self, 
        scan: ScanInDB
    ) -> str:
        """
        Prepare a structured context for narrative generation.
        
        Args:
            scan (ScanInDB): Scan results
        
        Returns:
            str: Structured context for AI
        """
        try:
            # Extract key metrics from different analyses
            website_analysis = scan.website_analysis or {}
            google_analysis = scan.google_business_analysis or {}
            reviews_analysis = scan.reviews_analysis or {}
            ordering_analysis = scan.ordering_analysis or {}
            
            # Construct narrative context
            context_parts = [
                f"Comprehensive Score: {scan.comprehensive_score}/100",
                
                # Website Performance
                f"Website Performance: {website_analysis.get('performance_score', 0)}/100 "
                f"({'Mobile Friendly' if website_analysis.get('mobile_friendly', False) else 'Not Mobile Friendly'})",
                
                # Google Business Profile
                f"Google Business Profile: {google_analysis.get('rating', 0)}/5.0 "
                f"({google_analysis.get('review_count', 0)} reviews)",
                
                # Reviews
                f"Reviews Sentiment: {reviews_analysis.get('sentiment_score', 0)}/1.0 "
                f"(Positive Reviews: {reviews_analysis.get('positive_review_percentage', 0)}%)",
                
                # Online Ordering
                f"Online Ordering: {'Available' if ordering_analysis.get('online_ordering_available', False) else 'Not Available'} "
                f"(Platforms: {len(ordering_analysis.get('platforms', []))})"
            ]
            
            return "\n".join(context_parts)
        
        except Exception as e:
            logging.warning(f"Narrative context preparation error: {e}")
            return "No detailed context available"
    
    async def generate_improvement_recommendations(
        self, 
        scan: ScanInDB
    ) -> Optional[Dict[str, Any]]:
        """
        Generate specific improvement recommendations.
        
        Args:
            scan (ScanInDB): Scan results
        
        Returns:
            Optional[Dict[str, Any]]: Improvement recommendations
        """
        try:
            # Prepare context for recommendations
            context = self._prepare_narrative_context(scan)
            
            # Generate recommendations using OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a digital marketing consultant for restaurants. "
                                   "Provide specific, actionable recommendations to improve digital presence."
                    },
                    {
                        "role": "user", 
                        "content": f"Generate improvement recommendations based on these metrics:\n{context}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse recommendations
            recommendations_text = response.choices[0].message.content.strip()
            
            # Structure recommendations
            return {
                "overall_recommendations": recommendations_text,
                "areas_of_focus": self._extract_areas_of_focus(recommendations_text)
            }
        
        except Exception as e:
            logging.error(f"Improvement recommendations error: {e}")
            return None
    
    @staticmethod
    def _extract_areas_of_focus(
        recommendations: str
    ) -> Dict[str, bool]:
        """
        Extract key areas of focus from recommendations.
        
        Args:
            recommendations (str): Recommendations text
        
        Returns:
            Dict[str, bool]: Areas of focus
        """
        focus_areas = {
            "website_improvement": "website" in recommendations.lower(),
            "google_profile_optimization": "google" in recommendations.lower(),
            "review_management": "review" in recommendations.lower(),
            "online_ordering": "order" in recommendations.lower(),
            "social_media": "social" in recommendations.lower()
        }
        
        return focus_areas