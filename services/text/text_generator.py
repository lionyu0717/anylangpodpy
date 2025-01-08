from openai import OpenAI
from typing import List, Dict, Optional
from config import get_config

class TextGenerationError(Exception):
    """Custom exception for text generation errors"""
    pass

def create_deepseek_client() -> OpenAI:
    """Create and return a configured Deepseek client"""
    config = get_config()
    if not config.DEEPSEEK_API_KEY:
        raise TextGenerationError("DEEPSEEK_API_KEY not found in config")
    return OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_API_BASE_URL
    )

class TextGenerator:
    """Class for generating text using the Deepseek API"""
    
    def __init__(self):
        self.config = get_config()
        
    async def generate(self, prompt: str) -> str:
        """Generate text using the Deepseek API"""
        return generate_text(
            prompt=prompt,
            system_message="You are an expert podcast host. Create engaging, informative content.",
            temperature=0.7,
            max_tokens=2000  # Adjust based on desired length
        )

def generate_text(
    prompt: str,
    system_message: str = "You are a helpful assistant",
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Generate text using the Deepseek API
    
    Args:
        prompt: The user prompt to generate text from
        system_message: The system message to set context
        model: The model to use for generation
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens to generate (optional)
    
    Returns:
        str: Generated text response
        
    Raises:
        TextGenerationError: If API call fails
    """
    try:
        client = create_deepseek_client()
        
        completion_args = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        if max_tokens:
            completion_args["max_tokens"] = max_tokens
            
        response = client.chat.completions.create(**completion_args)
        return response.choices[0].message.content
        
    except Exception as e:
        raise TextGenerationError(f"Failed to generate text: {str(e)}")

def test_deepseek_api():
    """Test the Deepseek API with a simple prompt"""
    try:
        response = generate_text(
            prompt="What is the capital of France?",
            system_message="You are a knowledgeable assistant. Keep answers brief.",
            temperature=0.7
        )
        print("Test successful! Response:")
        print(response)
        return True
    except TextGenerationError as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()