"""
Test script to verify Website-Only Analysis fixes.

Tests:
1. Invalid URL format → Should return 400
2. Non-existent domain → Should return 422
3. Complex site (Panera) → Should complete successfully
4. Valid site (Chipotle) → Should still work as before
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_invalid_url():
    """Test 1: Invalid URL should return 400"""
    print("\n" + "="*60)
    print("TEST 1: Invalid URL Format")
    print("="*60)
    
    test_cases = [
        "not-a-url",
        "just some text",
        "ftp://invalid-protocol.com",
        "",
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for url in test_cases:
            print(f"\nTesting: '{url}'")
            try:
                response = await client.post(
                    f"{BASE_URL}/api/website/analyze",
                    json={"url": url}
                )
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.json()}")
                
                if response.status_code == 422:
                    print("✅ PASS - Returned 422 (validation error)")
                else:
                    print(f"❌ FAIL - Expected 422, got {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")

async def test_nonexistent_domain():
    """Test 2: Non-existent domain should return 422"""
    print("\n" + "="*60)
    print("TEST 2: Non-existent Domain")
    print("="*60)
    
    test_url = "https://thisdoesnotexist12345xyz.com"
    print(f"\nTesting: {test_url}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/website/analyze",
                json={"url": test_url}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 422:
                print("✅ PASS - Returned 422 (unreachable)")
            else:
                print(f"❌ FAIL - Expected 422, got {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

async def test_complex_site():
    """Test 3: Complex site (Panera) should complete successfully"""
    print("\n" + "="*60)
    print("TEST 3: Complex Site (Panera)")
    print("="*60)
    
    test_url = "https://panera.com"
    print(f"\nTesting: {test_url}")
    print("This may take up to 30 seconds...")
    
    start_time = datetime.now()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/website/analyze",
                json={"url": test_url}
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\nCompleted in {elapsed:.1f} seconds")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS - Analysis completed successfully")
                print(f"   Website Score: {data.get('website_score', 0):.1f}")
                print(f"   Status: {data.get('status')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                
                # Check that analysis_data is not empty
                analysis_data = data.get('analysis_data', {})
                if analysis_data and len(analysis_data) > 0:
                    print(f"   Analysis Data Keys: {list(analysis_data.keys())}")
                    print("✅ Analysis data is populated")
                else:
                    print("❌ FAIL - Analysis data is empty")
            else:
                print(f"❌ FAIL - Expected 200, got {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

async def test_valid_site():
    """Test 4: Valid site (Chipotle) should work as before"""
    print("\n" + "="*60)
    print("TEST 4: Valid Site (Chipotle)")
    print("="*60)
    
    test_url = "https://chipotle.com"
    print(f"\nTesting: {test_url}")
    
    start_time = datetime.now()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/website/analyze",
                json={"url": test_url}
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\nCompleted in {elapsed:.1f} seconds")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS - Analysis completed successfully")
                print(f"   Website Score: {data.get('website_score', 0):.1f}")
                print(f"   Status: {data.get('status')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                
                # Check that analysis_data is not empty
                analysis_data = data.get('analysis_data', {})
                if analysis_data and len(analysis_data) > 0:
                    print(f"   Analysis Data Keys: {list(analysis_data.keys())}")
                    print("✅ Analysis data is populated")
                else:
                    print("❌ FAIL - Analysis data is empty")
            else:
                print(f"❌ FAIL - Expected 200, got {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WEBSITE-ONLY ANALYSIS FIXES - TEST SUITE")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests sequentially
    await test_invalid_url()
    await test_nonexistent_domain()
    await test_complex_site()
    await test_valid_site()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSummary:")
    print("- Test 1: Invalid URL format validation")
    print("- Test 2: Non-existent domain handling")
    print("- Test 3: Complex site timeout handling")
    print("- Test 4: Valid site functionality")

if __name__ == "__main__":
    asyncio.run(main())
