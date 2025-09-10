#!/usr/bin/env python3
"""
Generate a complete D&D campaign with text content and images
"""
import sys
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def generate_full_campaign(mode: str = "production"):
    """Generate a complete campaign with all components

    Args:
        mode: "test" or "production" - determines content volume and quality
    """
    try:
        print("🎲 GENERATING COMPLETE D&D CAMPAIGN WITH IMAGES")
        print("=" * 60)

        # Import services
        from services.ai_service import ClaudeAIService
        from services.image_service import ImageGenerationService

        # Get API keys
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not claude_key:
            print("❌ ANTHROPIC_API_KEY not found")
            return
        if not openai_key:
            print("❌ OPENAI_API_KEY not found")
            return

        # Initialize services
        print("🤖 Initializing AI services...")
        claude_service = ClaudeAIService(claude_key)
        image_service = ImageGenerationService(openai_key)

        # Create campaign-specific output directory
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent  # Go up to panverse root
        base_output_dir = project_root / "campaign_output"
        base_output_dir.mkdir(exist_ok=True)

        # Campaign directory will be created after concept generation with proper name

        # Campaign concept
        print(f"\n📝 Generating campaign concept (Mode: {mode})...")

        # Adjust concept generation based on mode
        if mode == "test":
            concept_length = "(150-250 words for quick validation)"
        else:
            concept_length = "(300-500 words for full campaign)"

        concept_prompt = f"""
        Create a compelling D&D 5e campaign concept with:
        - An evocative title and subtitle
        - A detailed description {concept_length}
        - Recommended level range
        - Key themes and plot hooks
        - Setting and atmosphere details
        """
        concept_response = await claude_service._call_claude_api(concept_prompt)
        concept_content = claude_service._parse_section_content_response(concept_response)

        # Extract campaign name from the first line
        first_line = concept_content.strip().split('\n')[0]
        if 'Title:' in first_line:
            campaign_name = first_line.replace('Title:', '').replace('Subtitle:', '').strip()
        else:
            campaign_name = first_line.strip()

        # Clean up the campaign name for folder use
        import re
        campaign_name = re.sub(r'[^\w\s-]', '', campaign_name)  # Remove special chars
        campaign_name = re.sub(r'\s+', '_', campaign_name)  # Replace spaces with underscores

        # Recalculate paths with actual campaign name
        campaign_base_dir = base_output_dir / campaign_name
        campaign_base_dir.mkdir(exist_ok=True)

        # Find the next version number
        existing_versions = []
        for item in campaign_base_dir.iterdir():
            if item.is_dir() and item.name.startswith('v'):
                try:
                    version_num = int(item.name[1:])  # Remove 'v' prefix
                    existing_versions.append(version_num)
                except ValueError:
                    pass

        next_version = max(existing_versions) + 1 if existing_versions else 1
        version_dir_name = f"v{next_version}"

        campaign_dir = campaign_base_dir / version_dir_name
        campaign_dir.mkdir(exist_ok=True)
        images_dir = campaign_dir  # Images go directly in version folder

        print(f"📁 Campaign: {campaign_name} (Version {next_version})")
        print(f"📁 Directory: {campaign_dir.absolute()}")

        # Save concept
        concept_file = campaign_dir / "campaign_concept.txt"
        with open(concept_file, 'w') as f:
            f.write(concept_content)
        print(f"✅ Campaign concept saved: {concept_file}")

        # Generate cover image (always generated)
        print("\n🎨 Generating campaign cover image...")
        cover_prompt = f"Create a dramatic D&D campaign cover art for: {concept_content[:200]}"
        cover_image = await image_service.generate_image(cover_prompt, size="1792x1024")
        if cover_image:
            print(f"✅ Cover image generated: {cover_image}")
        else:
            print("⚠️ Cover image generation failed")

        # Generate world description
        print("\n🌍 Generating world description...")
        world_prompt = f"""
        Based on this campaign concept: {concept_content[:300]}

        Create a detailed world description including:
        - Geography and key locations
        - Major cultures and societies
        - Magic system and supernatural elements
        - Political landscape and conflicts
        - Atmosphere and visual details
        """
        world_response = await claude_service._call_claude_api(world_prompt)
        world_content = claude_service._parse_section_content_response(world_response)

        world_file = campaign_dir / "world_description.txt"
        with open(world_file, 'w') as f:
            f.write(world_content)
        print(f"✅ World description saved: {world_file}")

        # Generate world map image (only in production mode)
        if mode == "production":
            world_map_prompt = f"Create a fantasy world map for this setting: {world_content[:200]}"
            world_map = await image_service.generate_image(world_map_prompt, size="1024x1024")
            if world_map:
                print(f"✅ World map generated: {world_map}")
            else:
                print("⚠️ World map generation failed")
        else:
            world_map = None
            print("⏭️ Skipping world map generation in test mode")

        # Generate plot summary
        print("\n📖 Generating plot summary...")
        plot_prompt = f"""
        Based on this campaign: {concept_content[:200]}

        Create a detailed plot summary including:
        - Main story arc and key events
        - Major plot twists and revelations
        - Character development opportunities
        - Multiple endings and player choice impact
        - Adventure hooks and side quests
        """
        plot_response = await claude_service._call_claude_api(plot_prompt)
        plot_content = claude_service._parse_section_content_response(plot_response)

        plot_file = campaign_dir / "plot_summary.txt"
        with open(plot_file, 'w') as f:
            f.write(plot_content)
        print(f"✅ Plot summary saved: {plot_file}")

        # Generate key NPCs
        print("\n👥 Generating key NPCs...")
        npc_prompt = f"""
        For this campaign: {concept_content[:200]}

        Create 3-4 memorable NPCs with:
        - Detailed physical descriptions
        - Personality traits and motivations
        - Background stories and secrets
        - Role in the main plot
        - Combat statistics (if applicable)
        - Relationship to player characters
        """
        npc_response = await claude_service._call_claude_api(npc_prompt)
        npc_content = claude_service._parse_section_content_response(npc_response)

        npc_file = campaign_dir / "key_npcs.txt"
        with open(npc_file, 'w') as f:
            f.write(npc_content)
        print(f"✅ NPCs saved: {npc_file}")

        # Generate NPC portraits (limit in test mode)
        num_npcs_to_generate = 2 if mode == "test" else 3
        for i in range(num_npcs_to_generate):
            npc_portrait_prompt = f"Create a detailed fantasy character portrait for NPC {i+1} from: {npc_content.split('.')[i] if i < len(npc_content.split('.')) else 'A fantasy NPC'}"
            # Generate at 1024x1024 (supported by DALL-E) then resize to 512x512
            npc_image = await image_service.generate_image(npc_portrait_prompt, size="1024x1024", resize_to=(512, 512))
            if npc_image:
                print(f"✅ NPC {i+1} portrait generated and resized: {npc_image}")
            else:
                print(f"⚠️ NPC {i+1} portrait generation failed")

        # Generate key locations
        print("\n🏰 Generating key locations...")
        location_prompt = f"""
        For this campaign world: {world_content[:300]}

        Create 3-4 important locations with:
        - Detailed descriptions and atmosphere
        - Strategic significance to the plot
        - Notable features and landmarks
        - Adventure opportunities and encounters
        - Maps and navigation details
        """
        location_response = await claude_service._call_claude_api(location_prompt)
        location_content = claude_service._parse_section_content_response(location_response)

        location_file = campaign_dir / "key_locations.txt"
        with open(location_file, 'w') as f:
            f.write(location_content)
        print(f"✅ Locations saved: {location_file}")

        # Generate location images (limit in test mode)
        num_locations_to_generate = 1 if mode == "test" else 2
        for i in range(num_locations_to_generate):
            location_image_prompt = f"Create a fantasy illustration of location {i+1}: {location_content.split('.')[i] if i < len(location_content.split('.')) else 'A fantasy location'}"
            location_image = await image_service.generate_image(location_image_prompt, size="1024x1024")
            if location_image:
                print(f"✅ Location {i+1} image generated: {location_image}")
            else:
                print(f"⚠️ Location {i+1} image generation failed")

        # Generate encounters
        print("\n⚔️ Generating encounters and combat...")
        encounter_prompt = f"""
        For this D&D 5e campaign: {concept_content[:200]}

        Create balanced encounters including:
        - Major combat encounters with monster stats
        - Social encounters and roleplaying opportunities
        - Traps, puzzles, and environmental challenges
        - Treasure and reward systems
        - Scaling guidelines for different party sizes
        """
        encounter_response = await claude_service._call_claude_api(encounter_prompt)
        encounter_content = claude_service._parse_section_content_response(encounter_response)

        encounter_file = campaign_dir / "encounters.txt"
        with open(encounter_file, 'w') as f:
            f.write(encounter_content)
        print(f"✅ Encounters saved: {encounter_file}")

        # Generate appendices
        print("\n📚 Generating appendices...")
        appendix_prompt = f"""
        Create comprehensive appendices for this campaign including:
        - Character creation guidelines
        - Important rules clarifications
        - Random encounter tables
        - Treasure and magic item lists
        - Player handouts and maps descriptions
        - Campaign tracking sheets
        """
        appendix_response = await claude_service._call_claude_api(appendix_prompt)
        appendix_content = claude_service._parse_section_content_response(appendix_response)

        appendix_file = campaign_dir / "appendices.txt"
        with open(appendix_file, 'w') as f:
            f.write(appendix_content)
        print(f"✅ Appendices saved: {appendix_file}")

        # Create campaign summary
        print("\n📋 Creating campaign summary...")
        summary = {
            "title": "Generated D&D 5e Campaign",
            "generated_at": datetime.now().isoformat(),
            "sections": [
                {"name": "Campaign Concept", "file": "campaign_concept.txt", "size": len(concept_content)},
                {"name": "World Description", "file": "world_description.txt", "size": len(world_content)},
                {"name": "Plot Summary", "file": "plot_summary.txt", "size": len(plot_content)},
                {"name": "Key NPCs", "file": "key_npcs.txt", "size": len(npc_content)},
                {"name": "Key Locations", "file": "key_locations.txt", "size": len(location_content)},
                {"name": "Encounters", "file": "encounters.txt", "size": len(encounter_content)},
                {"name": "Appendices", "file": "appendices.txt", "size": len(appendix_content)}
            ],
            "images_generated": len(list(images_dir.glob("*.png"))),
            "total_content_length": sum([
                len(concept_content), len(world_content), len(plot_content),
                len(npc_content), len(location_content), len(encounter_content), len(appendix_content)
            ])
        }

        summary_file = campaign_dir / "campaign_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Campaign summary saved: {summary_file}")

        # Final report
        print("\n" + "=" * 60)
        print("🎉 CAMPAIGN GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Campaign Location: {campaign_dir.absolute()}")
        print(f"📄 Text Files: {len(list(campaign_dir.glob('*.txt')))}")
        print(f"🖼️ Images: {len(list(images_dir.glob('*.png')))}")
        print(f"📊 Total Content: {summary['total_content_length']} characters")
        print("\n📋 Generated Files:")
        for section in summary['sections']:
            print(f"   • {section['name']} ({section['size']} chars)")

        print("\n🚀 Your complete D&D campaign is ready!")
        print("💡 You can now:")
        print("   - Read all text files for complete adventure details")
        print("   - Use the generated images for handouts and inspiration")
        print("   - Modify and customize the content as needed")
        print("   - Share with your players!")
        print(f"\n📂 All files are located in: {campaign_dir.absolute()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "production"
    if mode not in ["test", "production"]:
        print("❌ Invalid mode. Use 'test' or 'production'")
        sys.exit(1)
    asyncio.run(generate_full_campaign(mode))
