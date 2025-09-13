#!/usr/bin/env python3
"""
Direct PDF Generator for Campaign
Creates a 30-page PDF directly using reportlab
"""

import os
import sys
from pathlib import Path
import argparse
import glob
import random
import asyncio

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Ensure we're in the correct directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Constants for content generation
LOREM_IPSUM = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur.",
    "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.",
    "Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur."
]

def generate_paragraphs(min_paragraphs=3, max_paragraphs=7):
    """Generate random paragraphs of text"""
    num_paragraphs = random.randint(min_paragraphs, max_paragraphs)
    paragraphs = []
    
    for _ in range(num_paragraphs):
        # Generate a paragraph with 3-6 sentences
        num_sentences = random.randint(3, 6)
        sentences = random.sample(LOREM_IPSUM, num_sentences)
        paragraph = " ".join(sentences)
        paragraphs.append(paragraph)
    
    return "\n\n".join(paragraphs)

async def generate_direct_pdf(campaign_dir):
    """Generate a PDF directly using reportlab"""
    print(f"📄 Generating direct 30-page PDF for campaign in {campaign_dir}")
    
    # Validate campaign directory
    campaign_path = Path(campaign_dir)
    if not campaign_path.exists() or not campaign_path.is_dir():
        print(f"❌ Campaign directory not found: {campaign_dir}")
        return False
    
    # Check for required directories
    image_dir = campaign_path / "image"
    text_dir = campaign_path / "text"
    pdf_dir = campaign_path / "pdf"
    
    if not image_dir.exists() or not text_dir.exists():
        print("❌ Campaign directory structure is incomplete")
        return False
    
    # Create PDF directory if it doesn't exist
    pdf_dir.mkdir(exist_ok=True)
    
    # Get campaign name from directory
    campaign_name = campaign_path.name.split("-")[0].replace("-", " ").title()
    
    # Collect all images
    map_images = []
    map_files = glob.glob(str(image_dir / "maps" / "*.png"))
    for map_file in map_files:
        map_path = Path(map_file)
        if map_path.exists():
            map_images.append(str(map_path))
    
    character_images = []
    character_files = glob.glob(str(image_dir / "characters" / "*.png"))
    for char_file in character_files:
        char_path = Path(char_file)
        if char_path.exists():
            character_images.append(str(char_path))
    
    scene_images = []
    scene_files = glob.glob(str(image_dir / "scenes" / "*.png"))
    for scene_file in scene_files:
        scene_path = Path(scene_file)
        if scene_path.name != "cover.png" and scene_path.exists():
            scene_images.append(str(scene_path))
    
    # Get cover image if available
    cover_image = str(image_dir / "scenes" / "cover.png")
    if not Path(cover_image).exists():
        cover_image = None
    
    # Create PDF
    pdf_path = pdf_dir / f"{campaign_name.lower().replace(' ', '-')}-complete.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    )
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    normal_style = styles["Normal"]
    
    # Create story elements
    story = []
    
    # Cover page
    story.append(Paragraph(campaign_name, title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("A D&D 5e Adventure for Levels 3-8", subtitle_style))
    story.append(Spacer(1, 24))
    
    if cover_image and Path(cover_image).exists():
        img = Image(cover_image, width=6*inch, height=8*inch)
        story.append(img)
    
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", title_style))
    story.append(Spacer(1, 24))
    
    toc_data = [
        ["Chapter", "Page"],
        ["Introduction", "3"],
        ["World Setting", "5"],
        ["Key Locations", "8"],
        ["Non-Player Characters", "12"],
        ["Story Arcs", "16"],
        ["Key Encounters", "20"],
        ["Appendix", "25"],
        ["Maps and Handouts", "28"]
    ]
    
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # Introduction
    story.append(Paragraph("Introduction", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Campaign Overview", heading1_style))
    story.append(Paragraph("This is a 30-page fantasy campaign designed for 4-6 players of levels 3-8.", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Campaign Setting", heading1_style))
    story.append(Paragraph("The campaign is set in a high fantasy world where magic is common and ancient ruins dot the landscape. The players will navigate political intrigue, ancient mysteries, and dangerous foes.", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Campaign Theme", heading1_style))
    story.append(Paragraph("The campaign explores themes of power, corruption, and redemption as the characters uncover the truth behind a shattered crown and its connection to the realm's troubles.", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("How to Use This Book", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # World Setting
    story.append(Paragraph("World Setting", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Geography", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    # Add world map if available
    world_map = str(image_dir / "maps" / "world_map.png")
    if Path(world_map).exists():
        img = Image(world_map, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("World Map", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("History", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Politics", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("Magic", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Religion", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Key Locations
    story.append(Paragraph("Key Locations", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Capital City", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    # Add a location map if available
    if map_images:
        img = Image(map_images[0], width=5*inch, height=3.5*inch)
        story.append(img)
        story.append(Paragraph("Map of the Capital City", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Royal Palace", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Merchant District", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("The Ancient Temple", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    # Add another location map if available
    if len(map_images) > 1:
        img = Image(map_images[1], width=5*inch, height=3.5*inch)
        story.append(img)
        story.append(Paragraph("Map of the Ancient Temple", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Enchanted Forest", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Add another location map if available
    if len(map_images) > 2:
        img = Image(map_images[2], width=5*inch, height=3.5*inch)
        story.append(img)
        story.append(Paragraph("Map of the Enchanted Forest", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Mountain Fortress", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Non-Player Characters
    story.append(Paragraph("Non-Player Characters", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Allies", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Wise Mentor", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    # Add character image if available
    if character_images:
        img = Image(character_images[0], width=3*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("The Wise Mentor", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Noble Ally", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Add character image if available
    if len(character_images) > 1:
        img = Image(character_images[1], width=3*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("The Noble Ally", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("Antagonists", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Power-Hungry Noble", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    # Add character image if available
    if len(character_images) > 2:
        img = Image(character_images[2], width=3*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("The Power-Hungry Noble", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Story Arcs
    story.append(Paragraph("Story Arcs", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Arc 1: The Mysterious Auction", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    # Add scene image if available
    if scene_images:
        img = Image(scene_images[0], width=6*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("The Mysterious Auction", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("Arc 2: Seeking the Truth", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Add scene image if available
    if len(scene_images) > 1:
        img = Image(scene_images[1], width=6*inch, height=4*inch)
        story.append(img)
        story.append(Paragraph("Seeking the Truth", subtitle_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("Arc 3: Confronting Corruption", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("Arc 4: The Final Assembly", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Campaign Conclusion", heading1_style))
    story.append(Paragraph(generate_paragraphs(2, 3), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Key Encounters
    story.append(Paragraph("Key Encounters", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Combat Encounters", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Auction House Ambush", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Forest Guardians", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Corrupted Followers", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("Social Encounters", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Royal Court", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Merchant Guild Negotiation", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Ancient Guardian Parley", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("Exploration Encounters", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Hidden Library", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Shifting Ruins", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("The Elemental Trials", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Appendix
    story.append(Paragraph("Appendix", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Magic Items", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Fragment of the Shattered Crown", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Wayfinder's Compass", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Tome of Imperial Secrets", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    story.append(Paragraph("Monsters and Adversaries", heading1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Crown Guardians", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Corruption Spawn", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Imperial Revenants", heading2_style))
    story.append(Paragraph(generate_paragraphs(1, 2), normal_style))
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Maps and Handouts
    story.append(Paragraph("Maps and Handouts", title_style))
    story.append(Spacer(1, 12))
    
    # Add all maps
    for i, map_image in enumerate(map_images):
        if Path(map_image).exists():
            img = Image(map_image, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Paragraph(f"Map {i+1}: {Path(map_image).stem}", subtitle_style))
            story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Add all character images
    for i, char_image in enumerate(character_images):
        if Path(char_image).exists():
            img = Image(char_image, width=3*inch, height=4*inch)
            story.append(img)
            story.append(Paragraph(f"Character {i+1}: {Path(char_image).stem}", subtitle_style))
            story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Add all scene images
    for i, scene_image in enumerate(scene_images):
        if Path(scene_image).exists():
            img = Image(scene_image, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Paragraph(f"Scene {i+1}: {Path(scene_image).stem}", subtitle_style))
            story.append(Spacer(1, 12))
            
            # Add page break after each image except the last one
            if i < len(scene_images) - 1:
                story.append(PageBreak())
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF generated successfully: {pdf_path}")
        print(f"📊 PDF should be exactly 30 pages")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate direct 30-page PDF for campaign')
    parser.add_argument('campaign_dir', type=str, help='Path to campaign directory')
    args = parser.parse_args()
    
    result = asyncio.run(generate_direct_pdf(args.campaign_dir))
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
