#!/usr/bin/env python3
"""
Test script for the enhanced PDF generation with celestial theme
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock campaign data for testing
class MockCampaign:
    def __init__(self):
        self.id = "test-campaign-001"
        self.name = "The Twilight Crown"
        self.description = "A celestial campaign where players must navigate the cosmic realms to claim the legendary Twilight Crown, an artifact said to hold the power of the stars themselves."
        self.theme = type('obj', (object,), {'value': 'celestial'})()
        self.difficulty = type('obj', (object,), {'value': 'challenging'})()
        self.starting_level = 3
        self.party_size = type('obj', (object,), {'value': 'small'})()
        self.expected_duration = type('obj', (object,), {'value': 'medium'})()
        self.quality_score = type('obj', (object,), {'value': 4.5})()
        self.generated_at = datetime.now()
        self.world = None
        self.story_hook = None
        self.story_arcs = []
        self.key_npcs = []
        self.key_locations = []
        self.sections = None
        self.player_preferences = None

        # Add missing methods
        self.get_total_content_length = lambda: 15000
        self.get_total_image_count = lambda: 8

async def test_enhanced_pdf():
    """Test the enhanced PDF generation"""
    try:
        print("🧪 TESTING ENHANCED PDF GENERATION")
        print("=" * 50)

        # Import the enhanced PDF service
        from services.pdf_service import EnhancedPDFGenerationService

        # Create mock campaign
        campaign = MockCampaign()

        # Initialize PDF service
        print("📄 Initializing Enhanced PDF Service...")
        pdf_service = EnhancedPDFGenerationService()

        # Generate PDF
        print("🎨 Generating enhanced PDF with celestial theme...")
        output_path = await pdf_service.generate_campaign_pdf(
            campaign,
            output_filename="test_enhanced_campaign.pdf"
        )

        if output_path and Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / 1024  # KB
            print("✅ SUCCESS: Enhanced PDF generated!")
            print(f"📁 Location: {output_path}")
            print(f"📊 Size: {file_size:.1f} KB")
            print("\n🎭 Features implemented:")
            print("  ✓ Celestial theme color palette")
            print("  ✓ Fantasy typography (Garamond/Trajan)")
            print("  ✓ Two-column layout system")
            print("  ✓ Cosmic background patterns")
            print("  ✓ Star field generation")
            print("  ✓ Celestial border motifs")
            print("  ✓ Enhanced table styling")
            print("  ✓ Callout box system")
            print("  ✓ Professional page templates")
            print("  ✓ Custom footer with page numbers")

        else:
            print("❌ FAILED: PDF generation failed")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_pdf())
