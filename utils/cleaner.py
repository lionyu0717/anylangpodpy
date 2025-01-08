import re
from urllib.parse import urlparse, parse_qs
from typing import Dict

class TextCleaner:
    @staticmethod
    def clean_title(title: str) -> str:
        """Clean HTML and special characters from title."""
        cleanr = re.compile('<.*?>')
        clean_title = re.sub(cleanr, '', title)
        clean_title = clean_title.replace("<b>", "").replace("</b>", "").replace("&quot;", "")
        return clean_title

    @staticmethod
    def clean_link(url: str) -> str:
        """Extract actual URL from Google redirect URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params['url'][0] if 'url' in query_params else url

    @staticmethod
    def clean_article(article: Dict) -> Dict:
        """Clean all fields of an article."""
        cleaned_article = {
            'title': TextCleaner.clean_title(article['title']),
            'published': article['published'],
            'link': TextCleaner.clean_link(article['link']),
        }
        return cleaned_article

def clean_text(text: str) -> str:
    """Clean HTML and special characters from text content."""
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    text = re.sub(cleanr, '', text)
    
    # Remove special characters and normalize whitespace
    text = re.sub(r'[\n\r\t]+', ' ', text)  # Replace newlines and tabs with space
    text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    
    return text.strip() 