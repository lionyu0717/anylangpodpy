#!/root/news_test/jupyter_env/bin/python

import asyncio
import argparse
from services.tts.google_tts import GoogleTTS

async def main():
    parser = argparse.ArgumentParser(description="Generate podcast audio from a script")
    parser.add_argument("script_file", help="Path to the podcast script file")
    parser.add_argument("--language", default="en-GB", help="Language code (e.g., en-GB, es-ES)")
    parser.add_argument("--voice", help="Specific voice name (optional)")
    parser.add_argument("--output-dir", default="output", help="Output directory for audio file")
    args = parser.parse_args()
    
    tts = GoogleTTS()
    
    try:
        print(f"Generating podcast audio from script: {args.script_file}")
        print(f"Language: {args.language}")
        if args.voice:
            print(f"Voice: {args.voice}")
        
        audio_file = await tts.synthesize_podcast(
            script_file=args.script_file,
            language_code=args.language,
            voice_name=args.voice,
            output_dir=args.output_dir
        )
        
        print(f"\nPodcast audio generated and saved to: {audio_file}")
        
    except Exception as e:
        print(f"Error generating podcast audio: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 