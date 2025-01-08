import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import pandas as pd
from urllib.parse import quote, urlencode
from utils.logger import logger
import asyncio
import time
from utils.proxy_manager import ProxyManager
import aiohttp
import json

class GDELTService:
    def __init__(self, proxy_enabled: bool = True):
        """Initialize GDELT DOC 2.0 API service."""
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.proxy_enabled = proxy_enabled
        if proxy_enabled:
            self.proxy_manager = ProxyManager("http://localhost:5010")
        self.session = None  # Initialize session in async context

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': 'Mozilla/5.0 (compatible; GDELTBot/1.0; +https://www.gdeltproject.org/)',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Origin': 'https://www.gdeltproject.org',
                'Connection': 'keep-alive'
            })

    async def _make_request(self, url: str) -> Optional[Dict]:
        """Make request with retries"""
        await self._ensure_session()
        max_retries = 3
        
        for attempt in range(max_retries):
            proxy_dict = None
            try:
                if self.proxy_enabled and attempt < 2:  # Try first two attempts with proxy
                    proxy_dict = await self.proxy_manager.get_proxy()
                    if proxy_dict:
                        logger.info(f"Attempt {attempt + 1} with proxy: {proxy_dict}")
                    else:
                        logger.warning("Failed to get proxy, trying without proxy...")
                else:
                    logger.info("Attempting without proxy...")
                
                timeout = aiohttp.ClientTimeout(
                    total=60,
                    connect=20,
                    sock_read=30
                )
                
                logger.info(f"Making request to {url}")
                async with self.session.get(
                    url, 
                    proxy=proxy_dict["http"] if proxy_dict else None,
                    ssl=False,
                    timeout=timeout,
                    allow_redirects=True
                ) as response:
                    logger.info(f"Got response with status: {response.status}")
                    
                    # Read the raw content first
                    content = await response.text()
                    logger.info(f"Response content (first 200 chars): {content[:200]}")
                    
                    if response.status == 200 and content:
                        try:
                            data = json.loads(content)
                            if data:
                                logger.info(f"Successfully retrieved data (attempt {attempt + 1})")
                                return data
                            else:
                                logger.warning("Parsed JSON is empty")
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON response: {str(e)}")
                            logger.error(f"Raw content: {content[:500]}")
                    else:
                        logger.error(f"GDELT API error {response.status}: {content[:200]}")
                        if proxy_dict:
                            await self.proxy_manager.delete_proxy(proxy_dict)
                            logger.info("Deleted failed proxy")
                            
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout error on attempt {attempt + 1}: {str(e)}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            except aiohttp.ClientError as e:
                logger.error(f"Client error on attempt {attempt + 1}: {str(e)}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            
            await asyncio.sleep(2)
        
        logger.error("All retry attempts failed")
        return None

    async def search(self, query: str, **params) -> Optional[Dict[str, Any]]:
        """Search GDELT news articles"""
        try:
            # Format query string according to GDELT rules
            # Split on AND/OR and clean up each term
            terms = [term.strip() for term in query.replace(' AND ', ' OR ').split(' OR ')]
            
            # Filter out empty terms and ensure minimum length
            terms = [term for term in terms if len(term) >= 3]
            
            if not terms:
                logger.error("Query too short or empty after processing")
                return None
                
            # For multiple terms, wrap each in quotes and join with OR
            if len(terms) > 1:
                query = f'({" OR ".join(f'"{term}"' for term in terms)})'
            else:
                query = f'"{terms[0]}"'
            
            search_params = {
                'query': query,
                'mode': 'artlist',
                'format': 'json',
                'timespan': params.get('timespan', '7d'),
                'maxrecords': params.get('maxrecords', 250),
                'sort': params.get('sort', 'DateDesc'),  # Changed to date-based sorting
                'trans': params.get('trans', 'googtrans'),
                'SHOWSOURCES': 'yes'  # Added to get source information
            }
            
            url = f"{self.base_url}?{urlencode(search_params)}"
            logger.info(f"Using query: {query}")
            logger.info("Querying GDELT API...")
            
            return await self._make_request(url)

        except Exception as e:
            logger.error(f"Error in GDELT search: {str(e)}")
            return None

    async def get_timeline(
        self,
        keywords: List[str],
        timespan: str = "7d",
        mode: str = "timelinevolinfo"
    ) -> Dict:
        """Get timeline visualization data."""
        try:
            # Format query string with proper OR syntax in parentheses
            query = f'({" OR ".join(f'"{k}"' for k in keywords)})'
            
            params = {
                "query": query,
                "mode": mode,
                "format": "json",
                "timespan": timespan,
                "timezoom": "yes",
                "TIMELINESMOOTH": "5"  # Add timeline smoothing
            }
            
            url = f"{self.base_url}?{urlencode(params)}"
            return await self._make_request(url)
            
        except Exception as e:
            logger.error(f"Error getting timeline: {str(e)}")
            return {}

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def search_news(self, topic: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search for news articles about a topic and return in a standardized format"""
        try:
            # Search GDELT with our parameters
            results = await self.search(
                query=topic,
                timespan="7d",  # Last 7 days
                maxrecords=max_results * 2  # Get more results than needed in case some fail
            )
            
            if not results or 'articles' not in results:
                logger.error("No articles found in GDELT response")
                return []
                
            # Process and format the articles
            formatted_articles = []
            for article in results['articles'][:max_results]:
                formatted_articles.append({
                    "title": article.get('title', ''),
                    "url": article.get('url', ''),
                    "source": article.get('sourcecountry', 'Unknown'),
                    "published": article.get('seendate', '')
                })
                
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error in search_news: {str(e)}")
            return []
