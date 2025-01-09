import asyncio
import aiohttp
import json
from typing import Dict, Any
import time

async def test_endpoint(session: aiohttp.ClientSession, method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        if method.upper() == 'GET':
            async with session.get(url) as response:
                return {
                    'status': response.status,
                    'data': await response.text(),
                    'headers': dict(response.headers)
                }
        elif method.upper() == 'POST':
            async with session.post(url, json=data) as response:
                return {
                    'status': response.status,
                    'data': await response.text(),
                    'headers': dict(response.headers)
                }
    except Exception as e:
        return {'status': 'error', 'data': str(e)}

async def test_podcast_api():
    base_url = "http://localhost:8088"
    
    async with aiohttp.ClientSession() as session:
        print("\n1. Testing root endpoint...")
        result = await test_endpoint(session, 'GET', f"{base_url}/")
        print(f"Status: {result['status']}")
        print(f"Response: {result['data'][:100]}...")

        print("\n2. Testing news endpoint...")
        result = await test_endpoint(session, 'GET', f"{base_url}/api/podcast/news/AI")
        print(f"Status: {result['status']}")
        print(f"Response: {result['data']}")

        print("\n3. Testing podcast generation...")
        test_data = {
            "keyword": "AI technology",
            "max_length": 500,
            "language_code": "en-GB"
        }
        result = await test_endpoint(session, 'POST', f"{base_url}/api/podcast/generate", test_data)
        print(f"Status: {result['status']}")
        print(f"Response: {result['data']}")
        
        # If generation started successfully, poll for status
        try:
            response_data = json.loads(result['data'])
            if 'request_id' in response_data:
                print("\n4. Polling podcast status...")
                for _ in range(5):  # Poll 5 times
                    status_result = await test_endpoint(
                        session, 
                        'GET', 
                        f"{base_url}/api/podcast/status/{response_data['request_id']}"
                    )
                    print(f"Status check result: {status_result['data']}")
                    if '"status":"success"' in status_result['data']:
                        break
                    time.sleep(5)  # Wait 5 seconds between polls
        except Exception as e:
            print(f"Error polling status: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_podcast_api()) 