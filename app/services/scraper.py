import aiohttp
from typing import Dict, Any, List
from utils.logger import logger
import asyncio
from aiohttp import ClientTimeout
import json
import random
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, jina_base_url: str = None):
        """Initialize scraper."""
        self.session = None
        self.timeout = ClientTimeout(total=30)
        self._last_request_time = 0
        self._min_request_interval = 1  # Minimum seconds between requests
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
    
    async def _wait_for_rate_limit(self):
        """Implement rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = current_time
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def scrape_url(self, url: str) -> str:
        """Scrape content from a URL."""
        try:
            await self._ensure_session()
            await self._wait_for_rate_limit()
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch URL {url}: Status {response.status}")
                    return ""
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text and clean it up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length
                return text[:5000]  # Return first 5000 characters
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return ""
