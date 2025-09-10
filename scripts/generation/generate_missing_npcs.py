#!/usr/bin/env python3
"""
Generate missing NPC portraits for the current campaign
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def generate_missing_npcs():
    """Generate NPC portraits with correct image size"""

    # Import services
    from services.image_service import ImageGenerationService

    # Get API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        return

    # Initialize service
    image_service = ImageGenerationService(openai_key)

    # Campaign folder
    campaign_dir = Path("campaign_output/The_Twilight_Crown_V1")
    images_dir = campaign_dir / "images"

    # Read NPC descriptions
    npc_file = campaign_dir / "key_npcs.txt"
    if not npc_file.exists():
        print("❌ NPC file not found")
        return

    with open(npc_file, 'r') as f:
        npc_content = f.read()

    # Generate NPC portraits
    print("🎨 Generating NPC portraits...")
    for i in range(3):
        npc_portrait_prompt = f"Create a detailed fantasy character portrait for NPC {i+1} from this description: {npc_content.split('2.')[0] if i == 0 else npc_content.split(str(i+1)+'.')[1].split(str(i+2)+'.')[0] if i < 2 else npc_content.split(str(i+1)+'.')[1]}"

        print(f"Generating portrait for NPC {i+1}...")
        npc_image = await image_service.generate_image(npc_portrait_prompt, size="1024x1024")
        if npc_image:
            npc_dest = images_dir / f"npc_{i+1}.png"
            if os.path.exists(npc_image):
                import shutil
                shutil.move(npc_image, npc_dest)
                print(f"✅ NPC {i+1} portrait generated: {npc_dest}")
        else:
            print(f"⚠️ NPC {i+1} portrait generation failed")

if __name__ == "__main__":
    asyncio.run(generate_missing_npcs())
