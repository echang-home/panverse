#!/usr/bin/env python3
"""
Simple script to generate a sample campaign
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def generate_sample_campaign():
    """Generate a sample campaign"""
    try:
        from infrastructure.container import get_container
        from domain.value_objects import PlayerPreferences, CampaignTheme, DifficultyLevel, PartySize, Duration

        print("🚀 Initializing campaign generator...")

        # Get container
        container = await get_container()
        print("✅ Services initialized")

        # Create sample preferences
        preferences = PlayerPreferences(
            theme=CampaignTheme.FANTASY,
            difficulty=DifficultyLevel.MEDIUM,
            story_length=Duration.MEDIUM,
            freeform_input="Create an exciting fantasy adventure with dragons, magic, and heroic quests"
        )

        print("🎲 Generating sample campaign...")
        print(f"Theme: {preferences.theme.value}")
        print(f"Difficulty: {preferences.difficulty.value}")
        print(f"Duration: {preferences.story_length.value}")

        # Get campaign generation service
        generation_service = container.campaign_generation_service

        # Generate campaign with sample mode by default
        campaign_id = await generation_service.generate_campaign(
            theme=preferences.theme,
            difficulty=preferences.difficulty,
            party_size=PartySize.SMALL,
            starting_level=3,
            duration=preferences.story_length.value,
            user_id="sample-user-123",
            custom_instructions=preferences.freeform_input,
            mode="sample"  # Use sample mode for the sample generation script
        )

        print(f"✅ Campaign generated with ID: {campaign_id}")

        # Try to get campaign details
        retrieval_service = container.campaign_retrieval_service
        campaign = await retrieval_service.get_campaign(campaign_id, "sample-user-123")

        if campaign:
            print("📖 Campaign Details:")
            print(f"   Name: {campaign.name}")
            print(f"   Description: {campaign.description[:200]}...")
            print(f"   Sections: {len(campaign.sections)}")
            print(f"   Images: {len(campaign.images) if campaign.images else 0}")
            print(f"   Quality Score: {campaign.quality_score.value}/5.0")

            # List sections
            if campaign.sections:
                print("📑 Sections generated:")
                for i, section in enumerate(campaign.sections[:5], 1):  # Show first 5
                    print(f"   {i}. {section.title} ({len(section.content)} chars)")
                if len(campaign.sections) > 5:
                    print(f"   ... and {len(campaign.sections) - 5} more sections")

        print("🎉 Sample campaign generation completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_sample_campaign())
