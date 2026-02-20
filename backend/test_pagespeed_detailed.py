"""
Test script to examine the full PageSpeed API response structure.
"""
import asyncio
import httpx
import json
from app.config import settings

async def test_pagespeed_detailed():
    """Test PageSpeed API and examine full response"""
    
    test_url = "https://nizariospizzaandgrill.com/"
    pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    print(f"Testing PageSpeed API with URL: {test_url}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            params = {
                'url': test_url,
                'key': settings.PAGESPEED_API_KEY,
                'strategy': 'MOBILE'
            }
            
            # Add multiple categories as separate parameters
            params_list = [
                ('url', test_url),
                ('key', settings.PAGESPEED_API_KEY),
                ('strategy', 'MOBILE'),
                ('category', 'PERFORMANCE'),
                ('category', 'ACCESSIBILITY'),
                ('category', 'BEST_PRACTICES'),
                ('category', 'SEO')
            ]
            
            print("Making API request...")
            response = await client.get(pagespeed_url, params=params_list)
            
            if response.status_code == 200:
                data = response.json()
                
                # Save full response for inspection
                with open('pagespeed_response.json', 'w') as f:
                    json.dump(data, f, indent=2)
                
                print("✅ Full response saved to pagespeed_response.json")
                
                # Extract key metrics
                lighthouse_result = data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                
                print("\nCategories found:")
                for cat_name, cat_data in categories.items():
                    score = cat_data.get('score', 0)
                    print(f"  {cat_name}: {score}")
                
                print("\nExtracted Scores:")
                performance_score = categories.get('performance', {}).get('score', 0) * 100
                accessibility_score = categories.get('accessibility', {}).get('score', 0) * 100
                best_practices_score = categories.get('best-practices', {}).get('score', 0) * 100
                seo_score = categories.get('seo', {}).get('score', 0) * 100
                
                print(f"Performance: {performance_score:.1f}/100")
                print(f"Accessibility: {accessibility_score:.1f}/100")
                print(f"Best Practices: {best_practices_score:.1f}/100")
                print(f"SEO: {seo_score:.1f}/100")
                
                # Check audits
                audits = lighthouse_result.get('audits', {})
                print(f"\nTotal audits: {len(audits)}")
                
                # Check for interactive timing
                if 'interactive' in audits:
                    interactive = audits['interactive']
                    print(f"Interactive timing: {interactive.get('numericValue', 'N/A')}ms")
                
                return True
            else:
                print(f"❌ Failed with status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pagespeed_detailed())
    exit(0 if success else 1)
