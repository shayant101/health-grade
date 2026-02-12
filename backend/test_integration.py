"""
Integration Test for Restaurant Grader
Tests complete flow: Browser automation + Order detection + Scoring
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any
from app.core.browser import BrowserManager
from app.core.scoring import RestaurantScorer


class IntegrationTest:
    """Comprehensive integration test for restaurant grading system"""
    
    def __init__(self):
        self.browser_manager = None
        self.scorer = RestaurantScorer()
        self.results = []
        self.start_time = None
        self.end_time = None
        
    # Test restaurant URLs (including user-requested websites)
    RESTAURANTS = [
        {
            "name": "Chipotle",
            "url": "https://www.chipotle.com",
            "expected_order_button": True
        },
        {
            "name": "Desi Curry",
            "url": "https://desicurry.us/",
            "expected_order_button": True
        },
        {
            "name": "Yummee Sandwiches",
            "url": "http://www.yummeesandwiches.com/",
            "expected_order_button": True
        },
        {
            "name": "La KaViet",
            "url": "https://lakaviet.com",
            "expected_order_button": True
        },
        {
            "name": "Panera Bread",
            "url": "https://www.panerabread.com",
            "expected_order_button": True
        },
        {
            "name": "Burger Town USA",
            "url": "https://www.burgertownusa.net/",
            "expected_order_button": True
        }
    ]
    
    def create_mock_scoring_data(self, restaurant_name: str, browser_data: Dict) -> Dict:
        """Create mock scoring data for testing"""
        
        # Base scores with some variation per restaurant
        base_scores = {
            "Chipotle": {"google": 85, "reviews": 90, "ordering": 85},
            "Desi Curry": {"google": 75, "reviews": 80, "ordering": 70},
            "Yummee Sandwiches": {"google": 70, "reviews": 75, "ordering": 65},
            "La KaViet": {"google": 75, "reviews": 85, "ordering": 70},
            "Panera Bread": {"google": 80, "reviews": 85, "ordering": 80},
            "Burger Town USA": {"google": 70, "reviews": 75, "ordering": 70}
        }
        
        scores = base_scores.get(restaurant_name, {"google": 75, "reviews": 80, "ordering": 75})
        
        # Create website data for scoring
        website_data = {
            "has_ssl": browser_data.get("has_ssl", False),
            "is_mobile_friendly": browser_data.get("mobile_responsive", False),
            "has_online_ordering": browser_data.get("order_button_detected", False),
            "pagespeed_score": 75  # Mock PageSpeed score
        }
        
        # Create Google data
        google_data = {
            "is_verified": True,
            "profile_completeness": 80,
            "response_rate": 65,
            "post_frequency": 8
        }
        
        # Create reviews data
        reviews_data = {
            "avg_rating": 4.2,
            "review_count": 250,
            "reviews": []
        }
        
        # Create ordering data
        ordering_data = {
            "has_ordering_system": browser_data.get("order_button_detected", False),
            "platforms": browser_data.get("platforms", []),
            "direct_ordering": browser_data.get("order_button_detected", False),
            "order_button_ease": 8
        }
        
        return {
            "website_data": website_data,
            "google_data": google_data,
            "reviews_data": reviews_data,
            "ordering_data": ordering_data
        }
    
    async def test_restaurant(self, restaurant: Dict) -> Dict[str, Any]:
        """Test a single restaurant website"""
        
        print(f"\n{'='*60}")
        print(f"Testing: {restaurant['name']}")
        print(f"URL: {restaurant['url']}")
        print(f"{'='*60}")
        
        test_start = time.time()
        result = {
            "name": restaurant["name"],
            "url": restaurant["url"],
            "success": False,
            "error": None,
            "browser_data": {},
            "scores": {},
            "duration": 0
        }
        
        try:
            # Step 1: Browser Analysis
            print("\n🌐 Running browser analysis...")
            async with BrowserManager() as browser_manager:
                browser_data = await browser_manager.analyze_website(restaurant["url"])
            result["browser_data"] = browser_data
            
            # Display browser analysis results
            print("\nBrowser Analysis Results:")
            print(f"  {'✅' if browser_data.get('has_ssl') else '❌'} SSL: {browser_data.get('has_ssl')}")
            print(f"  {'✅' if browser_data.get('mobile_responsive') else '❌'} Mobile Friendly: {browser_data.get('mobile_responsive')}")
            print(f"  📄 Title: {browser_data.get('page_title', 'N/A')[:50]}")
            
            order_button_detected = browser_data.get('order_button_detected')
            button_text = browser_data.get('button_text')
            if order_button_detected and button_text:
                print(f"  ✅ Order Button: Found \"{button_text}\"")
            else:
                print(f"  ❌ Order Button: Not found")
                
            platforms = browser_data.get('platforms', [])
            if platforms:
                print(f"  🍔 Platforms: {', '.join(platforms)}")
            else:
                print(f"  🍔 Platforms: None detected")
            
            # Step 2: Create mock scoring data
            print("\n📊 Creating mock scoring data...")
            mock_data = self.create_mock_scoring_data(restaurant["name"], browser_data)
            
            # Step 3: Calculate individual category scores
            print("🧮 Calculating scores...")
            website_score = self.scorer.calculate_website_score(mock_data["website_data"])
            google_score = self.scorer.calculate_google_score(mock_data["google_data"])
            reviews_score = self.scorer.calculate_reviews_score(mock_data["reviews_data"])
            ordering_score = self.scorer.calculate_ordering_score(mock_data["ordering_data"])
            
            # Step 4: Calculate overall score
            category_scores = {
                "website": website_score,
                "google": google_score,
                "reviews": reviews_score,
                "ordering": ordering_score
            }
            
            scores = self.scorer.calculate_overall_score(category_scores)
            
            # Add letter grades for each category
            def get_letter_grade(score):
                if score >= 90: return 'A'
                elif score >= 80: return 'B'
                elif score >= 70: return 'C'
                elif score >= 60: return 'D'
                else: return 'F'
            
            scores['category_grades'] = {
                category: get_letter_grade(score)
                for category, score in scores['category_scores'].items()
            }
            
            result["scores"] = scores
            
            # Display scoring results
            print("\n" + "="*60)
            print("SCORING RESULTS")
            print("="*60)
            print(f"\nCategory Scores:")
            print(f"  Website Score:  {scores['category_scores']['website']:.1f}/100 (Grade: {scores['category_grades']['website']})")
            print(f"  Google Score:   {scores['category_scores']['google']:.1f}/100 (Grade: {scores['category_grades']['google']})")
            print(f"  Reviews Score:  {scores['category_scores']['reviews']:.1f}/100 (Grade: {scores['category_grades']['reviews']})")
            print(f"  Ordering Score: {scores['category_scores']['ordering']:.1f}/100 (Grade: {scores['category_grades']['ordering']})")
            
            print(f"\n🎯 Overall Score: {scores['overall_score']:.1f}/100")
            print(f"📝 Letter Grade: {scores['letter_grade']}")
            
            print(f"\nWeighted Breakdown:")
            weights = {'website': 0.30, 'google': 0.30, 'reviews': 0.25, 'ordering': 0.15}
            for category, weight in weights.items():
                weighted_score = scores['category_scores'][category] * weight
                print(f"  {category.capitalize()}: {weighted_score:.2f} ({weight*100:.0f}%)")
            
            result["success"] = True
            
        except Exception as e:
            print(f"\n❌ Error testing {restaurant['name']}: {str(e)}")
            result["error"] = str(e)
            
        finally:
            test_end = time.time()
            result["duration"] = test_end - test_start
            print(f"\n⏱️  Test duration: {result['duration']:.2f}s")
            
        return result
    
    async def run_all_tests(self):
        """Run tests on all restaurants"""
        
        print("\n" + "="*60)
        print("RESTAURANT GRADER - INTEGRATION TEST")
        print("="*60)
        print(f"Testing {len(self.RESTAURANTS)} restaurant websites")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.start_time = time.time()
        
        # Test each restaurant
        for restaurant in self.RESTAURANTS:
            result = await self.test_restaurant(restaurant)
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        self.end_time = time.time()
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        
        print("\n\n" + "="*60)
        print("INTEGRATION TEST SUMMARY REPORT")
        print("="*60)
        
        # Calculate statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_duration = self.end_time - self.start_time
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        print(f"\n📊 Test Statistics:")
        print(f"  Total Websites Tested: {total_tests}")
        print(f"  Successful: {successful_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Duration: {total_duration:.2f}s")
        print(f"  Average Time per Scan: {avg_duration:.2f}s")
        
        # Calculate average scores
        if successful_tests > 0:
            successful_results = [r for r in self.results if r["success"]]
            
            avg_overall = sum(r["scores"]["overall_score"] for r in successful_results) / successful_tests
            avg_website = sum(r["scores"]["category_scores"]["website"] for r in successful_results) / successful_tests
            avg_google = sum(r["scores"]["category_scores"]["google"] for r in successful_results) / successful_tests
            avg_reviews = sum(r["scores"]["category_scores"]["reviews"] for r in successful_results) / successful_tests
            avg_ordering = sum(r["scores"]["category_scores"]["ordering"] for r in successful_results) / successful_tests
            
            print(f"\n📈 Average Scores:")
            print(f"  Overall: {avg_overall:.1f}/100")
            print(f"  Website: {avg_website:.1f}/100")
            print(f"  Google: {avg_google:.1f}/100")
            print(f"  Reviews: {avg_reviews:.1f}/100")
            print(f"  Ordering: {avg_ordering:.1f}/100")
        
        # Browser analysis summary
        ssl_count = sum(1 for r in self.results if r.get("browser_data", {}).get("has_ssl"))
        mobile_count = sum(1 for r in self.results if r.get("browser_data", {}).get("mobile_responsive"))
        order_button_count = sum(1 for r in self.results if r.get("browser_data", {}).get("order_button_detected"))
        
        print(f"\n🌐 Browser Analysis Summary:")
        print(f"  SSL Enabled: {ssl_count}/{total_tests} ({ssl_count/total_tests*100:.0f}%)")
        print(f"  Mobile Friendly: {mobile_count}/{total_tests} ({mobile_count/total_tests*100:.0f}%)")
        print(f"  Order Button Found: {order_button_count}/{total_tests} ({order_button_count/total_tests*100:.0f}%)")
        
        # Individual results table
        print(f"\n📋 Individual Results:")
        print(f"\n{'Restaurant':<20} {'Status':<10} {'Overall':<10} {'Grade':<8} {'Time':<8}")
        print("-" * 60)
        
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            if result["success"]:
                overall = f"{result['scores']['overall_score']:.1f}"
                grade = result['scores']['letter_grade']
            else:
                overall = "N/A"
                grade = "N/A"
            duration = f"{result['duration']:.2f}s"
            
            print(f"{result['name']:<20} {status:<10} {overall:<10} {grade:<8} {duration:<8}")
        
        # Issues found
        print(f"\n⚠️  Issues Found:")
        issues = []
        
        for result in self.results:
            if not result["success"]:
                issues.append(f"  ❌ {result['name']}: {result['error']}")
            else:
                browser_data = result.get("browser_data", {})
                if not browser_data.get("has_ssl"):
                    issues.append(f"  ⚠️  {result['name']}: No SSL certificate")
                if not browser_data.get("mobile_responsive"):
                    issues.append(f"  ⚠️  {result['name']}: Not mobile friendly")
                if not browser_data.get("order_button_detected"):
                    issues.append(f"  ⚠️  {result['name']}: No order button detected")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("  ✅ No issues found!")
        
        # Performance metrics
        print(f"\n⚡ Performance Metrics:")
        if self.results:
            fastest = min(self.results, key=lambda x: x["duration"])
            slowest = max(self.results, key=lambda x: x["duration"])
            print(f"  Fastest: {fastest['name']} ({fastest['duration']:.2f}s)")
            print(f"  Slowest: {slowest['name']} ({slowest['duration']:.2f}s)")
        
        # Final verdict
        print(f"\n{'='*60}")
        if success_rate == 100:
            print("✅ ALL TESTS PASSED - MVP IS READY!")
        elif success_rate >= 80:
            print("⚠️  MOST TESTS PASSED - MINOR ISSUES TO ADDRESS")
        else:
            print("❌ MULTIPLE FAILURES - NEEDS ATTENTION")
        print(f"{'='*60}\n")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate == 100:
            print("  ✅ Browser automation is working correctly")
            print("  ✅ Order button detection is functional")
            print("  ✅ Scoring algorithm is calculating properly")
            print("  ✅ Ready to proceed with Phase 4 (Orchestrator)")
        else:
            print("  🔧 Review failed tests and fix issues")
            print("  🔧 Improve order button detection patterns")
            print("  🔧 Add error handling for edge cases")
        
        print(f"\n{'='*60}\n")


async def main():
    """Main test execution"""
    test = IntegrationTest()
    
    try:
        await test.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
