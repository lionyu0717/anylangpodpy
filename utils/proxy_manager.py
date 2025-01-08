import aiohttp
from typing import Optional, Dict
from utils.logger import logger

class ProxyManager:
    def __init__(self, proxy_pool_url: str = "http://127.0.0.1:5010") -> None:
        self.proxy_pool_url = proxy_pool_url

    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a proxy with HTTPS support"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.proxy_pool_url}/get?type=https") as response:
                    if response.status == 200:
                        proxy_data = await response.json()
                        proxy_str = proxy_data.get("proxy")
                        if proxy_str:
                            return {
                                "http": f"http://{proxy_str}",
                                "https": f"http://{proxy_str}"
                            }
        except Exception as e:
            logger.error(f"Error getting proxy: {str(e)}")
        return None

    async def delete_proxy(self, proxy: Dict[str, str]) -> None:
        """Delete a failed proxy"""
        try:
            proxy_str = proxy["http"].replace("http://", "")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.proxy_pool_url}/delete/?proxy={proxy_str}") as response:
                    if response.status != 200:
                        logger.error(f"Failed to delete proxy: {proxy_str}")
        except Exception as e:
            logger.error(f"Error deleting proxy: {str(e)}")