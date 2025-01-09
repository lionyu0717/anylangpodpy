from typing import Optional, Dict
import base64
import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from config import get_config

class GoogleTTSError(Exception):
    """Custom exception for Google TTS errors"""
    pass

class GoogleTTS:
    """Google Cloud Text-to-Speech service"""
    
    # Default voices for different languages
    DEFAULT_VOICES = {
        "en": "en-GB-Journey-D",
        "es": "es-ES-Neural2-F",
        "fr": "fr-FR-Neural2-D",
        "de": "de-DE-Neural2-D",
        "it": "it-IT-Neural2-A",
        "ja": "ja-JP-Neural2-D",
        "ko": "ko-KR-Neural2-C",
        "zh": "cmn-CN-Neural2-C"
    }
    
    def __init__(self):
        self.config = get_config()
        self.session = None
        
        # Validate required config
        if not self.config.GOOGLE_CLOUD_API_KEY:
            raise GoogleTTSError("GOOGLE_CLOUD_API_KEY not found in config")
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-GB",
        voice_name: Optional[str] = None,
        output_dir: str = "output"
    ) -> str:
        """
        Synthesize speech from text using Google Cloud TTS
        
        Args:
            text: The text to synthesize
            language_code: The language code (e.g., "en-GB", "es-ES")
            voice_name: Optional specific voice name
            output_dir: Directory to save the audio file
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            await self._ensure_session()
            
            # Prepare request
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.config.GOOGLE_CLOUD_API_KEY}"
            headers = {
                "Content-Type": "application/json"
            }
            
            # Use provided voice name or get default for language
            if not voice_name:
                voice_name = self._get_voice_name(language_code)
            
            data = {
                "input": {"text": text},
                "voice": {
                    "languageCode": language_code,
                    "name": voice_name
                },
                "audioConfig": {
                    "audioEncoding": "MP3"
                }
            }
            
            # Make request
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise GoogleTTSError(f"TTS API error {response.status}: {error_text}")
                
                result = await response.json()
                
            # Decode audio content
            audio_content = base64.b64decode(result["audioContent"])
            
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{output_dir}/tts_{language_code}_{timestamp}.mp3"
            
            # Save audio file
            with open(output_file, "wb") as f:
                f.write(audio_content)
            
            return output_file
            
        except Exception as e:
            raise GoogleTTSError(f"Failed to synthesize speech: {str(e)}")
        finally:
            if self.session:
                await self.session.close()
                self.session = None
    
    def _get_voice_name(self, language_code: str) -> str:
        """Get the voice name for a language code"""
        lang_prefix = language_code.split('-')[0]
        return self.DEFAULT_VOICES.get(lang_prefix, self.DEFAULT_VOICES["en"])
    
    async def text_to_speech(
        self,
        text: str,
        output_path: str,
        language_code: str = "en-GB",
        voice_name: Optional[str] = None
    ) -> float:
        """
        Convert text to speech (alias for synthesize_speech)
        
        Args:
            text: The text to convert
            output_path: Full path to save the audio file
            language_code: The language code
            voice_name: Optional specific voice name
            
        Returns:
            float: Duration of the audio in seconds (estimated)
        """
        try:
            # Get output directory from output_path
            output_dir = str(Path(output_path).parent)
            
            # Generate audio file
            await self.synthesize_speech(
                text=text,
                language_code=language_code,
                voice_name=voice_name,
                output_dir=output_dir
            )
            
            # Estimate duration (rough estimate based on words and speaking rate)
            words = len(text.split())
            duration = (words * 0.4) * 0.25  # 0.4s per word * speaking rate
            
            return duration
            
        except Exception as e:
            raise GoogleTTSError(f"Failed to convert text to speech: {str(e)}")
    
    async def synthesize_podcast(
        self,
        script_file: str,
        language_code: str = "en-GB",
        voice_name: Optional[str] = None,
        output_dir: str = "output"
    ) -> str:
        """
        Synthesize a podcast script into speech
        
        Args:
            script_file: Path to the podcast script file
            language_code: The language code
            voice_name: Optional specific voice name
            output_dir: Directory to save the audio file
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Read the script
            with open(script_file, "r") as f:
                script = f.read()
            
            # Synthesize speech
            return await self.synthesize_speech(
                text=script,
                language_code=language_code,
                voice_name=voice_name,
                output_dir=output_dir
            )
            
        except Exception as e:
            raise GoogleTTSError(f"Failed to synthesize podcast: {str(e)}") 