"""
Test script to verify PageSpeed API integration with the new API key.
"""
import asyncio
import httpx
import traceback
from app.config import settings

async def test_pagespeed_api():
    """Test PageSpeed API with a real website"""
    
    test_url = "https://nizariospizzaandgrill.com/"
    pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    print(f"Testing PageSpeed API with URL: {test_url}")
    print(f"API Key (first 10 chars): {settings.PAGESPEED_API_KEY[:10]}...")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            params = {
                'url': test_url,
                'key': settings.PAGESPEED_API_KEY,
                'strategy': 'MOBILE'
            }
            
            print("Making API request...")
            response = await client.get(pagespeed_url, params=params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics
                lighthouse_result = data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                
                performance_score = categories.get('performance', {}).get('score', 0) * 100
                accessibility_score = categories.get('accessibility', {}).get('score', 0) * 100
                best_practices_score = categories.get('best-practices', {}).get('score', 0) * 100
                seo_score = categories.get('seo', {}).get('score', 0) * 100
                loading_time_ms = lighthouse_result.get('audits', {}).get('interactive', {}).get('numericValue', 0)
                
                print("\n✅ PageSpeed API Test SUCCESSFUL!")
                print("-" * 60)
                print(f"Performance Score: {performance_score:.1f}/100")
                print(f"Accessibility Score: {accessibility_score:.1f}/100")
                print(f"Best Practices Score: {best_practices_score:.1f}/100")
                print(f"SEO Score: {seo_score:.1f}/100")
                print(f"Loading Time: {loading_time_ms:.0f}ms")
                print("-" * 60)
                
                return True
            else:
                print(f"\n❌ PageSpeed API Test FAILED!")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"\n❌ PageSpeed API Test FAILED with exception!")
        print(f"Error: {e}")
        print(f"Error Type: {type(e).__name__}")
        print("\nFull Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pagespeed_api())
    exit(0 if success else 1)
