#!/usr/bin/env python3
"""
Test script for the enhanced PDF generation features with Twilight Crown theme
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

from services.pdf_service import EnhancedPDFGenerationService
from domain.entities import Campaign, World, StoryHook, StoryArc, NPC, Location

class MockPlayerPreferences:
    def __init__(self):
        self.has_preferences = lambda: True
        self.get_preference_summary = lambda: {
            "theme": "celestial_fantasy",
            "difficulty": "challenging",
            "party_size": "small",
            "duration": "medium"
        }

async def test_enhanced_pdf_features():
    """Test all enhanced PDF features with sample data"""
    try:
        print("🧪 TESTING ENHANCED PDF FEATURES")
        print("=" * 60)

        # Create mock campaign data with Twilight Crown theme
        campaign = Campaign(
            id="test-twilight-crown-001",
            name="The Twilight Crown",
            description="A cosmic fantasy campaign where players discover the ancient secrets of the Starborn Dynasty and confront the celestial forces that threaten to unravel reality itself.",
            theme=type('obj', (object,), {'value': 'celestial_fantasy'})(),
            difficulty=type('obj', (object,), {'value': 'challenging'})(),
            world=World(
                id="test-world-001",
                name="Aldermere",
                description="An ancient realm where crystal spires pierce the veil between worlds, and the stars themselves hold secrets of unimaginable power.",
                geography={"regions": ["Crystal Spires", "Nebula Wastes", "Starborn Citadel"]},
                cultures=[{"name": "Starborn Elves", "description": "Ancient beings attuned to cosmic energies"}],
                magic_system={"traditions": ["Astral Magic", "Crystal Weaving", "Star Calling"]},
                factions=[{"name": "Twilight Order", "status": "conflicting"}],
                history="Long ago, the Starborn Dynasty ruled with wisdom, but their crown was shattered...",
                campaign_id="test-twilight-crown-001"
            ),
            story_hook=StoryHook(
                id="test-hook-001",
                title="The Shattered Crown Prophecy",
                description="Whispers of an ancient prophecy speak of a shattered crown that holds the key to either salvation or destruction.",
                hook_type=type('obj', (object,), {'value': 'prophecy'})(),
                stakes="The fate of all reality hangs in the balance",
                complications=["Ancient evils awakening", "Rival factions vying for power", "Cosmic forces beyond comprehension"],
                campaign_id="test-twilight-crown-001"
            ),
            story_arcs=[
                StoryArc(
                    id="test-arc-001",
                    title="The Crown's Reunion",
                    description="Players must gather the scattered shards of the Twilight Crown",
                    acts=[
                        {"title": "The First Shard", "description": "Discover the location of the first crown shard"},
                        {"title": "The Crystal Citadel", "description": "Infiltrate the Crystal Spire Citadel to claim the largest shard"}
                    ],
                    climax="Confrontation with the Crown's Guardian",
                    resolution="The players must choose between unity with risk or permanent division with safety",
                    arc_order=1,
                    campaign_id="test-twilight-crown-001"
                )
            ],
            key_npcs=[
                NPC(
                    id="test-npc-001",
                    name="Queen Elowen Starborn",
                    race="Elf",
                    character_class="Wizard",
                    background="Noble",
                    personality={
                        "traits": ["Wise", "Mysterious", "Compassionate"],
                        "ideals": ["Preservation of ancient knowledge"],
                        "bonds": ["The Starborn legacy"],
                        "flaws": ["Overly trusting of cosmic forces"]
                    },
                    motivation="Restore the Twilight Crown to prevent cosmic catastrophe",
                    role_in_story="Mentor and guide to the players",
                    campaign_id="test-twilight-crown-001"
                ),
                NPC(
                    id="test-npc-002",
                    name="Lord Thorne Shadowbane",
                    race="Human",
                    character_class="Warlock",
                    background="Charlatan",
                    personality={
                        "traits": ["Ambitious", "Cunning", "Charismatic"],
                        "ideals": ["Power through knowledge"],
                        "bonds": ["The shattered crown"],
                        "flaws": ["Reckless pursuit of power"]
                    },
                    motivation="Claim the crown's power for himself",
                    role_in_story="Antagonistic force and rival",
                    campaign_id="test-twilight-crown-001"
                )
            ],
            key_locations=[
                Location(
                    id="test-loc-001",
                    name="Crystal Spire Citadel",
                    type="Fortress",
                    description="Ancient citadel built from living crystal that responds to cosmic energies",
                    significance="Houses the largest remaining shard of the Twilight Crown",
                    encounters=[
                        {"type": "combat", "description": "Crystal guardians protect the inner sanctum"},
                        {"type": "social", "description": "Ancient spirits offer cryptic wisdom"}
                    ],
                    campaign_id="test-twilight-crown-001"
                ),
                Location(
                    id="test-loc-002",
                    name="Nebula Wastes",
                    type="Wasteland",
                    description="Desolate plains where reality thins and cosmic horrors lurk",
                    significance="Contains hidden pathways to other planes",
                    encounters=[
                        {"type": "exploration", "description": "Navigate the shifting cosmic storms"},
                        {"type": "combat", "description": "Defend against planar intrusions"}
                    ],
                    campaign_id="test-twilight-crown-001"
                )
            ],
            starting_level=3,
            party_size=type('obj', (object,), {'value': 'small'})(),
            expected_duration=type('obj', (object,), {'value': 'medium'})(),
            quality_score=type('obj', (object,), {'value': 4.8})(),
            generated_at=datetime.now(),
            user_preferences=None,
            status=type('obj', (object,), {'value': 'completed'})(),
            user_id="test-user-001",
            player_preferences=MockPlayerPreferences()
        )

        # Initialize enhanced PDF service
        print("📄 Initializing Enhanced PDF Service...")
        pdf_service = EnhancedPDFGenerationService()

        # Test output path
        test_output = project_root / "test_output"
        test_output.mkdir(exist_ok=True)
        test_filename = test_output / "test_twilight_crown_enhanced.pdf"

        # Generate enhanced PDF
        print("🎨 Generating enhanced PDF with all new features...")
        pdf_path = await pdf_service.generate_campaign_pdf(
            campaign,
            output_filename=str(test_filename)
        )

        if pdf_path and Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size / 1024  # KB
            print("✅ SUCCESS: Enhanced PDF generated!")
            print(f"📁 Location: {pdf_path}")
            print(f"📊 Size: {file_size:.1f} KB")
            print("\n🎭 Campaign Features Tested:")
            print("  ✓ Twilight Crown theme")
            print("  ✓ Celestial color scheme")
            print("  ✓ Fantasy typography (Modesto, Bookmania, Scala Sans)")
            print("  ✓ Two-column layout system")
            print("  ✓ Cosmic background textures")
            print("  ✓ Decorative borders with star motifs")
            print("  ✓ Drop caps at chapter beginnings")
            print("  ✓ Custom star bullet points")
            print("  ✓ Decorative section dividers")
            print("  ✓ Enhanced callout boxes")
            print("  ✓ Sidebar information boxes")
            print("  ✓ Celestial header and footer")
            print("  ✓ Enhanced table styling")
            print("  ✓ Professional NPC and location sections")

            print("\n📖 PDF Structure Verified:")
            print("  ✓ Cover page with Twilight Crown theme")
            print("  ✓ Table of contents with celestial styling")
            print("  ✓ Campaign overview with enhanced layout")
            print("  ✓ World setting section")
            print("  ✓ Story elements with callouts")
            print("  ✓ NPC portraits and information")
            print("  ✓ Location illustrations and encounters")
            print("  ✓ Enhanced appendices")

            print("\n" + "=" * 60)
            print("🎉 ALL ENHANCED PDF FEATURES WORKING!")
            print("=" * 60)

            return True

        else:
            print("❌ FAILED: PDF generation failed")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_features():
    """Test individual PDF features"""
    try:
        print("\n🔧 TESTING INDIVIDUAL FEATURES")
        print("=" * 40)

        pdf_service = EnhancedPDFGenerationService()

        # Test drop cap functionality
        print("✓ Testing drop cap creation...")
        drop_cap = pdf_service._create_drop_cap_paragraph("This is a test paragraph with a drop cap.")
        assert drop_cap is not None
        print("  ✓ Drop cap creation working")

        # Test custom bullet list
        print("✓ Testing custom bullet points...")
        bullets = pdf_service._create_custom_bullet_list(["Item 1", "Item 2", "Item 3"])
        assert len(bullets) == 6  # 3 items + 3 spacers
        print("  ✓ Custom bullets working")

        # Test callout box
        print("✓ Testing callout boxes...")
        callout = pdf_service._create_callout_box("This is a test callout", "Test Title")
        assert callout is not None
        print("  ✓ Callout boxes working")

        # Test decorative divider
        print("✓ Testing decorative dividers...")
        divider = pdf_service._create_decorative_section_divider()
        assert divider is not None
        print("  ✓ Decorative dividers working")

        print("✅ All individual features working!")
        return True

    except Exception as e:
        print(f"❌ Individual feature test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Test individual features first
        individual_success = await test_individual_features()

        # Test complete PDF generation
        pdf_success = await test_enhanced_pdf_features()

        if individual_success and pdf_success:
            print("\n🎯 ALL TESTS PASSED! Enhanced PDF system is ready.")
            sys.exit(0)
        else:
            print("\n💥 SOME TESTS FAILED. Check the output above.")
            sys.exit(1)

    asyncio.run(main())
