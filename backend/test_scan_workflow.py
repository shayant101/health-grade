import asyncio
import httpx
from datetime import datetime

async def test_scan_workflow():
    """Test complete scan workflow through API"""
    base_url = "http://localhost:8000"
    
    # Test data
    scan_data = {
        "restaurant_name": "Chipotle",
        "restaurant_website": "https://www.chipotle.com",
        "restaurant_data": {}
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 1. Create scan
        print("Creating scan...")
        response = await client.post(f"{base_url}/api/scans/", json=scan_data)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ Failed to create scan: {response.status_code}")
            return
            
        result = response.json()
        scan_id = result["scan_id"]
        print(f"Scan created: {scan_id}")
        
        # 2. Poll for results
        print("Waiting for scan to complete...")
        for i in range(30):  # Wait up to 30 seconds
            await asyncio.sleep(1)
            response = await client.get(f"{base_url}/api/scans/{scan_id}")
            scan = response.json()
            status = scan["status"]
            print(f"Status: {status}")
            
            if status == "completed":
                print("\n✅ Scan completed!")
                print(f"Overall Score: {scan['results']['overall_score']}")
                print(f"Letter Grade: {scan['results']['letter_grade']}")
                break
            elif status == "failed":
                print(f"\n❌ Scan failed: {scan.get('error')}")
                break

if __name__ == "__main__":
    asyncio.run(test_scan_workflow())
