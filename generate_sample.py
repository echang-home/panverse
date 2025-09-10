#!/usr/bin/env python3
"""
Simple script to generate a sample D&D campaign
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def generate_sample_campaign():
    """Generate a sample campaign using Claude AI"""

    # Import required modules
    from domain.value_objects import PlayerPreferences, CampaignTheme, DifficultyLevel
    from services.ai_service import ClaudeAIService
    from services.campaign_generation_service import CompleteCampaignGenerationService
    from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog

    print("🎲 Generating Sample D&D Campaign")
    print("=" * 50)

    # Check for API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    try:
        # Initialize services
        print("🔧 Initializing services...")

        # Content integrity watchdog
        watchdog = ContentIntegrityWatchdog(is_active=True)

        # Claude AI service
        claude_service = ClaudeAIService(
            api_key=anthropic_key,
            watchdog_service=None,  # Simplified for demo
            content_integrity_watchdog=watchdog
        )

        # Campaign generation service
        campaign_service = CompleteCampaignGenerationService(
            ai_service=claude_service,
            image_service=None,  # No images for sample
            watchdog_service=None,
            content_cache=None,
            image_cache=None,
            content_integrity_watchdog=watchdog
        )

        # Create sample preferences
        preferences = PlayerPreferences()
        preferences.theme = CampaignTheme.FANTASY
        preferences.difficulty = DifficultyLevel.MEDIUM
        preferences.story_length = Duration.MEDIUM
        preferences.specific_elements = ["dragons", "magic items", "mysterious ruins"]

        print("📋 Campaign Preferences:")
        print(f"  • Theme: {preferences.theme.value}")
        print(f"  • Difficulty: {preferences.difficulty.value}")
        print(f"  • Length: {preferences.story_length.value}")
        print(f"  • Elements: {', '.join(preferences.specific_elements)}")
        print()

        # Generate campaign
        print("🚀 Generating campaign...")
        request_id = await campaign_service.generate_campaign(
            theme=preferences.theme.value,
            difficulty=preferences.difficulty.value,
            party_size="small",
            starting_level=3,
            duration=preferences.story_length.value,
            user_id="sample-user",
            custom_instructions=f"Include elements: {', '.join(preferences.specific_elements)}",
            mode="sample"
        )

        print(f"✅ Campaign generation started with request ID: {request_id}")

        # Wait a moment for processing
        await asyncio.sleep(3)

        # Check status
        status = await campaign_service.get_generation_status(request_id)
        print(f"📊 Status: {status.get('status', 'unknown')}")

        if status.get('campaign_id'):
            print(f"🎉 Campaign generated successfully!")
            print(f"   Campaign ID: {status['campaign_id']}")

            # Create output directory
            output_dir = Path(__file__).parent / "campaign_output" / f"sample_campaign_{status['campaign_id']}"
            output_dir.mkdir(parents=True, exist_ok=True)

            print(f"💾 Campaign saved to: {output_dir}")

            # Try to get and display basic info
            if hasattr(campaign_service, 'get_campaign'):
                try:
                    campaign = await campaign_service.get_campaign(status['campaign_id'], "sample-user")
                    if campaign:
                        print("📖 Campaign Details:")
                        print(f"   • Name: {campaign.name}")
                        print(f"   • Description: {campaign.description[:100]}...")
                except Exception as e:
                    print(f"   (Could not retrieve full campaign details: {e})")

        else:
            print("⏳ Campaign generation is still in progress...")

    except Exception as e:
        print(f"❌ Error generating campaign: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Import Duration here to avoid circular imports
    from domain.value_objects import Duration

    asyncio.run(generate_sample_campaign())
