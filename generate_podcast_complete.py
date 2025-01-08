#!/root/news_test/jupyter_env/bin/python

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from services.podcast_generator import PodcastGenerator
from services.tts.google_tts import GoogleTTS

async def generate_complete_podcast(
    topic: str,
    language_code: str = "en-GB",
    voice_name: str = None,
    output_dir: str = "output"
):
    """
    Generate a complete podcast from topic to audio
    
    Steps:
    1. Search for news articles about the topic
    2. Generate podcast script in target language using LLM
    3. Convert script to audio using TTS
    """
    try:
        print(f"\n=== Starting podcast generation for topic: {topic} ===\n")
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1 & 2: Generate podcast script in target language
        print(f"Generating podcast script in {language_code}...")
        podcast_gen = PodcastGenerator()
        script = await podcast_gen.generate_podcast_script(topic, language_code)
        
        # Save the script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_file = f"{output_dir}/podcast_{topic.replace(' ', '_')}_{timestamp}.txt"
        with open(script_file, "w") as f:
            f.write(script)
        print(f"Script saved to: {script_file}")
        
        # Step 3: Convert to audio
        print("\nConverting script to audio...")
        tts = GoogleTTS()
        audio_file = await tts.synthesize_speech(
            text=script,
            language_code=language_code,
            voice_name=voice_name,
            output_dir=output_dir
        )
        print(f"Audio saved to: {audio_file}")
        
        print(f"\n=== Podcast generation complete! ===")
        print(f"Script: {script_file}")
        print(f"Audio: {audio_file}")
        
        return {
            "script_file": script_file,
            "audio_file": audio_file
        }
        
    except Exception as e:
        print(f"Error generating podcast: {str(e)}")
        raise

async def main():
    parser = argparse.ArgumentParser(description="Generate a complete podcast from topic to audio")
    parser.add_argument("topic", help="The topic to generate a podcast about")
    parser.add_argument("--language", default="en-GB", help="Language code (e.g., en-GB, fr-FR)")
    parser.add_argument("--voice", help="Specific voice name (optional)")
    parser.add_argument("--output-dir", default="output", help="Output directory for files")
    args = parser.parse_args()
    
    try:
        await generate_complete_podcast(
            topic=args.topic,
            language_code=args.language,
            voice_name=args.voice,
            output_dir=args.output_dir
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 