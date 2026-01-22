import logging
from typing import List, Dict, Any, Optional
import httpx
from textblob import TextBlob

class ReviewsAnalyzer:
    """
    Advanced service for analyzing restaurant reviews from multiple sources.
    Provides sentiment analysis, theme extraction, and comprehensive review insights.
    """
    
    @classmethod
    async def analyze_reviews(
        cls, 
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of restaurant reviews.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews to analyze
        
        Returns:
            Dict[str, Any]: Detailed review analysis
        """
        try:
            # Basic review statistics
            total_reviews = len(reviews)
            
            if total_reviews == 0:
                return cls._empty_review_analysis()
            
            # Calculate average rating
            average_rating = sum(
                review.get('rating', 0) for review in reviews
            ) / total_reviews
            
            # Sentiment analysis
            sentiment_scores = [
                cls._analyze_sentiment(review.get('text', '')) 
                for review in reviews
            ]
            
            # Calculate overall sentiment
            overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Extract key themes
            key_themes = cls._extract_themes(reviews)
            
            # Detailed rating distribution
            rating_distribution = cls._calculate_rating_distribution(reviews)
            
            return {
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 2),
                'sentiment_score': round(overall_sentiment, 2),
                'rating_distribution': rating_distribution,
                'key_themes': key_themes,
                'positive_review_percentage': cls._calculate_positive_review_percentage(sentiment_scores)
            }
        
        except Exception as e:
            logging.error(f"Review analysis error: {e}")
            return cls._empty_review_analysis()
    
    @staticmethod
    def _analyze_sentiment(text: str) -> float:
        """
        Perform sentiment analysis on review text.
        
        Args:
            text (str): Review text to analyze
        
        Returns:
            float: Sentiment score between -1 (very negative) and 1 (very positive)
        """
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text.lower())
            return blob.sentiment.polarity
        
        except Exception as e:
            logging.warning(f"Sentiment analysis error: {e}")
            return 0.0
    
    @staticmethod
    def _extract_themes(reviews: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key themes from reviews using basic NLP techniques.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews
        
        Returns:
            List[str]: Extracted key themes
        """
        try:
            # Combine all review texts
            all_text = ' '.join(
                review.get('text', '').lower() 
                for review in reviews
            )
            
            # Define a list of potential themes
            theme_keywords = {
                'food_quality': ['taste', 'delicious', 'flavor', 'fresh', 'quality'],
                'service': ['friendly', 'staff', 'service', 'wait', 'attentive'],
                'atmosphere': ['ambiance', 'decor', 'environment', 'clean', 'nice'],
                'price': ['expensive', 'cheap', 'value', 'affordable', 'cost'],
                'location': ['parking', 'convenient', 'location', 'area', 'accessible']
            }
            
            # Find themes
            detected_themes = [
                theme for theme, keywords in theme_keywords.items()
                if any(keyword in all_text for keyword in keywords)
            ]
            
            return detected_themes
        
        except Exception as e:
            logging.warning(f"Theme extraction error: {e}")
            return []
    
    @staticmethod
    def _calculate_rating_distribution(reviews: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Calculate distribution of ratings.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews
        
        Returns:
            Dict[int, int]: Rating distribution
        """
        try:
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            for review in reviews:
                rating = review.get('rating', 0)
                if 1 <= rating <= 5:
                    distribution[rating] += 1
            
            return distribution
        
        except Exception as e:
            logging.warning(f"Rating distribution error: {e}")
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    @staticmethod
    def _calculate_positive_review_percentage(sentiment_scores: List[float]) -> float:
        """
        Calculate percentage of positive reviews.
        
        Args:
            sentiment_scores (List[float]): List of sentiment scores
        
        Returns:
            float: Percentage of positive reviews
        """
        try:
            positive_reviews = sum(1 for score in sentiment_scores if score > 0)
            return round((positive_reviews / len(sentiment_scores)) * 100, 2) if sentiment_scores else 0.0
        
        except Exception as e:
            logging.warning(f"Positive review percentage calculation error: {e}")
            return 0.0
    
    @staticmethod
    def _empty_review_analysis() -> Dict[str, Any]:
        """
        Return a default empty review analysis.
        
        Returns:
            Dict[str, Any]: Empty review analysis structure
        """
        return {
            'total_reviews': 0,
            'average_rating': 0.0,
            'sentiment_score': 0.0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'key_themes': [],
            'positive_review_percentage': 0.0
        }
    
    @classmethod
    async def fetch_reviews(
        cls, 
        restaurant_id: str, 
        source: str = 'google'
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews from various sources.
        
        Args:
            restaurant_id (str): Unique identifier for the restaurant
            source (str): Source of reviews (default: 'google')
        
        Returns:
            List[Dict[str, Any]]: List of reviews
        """
        # Placeholder for future implementation of multi-source review fetching
        # Could integrate with Google, Yelp, TripAdvisor APIs
        logging.warning(f"Review fetching not implemented for source: {source}")
        return []