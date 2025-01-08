import asyncio
import argparse
from services.podcast_generator import PodcastGenerator

async def main():
    parser = argparse.ArgumentParser(description="Generate a podcast script about a topic")
    parser.add_argument("topic", help="The topic to generate a podcast about")
    args = parser.parse_args()
    
    generator = PodcastGenerator()
    
    try:
        print(f"Generating podcast script about: {args.topic}")
        script = await generator.generate_podcast_script(args.topic)
        
        # Save the script
        filename = await generator.save_podcast_script(args.topic, script)
        print(f"\nPodcast script generated and saved to: {filename}")
        
        # Print the script to console
        print("\nGenerated Script:")
        print("=" * 80)
        print(script)
        print("=" * 80)
        
    except Exception as e:
        print(f"Error generating podcast script: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 