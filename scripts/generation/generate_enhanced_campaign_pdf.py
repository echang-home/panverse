#!/usr/bin/env python3
"""
Generate enhanced PDF for the newly created campaign using our professional styling
"""
import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Mock campaign data structure
class MockCampaign:
    def __init__(self, concept_data, world_data, plot_data, npc_data, location_data, encounter_data, appendices_data, images):
        self.id = "echoes-shattered-crown-001"
        self.name = "Echoes of the Shattered Crown"
        self.description = concept_data.get('description', '')
        self.theme = type('obj', (object,), {'value': 'political_fantasy'})()
        self.difficulty = type('obj', (object,), {'value': 'challenging'})()
        self.starting_level = 3
        self.party_size = type('obj', (object,), {'value': 'small'})()
        self.expected_duration = type('obj', (object,), {'value': 'medium'})()
        self.quality_score = type('obj', (object,), {'value': 4.8})()
        self.generated_at = datetime.now()
        self.world = MockWorld(world_data)
        self.story_hook = MockStoryHook(concept_data)
        self.story_arcs = [MockStoryArc(plot_data)]
        self.key_npcs = [MockNPC(npc) for npc in npc_data.get('npcs', [])]
        self.key_locations = [MockLocation(loc) for loc in location_data.get('locations', [])]
        self.sections = None
        self.player_preferences = None

        # Add missing methods
        self.get_total_content_length = lambda: len(json.dumps({
            'concept': concept_data, 'world': world_data, 'plot': plot_data,
            'npcs': npc_data, 'locations': location_data, 'encounters': encounter_data
        }))
        self.get_total_image_count = lambda: len(images)

class MockWorld:
    def __init__(self, world_data):
        self.name = world_data.get('name', 'Aldermere')
        self.description = world_data.get('description', '')

class MockStoryHook:
    def __init__(self, concept_data):
        self.title = "The Shattered Crown Prophecy"
        self.description = concept_data.get('description', '')
        self.stakes = "The realm faces either reunification under a new dynasty or total destruction at the hands of ancient evil."

class MockStoryArc:
    def __init__(self, plot_data):
        self.title = plot_data.get('title', 'The Crown\'s Reunion')
        self.description = plot_data.get('description', '')
        self.climax = "Confrontation with the ancient evil at the crown's resting place"
        self.resolution = "The players must choose between unity with risk or permanent division with safety"

class MockNPC:
    def __init__(self, npc_data):
        self.name = npc_data.get('name', 'Unknown NPC')
        self.race = type('obj', (object,), {'title': lambda: npc_data.get('race', 'Human')})()
        self.character_class = type('obj', (object,), {'title': lambda: npc_data.get('class', 'Adventurer')})()
        self.background = npc_data.get('background', 'Mysterious origins')
        self.motivation = npc_data.get('motivation', 'Personal gain')
        self.role_in_story = npc_data.get('role', 'Supporting character')
        self.personality = {
            'traits': npc_data.get('personality', ['Enigmatic', 'Ambitious']),
            'alignment': npc_data.get('alignment', 'Neutral')
        }

class MockLocation:
    def __init__(self, location_data):
        self.name = location_data.get('name', 'Unknown Location')
        self.type = type('obj', (object,), {'title': lambda: location_data.get('type', 'Place')})()
        self.description = location_data.get('description', '')
        self.significance = location_data.get('significance', 'Important to the plot')
        self.encounters = location_data.get('encounters', [])

async def generate_enhanced_campaign_pdf():
    """Generate enhanced PDF for the new campaign"""
    try:
        print("🎨 GENERATING ENHANCED PDF FOR 'ECHOES OF THE SHATTERED CROWN'")
        print("=" * 70)

        # Read campaign data from the most recent campaign
        script_dir = Path(__file__).parent
        # Navigate up to find the campaign_output directory
        current = script_dir
        campaign_output_dir = None

        # Look for campaign_output in parent directories
        for _ in range(5):  # Check up to 5 levels up
            if (current / "campaign_output").exists():
                campaign_output_dir = current / "campaign_output"
                break
            current = current.parent

        if campaign_output_dir is None:
            print("❌ Could not find campaign_output directory")
            return
        if not campaign_output_dir.exists():
            print("❌ No campaign_output directory found")
            return

        # Find the most recent campaign directory
        campaign_dirs = [d for d in campaign_output_dir.iterdir() if d.is_dir()]
        if not campaign_dirs:
            print("❌ No campaign directories found")
            return

        # Get the most recent campaign
        most_recent_campaign = max(campaign_dirs, key=lambda x: x.stat().st_mtime)

        # Find the most recent version within that campaign
        version_dirs = [d for d in most_recent_campaign.iterdir() if d.is_dir() and d.name.startswith('v')]
        if not version_dirs:
            print("❌ No version directories found")
            return

        campaign_dir = max(version_dirs, key=lambda x: x.stat().st_mtime)
        print(f"📖 Reading campaign data from: {most_recent_campaign.name} (Version {campaign_dir.name})")

        # Read all the generated files
        files_to_read = [
            'campaign_concept.txt',
            'world_description.txt',
            'plot_summary.txt',
            'key_npcs.txt',
            'key_locations.txt',
            'encounters.txt',
            'appendices.txt'
        ]

        campaign_data = {}
        for filename in files_to_read:
            filepath = campaign_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    campaign_data[filename] = f.read()
                print(f"✅ Read {filename}")

        # Get list of generated images
        images_dir = campaign_dir / "images"
        images = []
        if images_dir.exists():
            images = list(images_dir.glob("*.png"))
            print(f"🖼️ Found {len(images)} images")

        # Parse some key data for the mock campaign
        concept_text = campaign_data.get('campaign_concept.txt', '')
        world_text = campaign_data.get('world_description.txt', '')
        plot_text = campaign_data.get('plot_summary.txt', '')
        npc_text = campaign_data.get('key_npcs.txt', '')
        location_text = campaign_data.get('key_locations.txt', '')

        # Create mock campaign object
        print("🎭 Creating campaign structure...")
        campaign = MockCampaign(
            concept_data={'description': concept_text[:500]},
            world_data={'name': 'Aldermere', 'description': world_text[:300]},
            plot_data={'title': 'The Crown\'s Reunion', 'description': plot_text[:400]},
            npc_data={'npcs': []},  # Would need proper parsing
            location_data={'locations': []},  # Would need proper parsing
            encounter_data={'content': campaign_data.get('encounters.txt', '')},
            appendices_data={'content': campaign_data.get('appendices.txt', '')},
            images=images
        )

        # Import and initialize enhanced PDF service
        print("📄 Initializing Enhanced PDF Service...")
        from services.pdf_service import EnhancedPDFGenerationService
        pdf_service = EnhancedPDFGenerationService()

        # Generate enhanced PDF in the campaign directory
        print("🎨 Generating professional campaign book...")
        campaign_name = most_recent_campaign.name
        version_num = campaign_dir.name
        pdf_filename = f"{campaign_name}_{version_num}_Enhanced.pdf"
        pdf_path = await pdf_service.generate_campaign_pdf(
            campaign,
            output_filename=str(campaign_dir / pdf_filename)
        )

        if pdf_path and Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size / 1024  # KB
            print("✅ SUCCESS: Enhanced PDF generated!")
            print(f"📁 Location: {pdf_path}")
            print(f"📊 Size: {file_size:.1f} KB")
            print(f"\n📖 Campaign: {campaign_name}")
            print(f"🎭 Version: {version_num}")
            print("🎨 Theme: Enhanced with Celestial Styling")
            print(f"🖼️ Images Processed: {len(images)}")
            print("\n🌟 Features:")
            print("  ✓ Celestial theme with cosmic styling")
            print("  ✓ Two-column professional layout")
            print("  ✓ Enhanced typography and spacing")
            print("  ✓ Custom borders and decorative elements")
            print("  ✓ Integrated image gallery")
            print("  ✓ Print-ready formatting")

            print("\n" + "=" * 70)
            print("🎉 YOUR PROFESSIONAL CAMPAIGN BOOK IS READY!")
            print("=" * 70)

        else:
            print("❌ FAILED: PDF generation failed")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_enhanced_campaign_pdf())
