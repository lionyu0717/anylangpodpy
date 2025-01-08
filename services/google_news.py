import feedparser
from datetime import datetime
import urllib.parse
from typing import Dict, Any, List, Optional
from utils.logger import logger
import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import base64
import re

class GoogleNewsService:
    def __init__(self, lang: str = 'en', country: str = 'US') -> None:
        """Initialize Google News service with language and country."""
        self.lang = lang
        self.country = country
        self.base_url = 'https://news.google.com/rss'
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': f'{self.lang}-{self.country},en-US;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            })

    async def _make_request(self, url: str) -> Optional[Dict]:
        """Make request to fetch RSS feed"""
        await self._ensure_session()
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    if feed and hasattr(feed, 'entries'):
                        logger.info(f"Successfully retrieved {len(feed.entries)} entries")
                        return feed
                    else:
                        logger.warning("Feed parsing returned no entries")
                else:
                    logger.error(f"Request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
        return None

    async def _extract_real_url(self, google_url: str) -> str:
        """Extract the actual URL from Google News redirect URL."""
        try:
            # First check if we're dealing with a consent URL
            if 'consent.google.com' in google_url:
                # Extract the continue parameter
                parsed = urllib.parse.urlparse(google_url)
                query_params = urllib.parse.parse_qs(parsed.query)
                if 'continue' in query_params:
                    google_url = query_params['continue'][0]

            if 'news.google.com' in google_url:
                # Extract article ID - handle both RSS and web URLs
                if '/articles/' in google_url:
                    article_id = google_url.split('/articles/')[1].split('?')[0]
                else:
                    return google_url
                
                # The article ID is base64 encoded and contains the actual URL
                try:
                    # First try standard base64
                    padded_id = article_id + '=' * (-len(article_id) % 4)
                    decoded = base64.b64decode(padded_id)
                    
                    # Look for URLs in the decoded content
                    url_match = re.search(br'https?://[^\s<>"]+', decoded)
                    if url_match:
                        url = url_match.group(0).decode('utf-8', errors='ignore')
                        if 'google.com' not in url:
                            return url
                    
                    # Try URL-safe base64
                    decoded = base64.urlsafe_b64decode(padded_id)
                    url_match = re.search(br'https?://[^\s<>"]+', decoded)
                    if url_match:
                        url = url_match.group(0).decode('utf-8', errors='ignore')
                        if 'google.com' not in url:
                            return url
                            
                except Exception as e:
                    logger.debug(f"Failed to decode article ID: {e}")
            
            return google_url
            
        except Exception as e:
            logger.error(f"Error extracting real URL: {e}")
            return google_url

    async def search(
        self,
        query: str,
        when: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search Google News."""
        try:
            # Format query parameters
            params = []
            
            # Add date range if specified
            if when:
                params.append(f'when:{when}')
            if from_date and to_date:
                params.append(f'after:{from_date} before:{to_date}')
            
            # Combine query with parameters
            full_query = f"{query} {' '.join(params)}".strip()
            encoded_query = urllib.parse.quote(full_query)
            
            # Construct URL
            url = f"{self.base_url}/search?q={encoded_query}&hl={self.lang}&gl={self.country}&ceid={self.country}:{self.lang}"
            
            feed = await self._make_request(url)
            if not feed:
                return {'feed': {}, 'entries': []}
            
            # Process entries to get real URLs
            entries = []
            for entry in feed.entries:
                entry_dict = dict(entry)
                if 'link' in entry_dict:
                    entry_dict['real_link'] = await self._extract_real_url(entry_dict['link'])
                entries.append(entry_dict)

            return {
                'feed': feed.feed,
                'entries': entries
            }
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {'feed': {}, 'entries': []}

    async def top_news(self) -> Dict[str, Any]:
        """Get top news."""
        try:
            url = f"{self.base_url}/headlines/section/topic/WORLD?hl={self.lang}&gl={self.country}&ceid={self.country}:{self.lang}"
            
            feed = await self._make_request(url)
            if not feed:
                return {'feed': {}, 'entries': []}
            
            # Process entries to get real URLs
            entries = []
            for entry in feed.entries:
                entry_dict = dict(entry)
                if 'link' in entry_dict:
                    entry_dict['real_link'] = await self._extract_real_url(entry_dict['link'])
                entries.append(entry_dict)
            
            return {
                'feed': feed.feed,
                'entries': entries
            }
            
        except Exception as e:
            logger.error(f"Top news fetch failed: {str(e)}")
            return {'feed': {}, 'entries': []}

    async def topic_headlines(self, topic: str) -> Dict[str, Any]:
        """Get topic headlines."""
        try:
            topic = topic.upper()
            url = f"{self.base_url}/headlines/section/topic/{topic}?hl={self.lang}&gl={self.country}&ceid={self.country}:{self.lang}"
            
            feed = await self._make_request(url)
            if not feed:
                return {'feed': {}, 'entries': []}
            
            # Process entries to get real URLs
            entries = []
            for entry in feed.entries:
                entry_dict = dict(entry)
                if 'link' in entry_dict:
                    entry_dict['real_link'] = await self._extract_real_url(entry_dict['link'])
                entries.append(entry_dict)
            
            return {
                'feed': feed.feed,
                'entries': entries
            }
            
        except Exception as e:
            logger.error(f"Topic headlines fetch failed: {str(e)}")
            return {'feed': {}, 'entries': []}

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None