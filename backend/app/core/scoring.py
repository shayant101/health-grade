from typing import Dict, Any, Optional
import statistics
from datetime import datetime, timedelta

class RestaurantScorer:
    """
    Scoring class for restaurant-related metrics with weighted scoring algorithm.
    """

    @staticmethod
    def _clamp_score(score: float) -> float:
        """
        Clamp score between 0 and 100.
        
        Args:
            score (float): Input score
        
        Returns:
            float: Clamped score between 0 and 100
        """
        return max(0.0, min(100.0, score))

    def calculate_website_score(self, website_data: dict) -> float:
        """
        Calculate website quality score incorporating PageSpeed metrics.
        
        Args:
            website_data (dict): Website analysis data including PageSpeed metrics
        
        Returns:
            float: Website score (0-100)
        """
        if not website_data:
            return 0.0

        # PageSpeed metrics (from PageSpeed API)
        performance_score = website_data.get('pagespeed_score', website_data.get('performance_score', 0))
        accessibility_score = website_data.get('accessibility_score', 0)
        seo_score = website_data.get('seo_score', 0)
        best_practices_score = website_data.get('best_practices_score', 0)
        
        # Playwright metrics
        is_mobile_friendly = website_data.get('is_mobile_friendly', website_data.get('mobile_friendly', False))
        has_online_ordering = website_data.get('has_online_ordering', False)
        has_ssl = website_data.get('has_ssl', website_data.get('https_enabled', False))

        # Calculate weighted PageSpeed score (if we have PageSpeed data)
        has_pagespeed_data = any([performance_score, accessibility_score, seo_score, best_practices_score])
        
        if has_pagespeed_data:
            # Weighted average of PageSpeed metrics
            pagespeed_composite = (
                performance_score * 0.40 +      # Performance is most important
                accessibility_score * 0.25 +    # Accessibility matters for all users
                seo_score * 0.20 +              # SEO helps discoverability
                best_practices_score * 0.15     # Best practices for quality
            )
        else:
            # Fallback if no PageSpeed data
            pagespeed_composite = 0

        # Additional feature scores
        mobile_friendly_score = 100 if is_mobile_friendly else 0
        online_ordering_score = 100 if has_online_ordering else 0
        ssl_score = 100 if has_ssl else 0

        # Combine all scores with weights
        total_score = (
            pagespeed_composite * 0.60 +      # 60% weight to PageSpeed metrics
            mobile_friendly_score * 0.15 +    # 15% weight to mobile friendliness
            ssl_score * 0.15 +                # 15% weight to HTTPS
            online_ordering_score * 0.10      # 10% weight to online ordering
        )

        return self._clamp_score(total_score)

    def calculate_google_score(self, google_data: dict) -> float:
        """
        Calculate Google Business Profile score.
        
        Args:
            google_data (dict): Google Business Profile data
        
        Returns:
            float: Google score (0-100)
        """
        if not google_data:
            return 0.0

        # Default values for missing data
        is_verified = google_data.get('is_verified', False)
        completeness = google_data.get('profile_completeness', 0)
        response_rate = google_data.get('response_rate', 0)
        post_frequency = google_data.get('post_frequency', 0)

        # Scoring components
        verification_score = 30 if is_verified else 0
        completeness_score = min(completeness * 0.5, 30)  # Max 30 points
        response_score = min(response_rate * 2, 20)  # Max 20 points
        post_score = min(post_frequency * 2, 20)  # Max 20 points

        total_score = verification_score + completeness_score + response_score + post_score

        return self._clamp_score(total_score)

    def calculate_reviews_score(self, reviews_data: dict) -> float:
        """
        Calculate reviews score.
        
        Args:
            reviews_data (dict): Reviews analysis data
        
        Returns:
            float: Reviews score (0-100)
        """
        if not reviews_data:
            return 0.0

        # Default values for missing data
        avg_rating = reviews_data.get('avg_rating', 0)
        review_count = reviews_data.get('review_count', 0)
        reviews = reviews_data.get('reviews', [])

        # Rating score (max 40 points)
        rating_score = min(avg_rating * 20, 40)  # 5-star rating = 100

        # Review count score (max 30 points)
        review_count_score = min(review_count * 0.3, 30)

        # Recency and sentiment score (max 30 points)
        recency_sentiment_score = 0
        if reviews:
            # Calculate average recency (prefer recent reviews)
            now = datetime.now()
            recency_scores = []
            for review in reviews:
                review_date = review.get('date')
                if review_date:
                    days_ago = (now - datetime.fromisoformat(review_date)).days
                    # More recent reviews get higher scores
                    recency_score = max(0, 100 - (days_ago / 30 * 100))
                    sentiment_score = review.get('sentiment_score', 50)
                    recency_scores.append((recency_score + sentiment_score) / 2)
            
            if recency_scores:
                recency_sentiment_score = min(statistics.mean(recency_scores), 30)

        total_score = rating_score + review_count_score + recency_sentiment_score

        return self._clamp_score(total_score)

    def calculate_ordering_score(self, ordering_data: dict) -> float:
        """
        Calculate ordering systems score.
        
        Args:
            ordering_data (dict): Ordering systems analysis data
        
        Returns:
            float: Ordering score (0-100)
        """
        if not ordering_data:
            return 0.0

        # Default values for missing data
        has_ordering_system = ordering_data.get('has_ordering_system', False)
        platforms = ordering_data.get('platforms', [])
        direct_ordering = ordering_data.get('direct_ordering', False)
        order_button_ease = ordering_data.get('order_button_ease', 0)

        # Scoring components
        system_score = 40 if has_ordering_system else 0
        platforms_score = min(len(platforms) * 10, 30)  # Max 30 points for multiple platforms
        direct_ordering_score = 20 if direct_ordering else 0
        button_ease_score = min(order_button_ease * 10, 10)  # Max 10 points

        total_score = system_score + platforms_score + direct_ordering_score + button_ease_score

        return self._clamp_score(total_score)

    def calculate_overall_score(self, scores: dict) -> dict:
        """
        Calculate overall restaurant score with weighted average and letter grade.
        
        Args:
            scores (dict): Category scores
        
        Returns:
            dict: Overall score details
        """
        # Default to 0 if category not present
        website_score = scores.get('website', 0)
        google_score = scores.get('google', 0)
        reviews_score = scores.get('reviews', 0)
        ordering_score = scores.get('ordering', 0)

        # Apply weights: 30/30/25/15
        weighted_scores = {
            'website': website_score * 0.30,
            'google': google_score * 0.30,
            'reviews': reviews_score * 0.25,
            'ordering': ordering_score * 0.15
        }

        # Calculate overall score
        overall_score = sum(weighted_scores.values())

        # Determine letter grade
        if overall_score >= 90:
            letter_grade = 'A'
        elif overall_score >= 80:
            letter_grade = 'B'
        elif overall_score >= 70:
            letter_grade = 'C'
        elif overall_score >= 60:
            letter_grade = 'D'
        else:
            letter_grade = 'F'

        return {
            'overall_score': round(overall_score, 2),
            'letter_grade': letter_grade,
            'category_scores': {
                'website': round(website_score, 2),
                'google': round(google_score, 2),
                'reviews': round(reviews_score, 2),
                'ordering': round(ordering_score, 2)
            },
            'weighted_scores': {
                key: round(value, 2) for key, value in weighted_scores.items()
            }
        }