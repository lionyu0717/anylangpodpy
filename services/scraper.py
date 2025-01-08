import aiohttp
from typing import Dict, Any, List
from utils.logger import logger
import asyncio
from aiohttp import ClientTimeout
import json
import random

class Scraper:
    def __init__(self, jina_base_url: str):
        """Initialize scraper with Jina base URL."""
        self.jina_base_url = jina_base_url.rstrip('/')  # Remove trailing slash if present
        self.session = None
        self.timeout = ClientTimeout(total=60)  # Increase timeout to 60 seconds
        self._last_request_time = 0
        self._min_request_interval = 1  # Minimum seconds between requests
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(ssl=False, force_close=True)
            )

    async def _wait_for_rate_limit(self):
        """Ensure we don't send requests too quickly"""
        now = asyncio.get_event_loop().time()
        if now - self._last_request_time < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - (now - self._last_request_time))
        self._last_request_time = now
            
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def fetch_content(self, url: str, keyword: str, title: str, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch webpage content using Jina scraper."""
        last_error = None
        await self._ensure_session()
        
        for attempt in range(max_retries):
            try:
                # Wait for rate limiting
                await self._wait_for_rate_limit()
                
                scraper_url = f'{self.jina_base_url}/{url}'
                logger.info(f"Requesting URL (attempt {attempt + 1}): {scraper_url}")
                
                async with self.session.get(scraper_url) as response:
                    response.raise_for_status()
                    text = await response.text()
                    
                    # Log response details for debugging
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    logger.info(f"Response content (first 200 chars): {text[:200]}")
                    
                    if not text.strip():
                        raise ValueError("Empty response received")
                        
                    return {
                        'keyword': keyword,
                        'title': title,
                        'content': text,
                        'link': url,
                        'status': 'success'
                    }
                    
            except aiohttp.ClientError as e:
                last_error = e
                logger.error(f"Network error for {url} (attempt {attempt + 1}): {str(e)}")
            except ValueError as e:
                last_error = e
                logger.error(f"Value error for {url} (attempt {attempt + 1}): {str(e)}")
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error for {url} (attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = (2 ** attempt) + (random.random() * 0.1)
                await asyncio.sleep(delay)
                await self.close()  # Close and create new session for retry
        
        # If we get here, all retries failed
        return {
            'keyword': keyword,
            'title': title,
            'content': '',
            'link': url,
            'status': 'error',
            'error': str(last_error) if last_error else "Maximum retries exceeded"
        }

    async def fetch_multiple(self, urls: List[str], keyword: str, titles: List[str]) -> List[Dict[str, Any]]:
        """Fetch content from multiple URLs."""
        try:
            results = []
            for url, title in zip(urls, titles):
                content = await self.fetch_content(url, keyword, title)
                results.append(content)
            return results
        finally:
            await self.close()  # Ensure session is closed after all requests
