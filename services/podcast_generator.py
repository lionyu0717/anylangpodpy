from typing import List, Dict
import asyncio
from pathlib import Path
from datetime import datetime

from .gdelt import GDELTService
from .scraper import Scraper
from .text.text_generator import TextGenerator
from utils.cleaner import clean_text
from config import get_config

class PodcastGenerator:
    # Language mapping for more natural language names
    LANGUAGE_NAMES = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese"
    }
    
    def __init__(self):
        self.config = get_config()
        self.gdelt_service = GDELTService()
        self.content_scraper = Scraper(self.config.JINA_CRAWLER_BASE_URL)
        self.text_generator = TextGenerator()
        
    async def _load_prompt_template(self) -> str:
        prompt_path = Path("services/prompts/podcast.txt")
        with open(prompt_path, "r") as f:
            return f.read()
            
    async def _collect_news_and_content(self, topic: str, max_articles: int = 5) -> List[Dict]:
        """Collect news articles and their content about the topic using GDELT"""
        try:
            # Get news articles from GDELT
            news_articles = await self.gdelt_service.search_news(topic, max_results=max_articles)
            
            # Scrape full content for each article
            articles_with_content = []
            for article in news_articles:
                try:
                    result = await self.content_scraper.fetch_content(
                        url=article["url"],
                        keyword=topic,
                        title=article["title"]
                    )
                    if result["content"]:
                        articles_with_content.append({
                            "title": article["title"],
                            "content": clean_text(result["content"]),
                            "link": article["url"],
                            "source": article.get("source", "Unknown Source")
                        })
                except Exception as e:
                    print(f"Error scraping content for {article['url']}: {str(e)}")
                    continue
                    
            return articles_with_content
        finally:
            # Clean up resources
            await self.gdelt_service.close()
            await self.content_scraper.close()
        
    async def _prepare_content_summary(self, articles: List[Dict]) -> str:
        """Prepare a consolidated summary of all articles"""
        combined_content = []
        for article in articles:
            combined_content.append(f"Article from {article['source']}: {article['title']}\n{article['content']}\n")
        
        return "\n\n".join(combined_content)
        
    async def generate_podcast_script(self, topic: str, language_code: str = "en-GB") -> str:
        """Generate a podcast script about the given topic in the specified language"""
        try:
            # Load the prompt template
            prompt_template = await self._load_prompt_template()
            
            # Get language name from code
            lang_prefix = language_code.split('-')[0]
            language_name = self.LANGUAGE_NAMES.get(lang_prefix, "English")
            
            # Collect news and content
            articles = await self._collect_news_and_content(topic)
            if not articles:
                raise ValueError(f"No articles found for topic: {topic}")
                
            # Prepare content summary
            content_summary = await self._prepare_content_summary(articles)
            
            # Generate podcast script using the template
            prompt = (prompt_template
                     .replace("{topic}", topic)
                     .replace("{language}", language_name)
                     .replace("{content}", content_summary))
            
            # Generate the script using AI
            podcast_script = await self.text_generator.generate(prompt)
            
            return podcast_script
        except Exception as e:
            raise e
        
    async def save_podcast_script(self, topic: str, script: str):
        """Save the generated podcast script to a file"""
        # Clean the script of any formatting markers
        script = script.replace("================================================================================", "")
        script = script.strip()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/podcast_{topic.replace(' ', '_')}_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(script)
        
        return filename 