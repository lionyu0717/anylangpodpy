#!/root/news_test/jupyter_env/bin/python

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from services.gdelt import GDELTService
from services.text.text_generator import TextGenerator
from services.tts.google_tts import GoogleTTS
from services.scraper import Scraper
from config import get_config

class PodcastGenerator:
    def __init__(self):
        self.config = get_config()
        self.gdelt_service = GDELTService()
        self.text_generator = TextGenerator()
        self.tts_service = GoogleTTS()
        self.content_scraper = Scraper(self.config.JINA_CRAWLER_BASE_URL)

    async def generate_podcast_script(
        self,
        keyword: str,
        language_code: str = "en-GB",
        max_length: int = None
    ) -> str:
        try:
            # Get news articles from GDELT
            news_data = await self.gdelt_service.search_news(keyword)
            
            # Scrape content from URLs
            articles = []
            for article in news_data[:3]:  # Process top 3 articles
                content = await self.content_scraper.scrape_url(article.get("url", ""))
                if content:
                    articles.append({
                        "title": article.get("title", ""),
                        "content": content,
                        "source": article.get("source", "")
                    })
            
            if not articles:
                return f"No news found for the topic: {keyword}"
            
            # Create a summary prompt
            articles_text = "\n\n".join([
                f"Article from {article['source']}:\nTitle: {article['title']}\nContent: {article['content'][:500]}..."
                for article in articles
            ])
            
            prompt = f"""Create a podcast script about {keyword} based on these news articles:
            {articles_text}
            
            The script should be in a conversational tone and include:
            1. An engaging introduction
            2. Discussion of each news item, highlighting key points
            3. A thoughtful conclusion that ties everything together
            
            Make it engaging and informative, suitable for a podcast format."""
            
            # Generate the script
            script = await self.text_generator.generate(prompt)
            return script
            
        except Exception as e:
            print(f"Error generating podcast: {str(e)}")
            return f"Error generating podcast content: {str(e)}"

    async def generate_podcast_audio(
        self,
        text: str,
        output_path: str,
        language_code: str = "en-GB"
    ) -> None:
        """Generate audio from text using TTS."""
        await self.tts_service.text_to_speech(
            text=text,
            output_path=output_path,
            language_code=language_code
        )

async def generate_complete_podcast(
    topic: str,
    language_code: str = "en-GB",
    voice_name: str = None,
    output_dir: str = "output"
):
    """
    Generate a complete podcast from topic to audio
    """
    try:
        # Initialize generator
        generator = PodcastGenerator()
        
        # Generate script
        script = await generator.generate_podcast_script(topic, language_code)
        
        # Save script to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"podcast_{topic.lower().replace(' ', '_')}_{timestamp}.txt"
        script_path = Path(output_dir) / script_filename
        
        with open(script_path, "w") as f:
            f.write(script)
            
        # Generate audio
        audio_filename = f"tts_{language_code}_{timestamp}.mp3"
        audio_path = Path(output_dir) / audio_filename
        
        await generator.generate_podcast_audio(
            text=script,
            output_path=str(audio_path),
            language_code=language_code
        )
        
        return {
            "script_path": str(script_path),
            "audio_path": str(audio_path),
            "script": script
        }
        
    except Exception as e:
        print(f"Error in complete podcast generation: {str(e)}")
        return None

async def main():
    parser = argparse.ArgumentParser(description="Generate a podcast from a topic")
    parser.add_argument("topic", help="Topic to generate podcast about")
    parser.add_argument("--language", default="en-GB", help="Language code (default: en-GB)")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    
    args = parser.parse_args()
    
    result = await generate_complete_podcast(
        args.topic,
        language_code=args.language,
        output_dir=args.output_dir
    )
    
    if result:
        print(f"Generated podcast:")
        print(f"Script saved to: {result['script_path']}")
        print(f"Audio saved to: {result['audio_path']}")
    else:
        print("Failed to generate podcast")

if __name__ == "__main__":
    asyncio.run(main()) 