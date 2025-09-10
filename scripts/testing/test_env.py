#!/usr/bin/env python3
"""
Test script to verify .env loading and API keys
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("Testing environment variable loading...")
print(f"ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")

# Test container
try:
    from infrastructure.container import get_container
    print("Container import successful")

    async def test_container():
        container = await get_container()
        print("Container initialized successfully")
        print(f"Claude service: {'Available' if container.claude_service else 'Not available'}")
        print(f"Image service: {'Available' if container.image_service else 'Not available'}")

    import asyncio
    asyncio.run(test_container())

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
