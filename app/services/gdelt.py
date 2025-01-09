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
        logger.info(f"Initializing GDELTService with proxy_enabled={proxy_enabled}")
        
        if proxy_enabled:
            try:
                self.proxy_manager = ProxyManager("http://localhost:5010")
                # Test proxy connection
                asyncio.create_task(self._test_proxy_connection())
            except Exception as e:
                logger.error(f"Failed to initialize proxy manager: {str(e)}")
                self.proxy_enabled = False
        self.session = None

    async def _test_proxy_connection(self):
        """Test if proxy service is available"""
        try:
            proxy = await self.proxy_manager.get_proxy()
            if proxy:
                logger.info("Successfully connected to proxy service")
                await self.proxy_manager.delete_proxy(proxy)
            else:
                logger.error("Proxy service returned no proxies")
                self.proxy_enabled = False
        except Exception as e:
            logger.error(f"Proxy service test failed: {str(e)}")
            self.proxy_enabled = False

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            logger.info("Creating new aiohttp session")
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
                if self.proxy_enabled and attempt < 2:
                    logger.info(f"Attempt {attempt + 1}: Getting proxy from service")
                    proxy_dict = await self.proxy_manager.get_proxy()
                    if proxy_dict:
                        logger.info(f"Using proxy: {proxy_dict['http']}")
                    else:
                        logger.warning("No proxy available, falling back to direct connection")
                else:
                    logger.info(f"Attempt {attempt + 1}: Using direct connection")
                
                timeout = aiohttp.ClientTimeout(
                    total=60,
                    connect=20,
                    sock_read=30
                )
                
                logger.info(f"Making request to: {url}")
                request_start = time.time()
                async with self.session.get(
                    url, 
                    proxy=proxy_dict["http"] if proxy_dict else None,
                    ssl=False,
                    timeout=timeout,
                    allow_redirects=True
                ) as response:
                    request_time = time.time() - request_start
                    logger.info(f"Request completed in {request_time:.2f}s with status: {response.status}")
                    
                    content = await response.text()
                    logger.debug(f"Response content preview: {content[:200]}")
                    
                    if response.status == 200 and content:
                        try:
                            data = json.loads(content)
                            if data:
                                logger.info(f"Successfully parsed JSON response on attempt {attempt + 1}")
                                return data
                            else:
                                logger.warning("Received empty JSON response")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON parse error: {str(e)}")
                            logger.debug(f"Failed content: {content[:500]}")
                    else:
                        logger.error(f"HTTP {response.status}: {content[:200]}")
                        if proxy_dict:
                            logger.info(f"Removing failed proxy: {proxy_dict['http']}")
                            await self.proxy_manager.delete_proxy(proxy_dict)
                            
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout after {timeout.total}s on attempt {attempt + 1}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            except aiohttp.ClientError as e:
                logger.error(f"HTTP client error on attempt {attempt + 1}: {str(e)}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if proxy_dict:
                    await self.proxy_manager.delete_proxy(proxy_dict)
            
            logger.info(f"Waiting 2s before retry {attempt + 2}/{max_retries}")
            await asyncio.sleep(2)
        
        logger.error(f"All {max_retries} retry attempts failed")
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
                quoted_terms = [f'"{term}"' for term in terms]
                query = f"({' OR '.join(quoted_terms)})"
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
            quoted_keywords = [f'"{k}"' for k in keywords]
            query = f"({' OR '.join(quoted_keywords)})"
            
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
            # Clean and validate the topic
            topic = topic.strip()
            if len(topic) < 4:  # GDELT requires longer phrases
                topic = f"{topic} news"  # Append 'news' to make it longer
                logger.info(f"Topic too short, modified to: {topic}")
            
            # Format query for GDELT with proper escaping
            query = f'"{topic}"'
            if ' ' in topic:  # If topic has spaces, add an OR condition with hyphenated version
                hyphenated = topic.replace(' ', '-')
                query = f'("{topic}" OR "{hyphenated}")'
            
            search_params = {
                'query': query,
                'mode': 'artlist',
                'format': 'json',
                'timespan': '7d',
                'maxrecords': max_results * 2,  # Get more results than needed in case some fail
                'sort': 'DateDesc',
                'trans': 'googtrans',
                'SHOWSOURCES': 'yes'
            }
            
            url = f"{self.base_url}?{urlencode(search_params)}"
            logger.info(f"Using query: {query}")
            logger.info(f"Full URL: {url}")
            
            results = await self._make_request(url)
            
            if isinstance(results, str) and "too short" in results.lower():
                logger.error("GDELT rejected query as too short")
                return []
                
            if not results:
                logger.error("No results returned from GDELT")
                return []
                
            if isinstance(results, str):
                logger.error(f"Unexpected string response from GDELT: {results}")
                return []
                
            if 'articles' not in results:
                logger.error("No articles found in GDELT response")
                return []
                
            # Process and format the articles
            formatted_articles = []
            for article in results['articles'][:max_results]:
                try:
                    formatted_article = {
                        "title": article.get('title', '').strip(),
                        "url": article.get('url', ''),
                        "source": article.get('sourcecountry', 'Unknown'),
                        "date": article.get('seendate', '')
                    }
                    # Only add articles with non-empty titles and URLs
                    if formatted_article["title"] and formatted_article["url"]:
                        formatted_articles.append(formatted_article)
                    else:
                        logger.warning(f"Skipping article with missing title or URL: {article}")
                except Exception as e:
                    logger.error(f"Error formatting article: {str(e)}")
                    continue
                
            logger.info(f"Found {len(formatted_articles)} valid articles")
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error in search_news: {str(e)}")
            return []
