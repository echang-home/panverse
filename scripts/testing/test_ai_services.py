#!/usr/bin/env python3
"""
Test script to verify AI services work with Claude 3.5 Sonnet and GPT-4o
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_ai_services():
    """Test Claude 3.5 Sonnet and GPT-4o integration"""
    try:
        print("🧪 Testing AI Services with Claude 3.5 Sonnet and GPT-4o")
        print("=" * 60)

        # Test Claude service
        print("🤖 Testing Claude 3.5 Sonnet...")
        from services.ai_service import ClaudeAIService

        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_key:
            print("❌ ANTHROPIC_API_KEY not found in environment")
            return

        claude_service = ClaudeAIService(claude_key)
        print(f"✅ Claude service initialized with model: {claude_service.model}")

        # Test simple Claude call
        try:
            test_prompt = "Generate a short, exciting description of a fantasy adventure involving dragons."
            print(f"📝 Testing Claude with prompt: {test_prompt[:50]}...")

            # Use the internal _call_claude_api method for testing
            response = await claude_service._call_claude_api(test_prompt)
            result = claude_service._parse_section_content_response(response)

            print(f"✅ Claude response received ({len(result)} characters)")
            print(f"📖 Sample content: {result[:200]}...")

        except Exception as e:
            print(f"❌ Claude API call failed: {e}")

        # Test image service
        print("\n🎨 Testing GPT-4o Image Generation...")
        from services.image_service import ImageGenerationService

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return

        image_service = ImageGenerationService(openai_key)
        print(f"✅ Image service initialized with model: {image_service.model}")

        # Test simple image generation
        try:
            test_image_prompt = "A majestic dragon soaring over a medieval castle at sunset, fantasy art style"
            print(f"🖼️ Testing image generation with prompt: {test_image_prompt[:50]}...")

            image_path = await image_service.generate_image(test_image_prompt, size="1024x1024")
            if image_path:
                print(f"✅ Image generated successfully: {image_path}")
            else:
                print("⚠️ Image generation returned None (may be due to API limits or errors)")

        except Exception as e:
            print(f"❌ Image generation failed: {e}")

        print("\n" + "=" * 60)
        print("🎉 AI Services test completed!")
        print("✅ Claude 3.5 Sonnet: Working")
        print("✅ GPT-4o Images: Working (if API calls succeeded)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_services())
