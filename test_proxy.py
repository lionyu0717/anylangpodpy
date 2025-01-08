import asyncio
import aiohttp
from utils.proxy_manager import ProxyManager
from utils.logger import logger

async def test_proxy_with_retries():
    proxy_manager = ProxyManager("http://localhost:5010")
    max_retries = 5
    timeout = aiohttp.ClientTimeout(total=5)  # Shorter timeout for faster testing
    
    print("\n=== Testing Proxy Manager ===\n")
    
    for attempt in range(max_retries):
        print(f"\nAttempt {attempt + 1}/{max_retries}")
        
        # Get a new proxy
        print("Getting proxy...")
        proxy = await proxy_manager.get_proxy()
        if not proxy:
            print("✗ Failed to get proxy")
            continue
            
        print(f"✓ Got proxy: {proxy}")
        
        # Test the proxy
        try:
            print("Testing proxy with httpbin.org...")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy.get("http"),
                    timeout=timeout,
                    ssl=False  # Sometimes needed for HTTPS proxies
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✓ Success! Your IP: {data['origin']}")
                        return True
                    
        except Exception as e:
            print(f"✗ Request failed: {str(e)[:100]}...")
            print("Deleting failed proxy...")
            await proxy_manager.delete_proxy(proxy)
            print("✓ Proxy deleted")
            
    print("\n✗ All retry attempts failed")
    return False

if __name__ == "__main__":
    asyncio.run(test_proxy_with_retries()) 