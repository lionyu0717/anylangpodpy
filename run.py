import asyncio
from services.gdelt import GDELTService
from services.scraper import Scraper
from utils.logger import logger
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def main():
    gdelt = GDELTService(proxy_enabled=True)
    jina_url = os.getenv('JINA_CRAWLER_BASE_URL')
    if not jina_url:
        logger.error("JINA_CRAWLER_BASE_URL not found in .env file")
        return
    scraper = Scraper(jina_base_url=jina_url)
    
    try:
        # Get GDELT results
        results = await gdelt.search('Haoshan OR Genius')
        if not results:
            logger.warning("No GDELT results found")
            return

        articles = results.get('articles', [])
        logger.info(f"Found {len(articles)} articles in GDELT")
        
        # Take first 5 articles
        articles_to_scrape = articles[:5]
        
        # Prepare lists for scraper
        urls = [article.get('url') for article in articles_to_scrape]
        titles = [article.get('title', 'No title') for article in articles_to_scrape]
        keyword = 'Donald Trump OR Hong Kong'  # Using the same search query
        
        # Scrape the articles
        logger.info(f"Starting to scrape {len(urls)} articles...")
        scraped_results = await scraper.fetch_multiple(urls, keyword, titles)
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save GDELT results
        gdelt_filename = f"{output_dir}/gdelt_results_{timestamp}.csv"
        with open(gdelt_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'url', 'timestamp'])
            writer.writeheader()
            for article in articles_to_scrape:
                writer.writerow({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'timestamp': article.get('timestamp', '')
                })
        
        # Save scraped content
        content_filename = f"{output_dir}/scraped_content_{timestamp}.csv"
        with open(content_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['keyword', 'title', 'link', 'content', 'status', 'error'])
            writer.writeheader()
            for result in scraped_results:
                writer.writerow(result)
        
        logger.info(f"Results saved to {gdelt_filename} and {content_filename}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        await gdelt.close()

if __name__ == "__main__":
    asyncio.run(main())