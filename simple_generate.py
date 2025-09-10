#!/usr/bin/env python3
"""
Ultra-simple script to generate a sample D&D campaign using Claude API directly
"""
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Check for API key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("❌ ANTHROPIC_API_KEY not found!")
    print("Please check your .env file and ensure ANTHROPIC_API_KEY is set")
    exit(1)

try:
    import anthropic
except ImportError:
    print("❌ anthropic package not installed!")
    print("Install with: pip install anthropic")
    exit(1)

async def generate_sample_campaign():
    """Generate a sample campaign using Claude API directly"""

    print("🎲 Generating Sample D&D Campaign")
    print("=" * 50)

    # Sample campaign prompt
    prompt = """
You are a master D&D 5th Edition campaign designer. Create a complete sample campaign that would be approximately 20-30 pages when formatted as a PDF.

CAMPAIGN REQUIREMENTS:
- Theme: Epic Fantasy with dragons and ancient magic
- Difficulty: Medium (balanced challenge)
- Party Size: Small group (3-5 players)
- Starting Level: 3
- Duration: Medium (6-10 sessions)
- Setting: Medieval fantasy world with some unique twists

CAMPAIGN STRUCTURE:
Please provide a complete campaign with the following sections:

1. CAMPAIGN OVERVIEW
   - Title and tagline
   - Premise/summary (2-3 paragraphs)
   - Main plot hooks
   - Campaign goals/objectives

2. WORLD SETTING
   - World name and description
   - Key locations (3-5 important places)
   - Current world situation/political climate

3. PLAYER CHARACTERS
   - Recommended character concepts
   - Background suggestions
   - Party composition advice

4. MAIN PLOT
   - Central storyline
   - Key events and turning points
   - Climax and resolution ideas

5. KEY NPCs (4-6 important characters)
   - Name, role, personality, motivations
   - Relationship to plot

6. IMPORTANT LOCATIONS (4-6 locations)
   - Name, description, significance to plot
   - Notable features or dangers

7. STORY ARCS (3-4 major storylines)
   - Brief description of each arc
   - How they interconnect

8. ENCOUNTERS & COMBAT (6-8 encounters)
   - Brief description, difficulty, rewards

9. MAGIC ITEMS & TREASURES (4-6 items)
   - Name, description, powers

10. ADVENTURE HOOKS (5-7 plot hooks)
    - Ways to draw players into the campaign

Make this campaign creative, engaging, and ready to run. Include specific details that make it feel alive and immersive. Focus on quality storytelling with memorable characters, intriguing mysteries, and epic moments.

Format your response as a well-structured document that could be directly copied into a campaign guide.
"""

    try:
        # Initialize Claude client
        print("🔧 Initializing Claude AI client...")
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as init_error:
            print(f"❌ Error initializing Anthropic client: {init_error}")
            print("Trying alternative initialization...")
            # Try without any extra parameters
            try:
                client = anthropic.Anthropic()
                client.api_key = ANTHROPIC_API_KEY
            except Exception as alt_error:
                print(f"❌ Alternative initialization also failed: {alt_error}")
                return

        print("🚀 Generating campaign with Claude AI...")
        print("(This may take 30-60 seconds)")

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            temperature=0.7,
            system="You are a master D&D campaign designer creating engaging, high-quality adventures.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        campaign_content = response.content[0].text

        # Generate campaign ID
        campaign_id = f"sample_{int(datetime.now().timestamp())}"

        # Create output directory
        output_dir = Path("campaign_output") / f"sample_campaign_{campaign_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save campaign content
        campaign_file = output_dir / "campaign.txt"
        with open(campaign_file, 'w', encoding='utf-8') as f:
            f.write(f"# Sample D&D Campaign - {campaign_id}\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(campaign_content)

        # Save metadata
        metadata = {
            "campaign_id": campaign_id,
            "generated_at": datetime.now().isoformat(),
            "theme": "epic_fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium",
            "mode": "sample",
            "ai_model": "claude-3-5-sonnet",
            "word_count": len(campaign_content.split()),
            "sections": 10
        }

        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print("✅ Campaign generated successfully!")
        print(f"📁 Saved to: {output_dir}")
        print(f"📄 Campaign file: {campaign_file}")
        print(f"📊 Metadata: {metadata_file}")
        print(f"📏 Content length: {len(campaign_content)} characters")
        print(f"📝 Word count: {len(campaign_content.split())} words")

        # Show preview
        print("\n📖 CAMPAIGN PREVIEW:")
        print("-" * 30)
        preview_lines = campaign_content.split('\n')[:10]
        for line in preview_lines:
            if line.strip():
                print(f"  {line}")
        if len(campaign_content.split('\n')) > 10:
            print("  ... (campaign continues)")

        print("\n🎉 Your sample campaign is ready!")
        print("You can find the full campaign in the campaign_output directory.")

    except Exception as e:
        print(f"❌ Error generating campaign: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_sample_campaign())
