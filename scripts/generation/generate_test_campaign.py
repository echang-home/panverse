#!/usr/bin/env python3
"""
Generate a test campaign with reduced content for quick validation

This script generates a test campaign with:
- 25-30 pages total
- 7-15 images
- Shorter/placeholder text content
- All visual elements and layout features
- Complete table of contents and section headers

Usage: python generate_test_campaign.py
"""

import sys
import os
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

async def generate_test_campaign():
    """Generate a test campaign with reduced content for quick validation"""
    try:
        print("🧪 GENERATING TEST CAMPAIGN (QUICK VALIDATION MODE)")
        print("=" * 60)
        print("📊 Test Mode Features:")
        print("  ✓ 25-30 pages total")
        print("  ✓ 7-15 images")
        print("  ✓ Shorter/placeholder content")
        print("  ✓ All visual elements and layouts")
        print("  ✓ Complete table of contents")
        print("  ✓ Section headers and structure")
        print("=" * 60)

        # Import and run the full campaign generator in test mode
        from scripts.generation.generate_full_campaign import generate_full_campaign

        await generate_full_campaign(mode="test")

        print("\n" + "=" * 60)
        print("✅ TEST CAMPAIGN GENERATION COMPLETE!")
        print("=" * 60)
        print("🎯 Test campaign ready for validation:")
        print("  • Check PDF layout and design")
        print("  • Verify image placement and quality")
        print("  • Confirm table of contents structure")
        print("  • Validate section headers and formatting")
        print("  • Test overall document flow")

    except Exception as e:
        print(f"❌ Error generating test campaign: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(generate_test_campaign())
    sys.exit(0 if success else 1)
