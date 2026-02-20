#!/usr/bin/env python3
"""
Test to reproduce the 9.78 score calculation
"""

# Mock data from scan_orchestrator.py lines 32-53
google_data = {
    "has_photos": True,
    "has_hours": True,
    "has_description": True,
    "is_verified": True,
    "response_rate": 0.8,
    "posts_per_month": 4
}

reviews_data = {
    "average_rating": 4.2,
    "total_reviews": 150,
    "recent_reviews_count": 30,
    "positive_sentiment": 0.75
}

# When website times out, website_data would be empty {}
website_data = {}

ordering_data = {
    "has_ordering": False,  # No order button found when timeout
    "platforms_count": 0,
    "has_direct_ordering": False,
    "order_button_found": False
}

print("=" * 60)
print("REPRODUCING THE 9.78 SCORE CALCULATION")
print("=" * 60)

# Website score (from scoring.py lines 23-56)
# When website_data is empty, returns 0.0
website_score = 0.0
print(f"\n1. WEBSITE SCORE: {website_score}")
print(f"   - website_data is empty (timeout occurred)")

# Google score (from scoring.py lines 58-85)
# Note: The mock data keys don't match the expected keys in calculate_google_score
# Expected: is_verified, profile_completeness, response_rate, post_frequency
# Provided: is_verified, response_rate, posts_per_month (WRONG KEYS!)
print(f"\n2. GOOGLE SCORE CALCULATION:")
print(f"   Mock data provided: {google_data}")
print(f"   Expected keys: is_verified, profile_completeness, response_rate, post_frequency")

is_verified = google_data.get('is_verified', False)
completeness = google_data.get('profile_completeness', 0)  # MISSING! Defaults to 0
response_rate = google_data.get('response_rate', 0)
post_frequency = google_data.get('post_frequency', 0)  # WRONG KEY! Should be 'posts_per_month'

verification_score = 30 if is_verified else 0
completeness_score = min(completeness * 0.5, 30)
response_score = min(response_rate * 2, 20)
post_score = min(post_frequency * 2, 20)

google_score = verification_score + completeness_score + response_score + post_score
print(f"   - verification_score: {verification_score} (is_verified={is_verified})")
print(f"   - completeness_score: {completeness_score} (profile_completeness={completeness} - KEY MISSING!)")
print(f"   - response_score: {response_score} (response_rate={response_rate})")
print(f"   - post_score: {post_score} (post_frequency={post_frequency} - WRONG KEY!)")
print(f"   GOOGLE SCORE: {google_score}")

# Reviews score (from scoring.py lines 87-131)
# Expected: avg_rating, review_count, reviews
# Provided: average_rating, total_reviews (WRONG KEYS!)
print(f"\n3. REVIEWS SCORE CALCULATION:")
print(f"   Mock data provided: {reviews_data}")
print(f"   Expected keys: avg_rating, review_count, reviews")

avg_rating = reviews_data.get('avg_rating', 0)  # WRONG KEY! Should be 'average_rating'
review_count = reviews_data.get('review_count', 0)  # WRONG KEY! Should be 'total_reviews'
reviews = reviews_data.get('reviews', [])

rating_score = min(avg_rating * 20, 40)
review_count_score = min(review_count * 0.3, 30)
recency_sentiment_score = 0  # No reviews array

reviews_score = rating_score + review_count_score + recency_sentiment_score
print(f"   - rating_score: {rating_score} (avg_rating={avg_rating} - KEY MISSING!)")
print(f"   - review_count_score: {review_count_score} (review_count={review_count} - KEY MISSING!)")
print(f"   - recency_sentiment_score: {recency_sentiment_score} (no reviews array)")
print(f"   REVIEWS SCORE: {reviews_score}")

# Ordering score (from scoring.py lines 133-160)
# Expected: has_ordering_system, platforms, direct_ordering, order_button_ease
# Provided: has_ordering, platforms_count (WRONG KEYS!)
print(f"\n4. ORDERING SCORE CALCULATION:")
print(f"   Mock data provided: {ordering_data}")
print(f"   Expected keys: has_ordering_system, platforms, direct_ordering, order_button_ease")

has_ordering_system = ordering_data.get('has_ordering_system', False)  # WRONG KEY!
platforms = ordering_data.get('platforms', [])
direct_ordering = ordering_data.get('direct_ordering', False)
order_button_ease = ordering_data.get('order_button_ease', 0)

system_score = 40 if has_ordering_system else 0
platforms_score = min(len(platforms) * 10, 30)
direct_ordering_score = 20 if direct_ordering else 0
button_ease_score = min(order_button_ease * 10, 10)

ordering_score = system_score + platforms_score + direct_ordering_score + button_ease_score
print(f"   - system_score: {system_score} (has_ordering_system={has_ordering_system} - KEY MISSING!)")
print(f"   - platforms_score: {platforms_score} (platforms={platforms})")
print(f"   - direct_ordering_score: {direct_ordering_score} (direct_ordering={direct_ordering})")
print(f"   - button_ease_score: {button_ease_score} (order_button_ease={order_button_ease})")
print(f"   ORDERING SCORE: {ordering_score}")

# Overall score (from scoring.py lines 162-213)
# Weights: 30/30/25/15
print(f"\n5. OVERALL SCORE CALCULATION:")
print(f"   Weights: website=30%, google=30%, reviews=25%, ordering=15%")

weighted_scores = {
    'website': website_score * 0.30,
    'google': google_score * 0.30,
    'reviews': reviews_score * 0.25,
    'ordering': ordering_score * 0.15
}

overall_score = sum(weighted_scores.values())

print(f"   - website: {website_score} * 0.30 = {weighted_scores['website']}")
print(f"   - google: {google_score} * 0.30 = {weighted_scores['google']}")
print(f"   - reviews: {reviews_score} * 0.25 = {weighted_scores['reviews']}")
print(f"   - ordering: {ordering_score} * 0.15 = {weighted_scores['ordering']}")

print(f"\n" + "=" * 60)
print(f"FINAL OVERALL SCORE: {round(overall_score, 2)}")
print(f"=" * 60)

print(f"\n🔍 ROOT CAUSE ANALYSIS:")
print(f"The score is calculated from MOCK DATA with MISMATCHED KEYS!")
print(f"The mock data in scan_orchestrator.py (lines 32-53) uses different")
print(f"key names than what the scoring functions expect, causing all the")
print(f"mock values to be ignored and defaulting to 0.")
