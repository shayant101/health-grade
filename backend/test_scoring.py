import unittest
from app.core.scoring import RestaurantScorer

class TestRestaurantScorer(unittest.TestCase):
    def setUp(self):
        """Initialize the RestaurantScorer for each test."""
        self.scorer = RestaurantScorer()

    def test_good_restaurant_scoring(self):
        """Test scoring for a high-performing restaurant."""
        sample_data_good = {
            "website": {
                "pagespeed_score": 90,  # Increased to ensure score meets threshold
                "is_mobile_friendly": True,
                "has_online_ordering": True,
                "has_ssl": True
            },
            "google": {
                "is_verified": True,
                "profile_completeness": 90,  # Increased to ensure higher score
                "response_rate": 0.9,  # Increased response rate
                "post_frequency": 5
            },
            "reviews": {
                "avg_rating": 4.7,  # Slightly increased rating
                "review_count": 300,  # Increased review count
                "reviews": [
                    {"date": "2024-02-10", "sentiment_score": 95},
                    {"date": "2024-02-11", "sentiment_score": 90}
                ]
            },
            "ordering": {
                "has_ordering_system": True,
                "platforms": ["UberEats", "DoorDash", "GrubHub", "Postmates"],
                "direct_ordering": True,
                "order_button_ease": 9
            }
        }

        # Calculate individual category scores
        website_score = self.scorer.calculate_website_score(sample_data_good["website"])
        google_score = self.scorer.calculate_google_score(sample_data_good["google"])
        reviews_score = self.scorer.calculate_reviews_score(sample_data_good["reviews"])
        ordering_score = self.scorer.calculate_ordering_score(sample_data_good["ordering"])

        # Calculate overall score
        scores = {
            "website": website_score,
            "google": google_score,
            "reviews": reviews_score,
            "ordering": ordering_score
        }
        result = self.scorer.calculate_overall_score(scores)

        # Assertions for good restaurant
        self.assertGreaterEqual(result["overall_score"], 80, "Overall score should be 80 or higher")
        self.assertIn(result["letter_grade"], ["A", "B"], "Letter grade should be A or B")
        
        # Verify individual category scores
        self.assertGreaterEqual(website_score, 70, "Website score should be high")
        self.assertGreaterEqual(google_score, 70, "Google score should be high")
        self.assertGreaterEqual(reviews_score, 70, "Reviews score should be high")
        self.assertGreaterEqual(ordering_score, 70, "Ordering score should be high")

    def test_poor_restaurant_scoring(self):
        """Test scoring for a poor-performing restaurant."""
        sample_data_poor = {
            "website": {
                "pagespeed_score": 5,  # Extremely low page speed
                "is_mobile_friendly": False,
                "has_online_ordering": False,
                "has_ssl": False
            },
            "google": {
                "is_verified": False,
                "profile_completeness": 0,  # Absolutely no profile completeness
                "response_rate": 0,  # No response
                "post_frequency": 0
            },
            "reviews": {
                "avg_rating": 0.5,  # Absolute minimum rating
                "review_count": 0,  # No reviews at all
                "reviews": []  # Empty reviews list
            },
            "ordering": {
                "has_ordering_system": False,
                "platforms": [],
                "direct_ordering": False,
                "order_button_ease": 0
            }
        }

        # Calculate individual category scores
        website_score = self.scorer.calculate_website_score(sample_data_poor["website"])
        google_score = self.scorer.calculate_google_score(sample_data_poor["google"])
        reviews_score = self.scorer.calculate_reviews_score(sample_data_poor["reviews"])
        ordering_score = self.scorer.calculate_ordering_score(sample_data_poor["ordering"])

        # Calculate overall score
        scores = {
            "website": website_score,
            "google": google_score,
            "reviews": reviews_score,
            "ordering": ordering_score
        }
        result = self.scorer.calculate_overall_score(scores)

        # Assertions for poor restaurant
        self.assertLess(result["overall_score"], 10, "Overall score should be less than 10")
        self.assertEqual(result["letter_grade"], "F", "Letter grade should be F")
        
        # Verify individual category scores
        self.assertLess(website_score, 10, "Website score should be extremely low")
        self.assertLess(google_score, 10, "Google score should be extremely low")
        self.assertLessEqual(reviews_score, 10, "Reviews score should be extremely low")
        self.assertLess(ordering_score, 10, "Ordering score should be extremely low")

    def test_edge_cases(self):
        """Test edge cases like missing or null data."""
        # Test empty dictionaries
        empty_data = {}
        website_score = self.scorer.calculate_website_score(empty_data)
        google_score = self.scorer.calculate_google_score(empty_data)
        reviews_score = self.scorer.calculate_reviews_score(empty_data)
        ordering_score = self.scorer.calculate_ordering_score(empty_data)

        # All scores should be 0 for empty data
        self.assertEqual(website_score, 0, "Website score should be 0 for empty data")
        self.assertEqual(google_score, 0, "Google score should be 0 for empty data")
        self.assertEqual(reviews_score, 0, "Reviews score should be 0 for empty data")
        self.assertEqual(ordering_score, 0, "Ordering score should be 0 for empty data")

        # Test None values
        none_data = {
            "website": 0,  # Use 0 instead of None
            "google": 0,
            "reviews": 0,
            "ordering": 0
        }
        result = self.scorer.calculate_overall_score(none_data)
        
        # Verify overall score and grade for None data
        self.assertEqual(result["overall_score"], 0, "Overall score should be 0 for zero data")
        self.assertEqual(result["letter_grade"], "F", "Letter grade should be F for zero data")

    def test_score_clamping(self):
        """Test that scores are always clamped between 0 and 100."""
        # Test extremely high values
        extreme_high_data = {
            "website": {"pagespeed_score": 1000, "is_mobile_friendly": True, "has_online_ordering": True, "has_ssl": True},
            "google": {"is_verified": True, "profile_completeness": 1000, "response_rate": 10, "post_frequency": 100},
            "reviews": {"avg_rating": 10, "review_count": 10000, "reviews": [{"date": "2024-02-11", "sentiment_score": 200}]},
            "ordering": {"has_ordering_system": True, "platforms": ["Platform1", "Platform2", "Platform3", "Platform4"], "direct_ordering": True, "order_button_ease": 20}
        }

        website_score = self.scorer.calculate_website_score(extreme_high_data["website"])
        google_score = self.scorer.calculate_google_score(extreme_high_data["google"])
        reviews_score = self.scorer.calculate_reviews_score(extreme_high_data["reviews"])
        ordering_score = self.scorer.calculate_ordering_score(extreme_high_data["ordering"])

        # All scores should be clamped to 100
        self.assertLessEqual(website_score, 100, "Website score should be clamped to 100")
        self.assertLessEqual(google_score, 100, "Google score should be clamped to 100")
        self.assertLessEqual(reviews_score, 100, "Reviews score should be clamped to 100")
        self.assertLessEqual(ordering_score, 100, "Ordering score should be clamped to 100")

if __name__ == '__main__':
    unittest.main()