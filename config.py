import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuration class for environment variables."""
    
    # Jina Crawler settings
    JINA_CRAWLER_BASE_URL: str = os.getenv('JINA_CRAWLER_BASE_URL', 'http://localhost:3000/')
    
    # GDELT settings
    GDELT_VERSION: int = int(os.getenv('GDELT_VERSION', '2'))
    
    # Scraping settings
    MAX_URLS_TO_SCRAPE: int = int(os.getenv('MAX_URLS_TO_SCRAPE', '10'))
    
    # Output settings
    OUTPUT_DIR: str = os.getenv('OUTPUT_DIR', 'output')
    
    # Deepseek API settings
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_BASE_URL: str = "https://api.deepseek.com"
    
    # Google Cloud settings
    GOOGLE_CLOUD_API_KEY: str = os.getenv('GOOGLE_CLOUD_API_KEY', '')

def get_config() -> Config:
    """Get configuration instance.
    
    Returns:
        Config: Configuration instance with environment variables.
    """
    return Config() 