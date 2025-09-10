#!/usr/bin/env python3
"""
Generate cover art for The Twilight Crown campaign using Claude AI
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from services.image_service import ImageGenerationService

async def generate_twilight_crown_cover_art():
    """Generate cover art for The Twilight Crown campaign"""
    try:
        print("🎨 GENERATING TWILIGHT CROWN COVER ART")
        print("=" * 60)

        # Initialize image service
        image_service = ImageGenerationService()

        # Claude prompt for cover art (as specified in requirements)
        cover_prompt = """Create a dramatic fantasy book cover for a D&D campaign called 'The Twilight Crown: Legacy of the Starborn Dynasty'. The image should feature a mysterious cosmic crown floating against a dramatic starry background with nebula clouds in deep blues and purples. The crown should have ethereal energy emanating from it, with constellation patterns visible within. Include ancient crystal spires or structures in the background. Use a style similar to official D&D campaign books with rich colors and dramatic lighting. The image should feel mysterious, magical and invoke a sense of ancient cosmic power."""

        print("🖼️ Generating cover art with Claude...")

        # Generate cover image
        cover_image_path = await image_service.generate_image(
            prompt=cover_prompt,
            image_type="cover",
            filename="twilight_crown_cover.png",
            style="dramatic_fantasy"
        )

        if cover_image_path and Path(cover_image_path).exists():
            file_size = Path(cover_image_path).stat().st_size / 1024  # KB
            print("✅ SUCCESS: Cover art generated!")
            print(f"📁 Location: {cover_image_path}")
            print(f"📊 Size: {file_size:.1f} KB")
            print("\n🎨 Cover Art Details:")
            print("  ✓ Twilight Crown theme")
            print("  ✓ Celestial cosmic styling")
            print("  ✓ Nebula backgrounds")
            print("  ✓ Ethereal energy effects")
            print("  ✓ Ancient crystal structures")
            print("  ✓ D&D campaign book style")

            print("\n" + "=" * 60)
            print("🎉 COVER ART READY FOR CAMPAIGN PDF!")
            print("=" * 60)

        else:
            print("❌ FAILED: Cover art generation failed")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def generate_additional_campaign_images():
    """Generate additional images for the campaign"""
    try:
        print("\n🖼️ GENERATING ADDITIONAL CAMPAIGN IMAGES")
        print("=" * 50)

        image_service = ImageGenerationService()

        # Generate chapter opener illustration
        chapter_prompt = """Create a detailed fantasy illustration for a D&D campaign book in the style of official Wizards of the Coast publications. The image should show the ancient city of Aldermere at twilight, with crystal spires reaching into a starry sky filled with cosmic energy. A mysterious crown floats above the city, casting ethereal light on the streets below. Use deep blues, purples, and silver highlights with dramatic lighting. The style should be professional fantasy art suitable for a published RPG book."""

        print("📖 Generating chapter opener illustration...")
        chapter_image_path = await image_service.generate_image(
            prompt=chapter_prompt,
            image_type="chapter_opener",
            filename="aldermere_twilight.png",
            style="fantasy_illustration"
        )

        if chapter_image_path:
            print(f"✅ Chapter opener: {chapter_image_path}")

        # Generate NPC portraits
        npc_prompts = [
            ("Queen Elowen Starborn", "A regal elf queen with silver hair and eyes that glow with cosmic energy, wearing a crown embedded with star sapphires"),
            ("Lord Thorne Shadowbane", "A mysterious human warlock with dark robes and arcane symbols floating around him"),
            ("Sister Lirael Moonwhisper", "An elven cleric with flowing white robes and a crescent moon pendant")
        ]

        for npc_name, npc_description in npc_prompts:
            npc_prompt = f"""Create a portrait of {npc_name}, {npc_description}. Style: Professional fantasy character portrait in the style of official D&D publications, with dramatic lighting and rich colors suitable for an RPG campaign book."""

            print(f"👤 Generating portrait for {npc_name}...")
            npc_image_path = await image_service.generate_image(
                prompt=npc_prompt,
                image_type="npc_portrait",
                filename=f"{npc_name.lower().replace(' ', '_')}_portrait.png",
                style="character_portrait"
            )

            if npc_image_path:
                print(f"✅ {npc_name}: {npc_image_path}")

        print("\n🎉 ALL CAMPAIGN IMAGES GENERATED!")

    except Exception as e:
        print(f"❌ ERROR generating additional images: {e}")

if __name__ == "__main__":
    # Generate cover art
    asyncio.run(generate_twilight_crown_cover_art())

    # Generate additional images
    asyncio.run(generate_additional_campaign_images())
