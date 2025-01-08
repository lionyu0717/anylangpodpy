import asyncio
from services.google_news import GoogleNewsService
from utils.logger import logger

async def test_google_news():
    news_service = GoogleNewsService()
    try:
        print("\n=== Testing Google News Search ===\n")
        results = await news_service.search(
            query="artificial intelligence",
            when="7d"  # Last 7 days
        )
        
        if results['entries']:
            print(f"Found {len(results['entries'])} articles")
            for entry in results['entries'][:5]:
                print(f"\nTitle: {entry.get('title', 'No title')}")
                print(f"Original Link: {entry.get('link', 'No link')}")
                print(f"Real Link: {entry.get('real_link', 'No real link')}")
        else:
            print("No results found")
            
        print("\n=== Testing Top News ===\n")
        top_news = await news_service.top_news()
        if top_news['entries']:
            print(f"Found {len(top_news['entries'])} top news articles")
            for entry in top_news['entries'][:5]:
                print(f"\nTitle: {entry.get('title', 'No title')}")
                print(f"Original Link: {entry.get('link', 'No link')}")
                print(f"Real Link: {entry.get('real_link', 'No real link')}")
        else:
            print("No top news found")
            
        print("\n=== Testing Tech Headlines ===\n")
        tech_news = await news_service.topic_headlines("TECHNOLOGY")
        if tech_news['entries']:
            print(f"Found {len(tech_news['entries'])} tech articles")
            for entry in tech_news['entries'][:5]:
                print(f"\nTitle: {entry.get('title', 'No title')}")
                print(f"Original Link: {entry.get('link', 'No link')}")
                print(f"Real Link: {entry.get('real_link', 'No real link')}")
        else:
            print("No tech news found")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        await news_service.close()

if __name__ == "__main__":
    asyncio.run(test_google_news()) 