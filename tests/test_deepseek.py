from dotenv import load_dotenv
import os
from services.text.text_generator import test_deepseek_api

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Verify API key is loaded
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found in .env file")
        return
    
    print(f"Using API key: {api_key[:8]}...")
    test_deepseek_api()

if __name__ == "__main__":
    main() 