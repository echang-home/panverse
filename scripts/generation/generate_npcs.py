#!/usr/bin/env python3
"""
Generate NPC portraits with correct image size
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def generate_npcs():
    """Generate NPC portraits"""
    from services.image_service import ImageGenerationService

    service = ImageGenerationService(os.getenv('OPENAI_API_KEY'))

    for i in range(3):
        result = await service.generate_image(
            f'Create a detailed fantasy character portrait for NPC {i+1}, professional fantasy art style',
            size='1024x1024'
        )
        if result:
            print(f'✅ NPC {i+1} portrait: {result}')
        else:
            print(f'❌ NPC {i+1} failed')

if __name__ == "__main__":
    asyncio.run(generate_npcs())
