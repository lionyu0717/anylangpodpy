from services.google_news import GoogleNewsService
import asyncio

async def main():
    news_service = GoogleNewsService()
    
    # Search with proxies
    results = await news_service.search(
        query="artificial intelligence",
        when="7d"  # Last 7 days
    )

    print(results)
    
    # Get top news
    top_news = await news_service.top_news()
    
    # Get topic headlines
    tech_news = await news_service.topic_headlines("TECHNOLOGY")

if __name__ == "__main__":
    asyncio.run(main())