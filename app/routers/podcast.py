from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import os
import re

from app.services.gdelt import GDELTService
from app.services.scraper import Scraper
from app.services.text.text_generator import TextGenerator
from app.services.tts.google_tts import GoogleTTS
from app.services.podcast_generator import PodcastGenerator
from config import get_config

# Models
class KeywordRequest(BaseModel):
    keyword: str = Field(..., description="The main keyword to generate podcast content about")
    max_length: Optional[int] = Field(default=500, description="Maximum length of the generated content")
    language_code: Optional[str] = Field(default="en-GB", description="Language code for the podcast")
    use_llm_fallback: Optional[bool] = Field(default=True, description="Whether to use LLM for suggestions if news not found")

class PodcastResponse(BaseModel):
    keyword: str
    content: Optional[str]
    audio_url: Optional[str]
    duration: Optional[float] = None
    status: str = Field(..., description="Status of the podcast generation: success, processing, or error")
    request_id: Optional[str]
    error: Optional[str] = None

router = APIRouter(prefix="/api/podcast", tags=["podcast"])

# Initialize services
config = get_config()
podcast_generator = PodcastGenerator()

# Store podcast generation state
podcast_status: Dict[str, str] = {}  # request_id -> status
podcast_content: Dict[str, str] = {}  # request_id -> content
podcast_audio: Dict[str, Dict] = {}  # request_id -> audio info
podcast_errors: Dict[str, Optional[str]] = {}  # request_id -> error message

@router.post("/generate", response_model=PodcastResponse)
async def generate_podcast(request: KeywordRequest, background_tasks: BackgroundTasks):
    try:
        # Generate request ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = re.sub(r'[^a-zA-Z0-9]', '_', request.keyword.lower())
        request_id = f"{safe_keyword}_{timestamp}"
        
        # Initialize status
        podcast_status[request_id] = "processing"
        podcast_content[request_id] = ""
        podcast_audio[request_id] = None
        podcast_errors[request_id] = None
        
        # Start background task
        background_tasks.add_task(generate_podcast_background, request, request_id)
        
        return PodcastResponse(
            keyword=request.keyword,
            content="",  # Will be updated in background
            audio_url=None,  # Will be updated in background
            status="processing",
            request_id=request_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{request_id}", response_model=PodcastResponse)
async def get_podcast_status(request_id: str):
    if request_id not in podcast_status:
        raise HTTPException(status_code=404, detail="Podcast request not found")
    
    audio_info = podcast_audio.get(request_id)
    audio_url = audio_info.get("url") if audio_info else None
    duration = audio_info.get("duration") if audio_info else None
    
    return PodcastResponse(
        keyword=request_id.split("_")[0],  # Extract keyword from request_id
        content=podcast_content.get(request_id),
        audio_url=audio_url,
        duration=duration,
        status=podcast_status.get(request_id),
        request_id=request_id,
        error=podcast_errors.get(request_id)
    )

async def generate_podcast_background(request: KeywordRequest, request_id: str):
    try:
        # Generate the script using PodcastGenerator
        script = await podcast_generator.generate_podcast_script(
            topic=request.keyword,
            language_code=request.language_code
        )
        
        # Store the script even if empty
        podcast_content[request_id] = script if script else ""
        
        if not script:
            podcast_status[request_id] = "error"
            podcast_errors[request_id] = f"No content generated for topic: {request.keyword}"
            return
            
        # Clean up any remaining formatting
        script = script.replace("**", "").replace("*", "").replace("[", "").replace("]", "")
        script = script.replace("Host:", "").replace("---", "").replace("Music", "")
        script = script.replace("Intro:", "").replace("Outro:", "")
        script = "\n".join(line for line in script.split("\n") if not line.strip().startswith("(") and not line.strip().endswith(")"))
        script = script.strip()
        
        # Update content with cleaned script
        podcast_content[request_id] = script
        podcast_status[request_id] = "success"
        
        try:
            # Generate audio using TTS
            safe_keyword = re.sub(r'[^a-zA-Z0-9]', '_', request.keyword.lower())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"{safe_keyword}_{timestamp}.mp3"
            output_path = os.path.join("output", audio_filename)
            
            # Ensure output directory exists
            os.makedirs("output", exist_ok=True)
            
            # Convert text to speech
            tts_service = GoogleTTS()
            duration = await tts_service.text_to_speech(
                text=script,
                output_path=output_path,
                language_code=request.language_code
            )
            
            # Store the audio information
            podcast_audio[request_id] = {
                "filename": audio_filename,
                "url": f"/output/{audio_filename}",
                "content_type": "audio/mpeg",
                "duration": duration
            }
            
        except Exception as e:
            # If TTS fails, still keep the script
            podcast_errors[request_id] = f"TTS failed: {str(e)}"
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating podcast: {error_msg}")
        podcast_status[request_id] = "error"
        podcast_errors[request_id] = error_msg 