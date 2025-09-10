#!/usr/bin/env python3
"""
Generate PDF for the current campaign
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# PDF generation imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, Flowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_campaign_pdf(campaign_data: dict, output_path: Path, images_dir: Path) -> str:
    """Generate a PDF campaign booklet in typical D&D book layout"""

    # Setup styles
    styles = getSampleStyleSheet()

    # Custom styles for D&D campaign book
    styles.add(ParagraphStyle(
        name='CampaignTitle',
        parent=styles['Title'],
        fontSize=28,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkred
    ))

    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=15,
        textColor=colors.darkgreen,
        borderWidth=1,
        borderColor=colors.darkgreen,
        borderPadding=5
    ))

    # Modify existing BodyText style if it exists
    if 'BodyText' in styles:
        styles['BodyText'].fontSize = 11
        styles['BodyText'].spaceAfter = 12
        styles['BodyText'].alignment = TA_JUSTIFY
        styles['BodyText'].leading = 14
    else:
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        ))

    styles.add(ParagraphStyle(
        name='TOCEntry',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkblue
    ))

    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    content = []

    # Title page
    content.append(Paragraph(campaign_data['title'], styles['CampaignTitle']))
    content.append(Spacer(1, 0.5*inch))

    # Get subtitle from concept file
    concept_file = images_dir.parent / "campaign_concept.txt"
    subtitle = ""
    if concept_file.exists():
        with open(concept_file, 'r') as f:
            concept_content = f.read()
            lines = concept_content.strip().split('\n')
            for line in lines[1:5]:
                if "Level Range:" in line:
                    subtitle = f"Level Range: {line.replace('Level Range:', '').strip()}"
                    break

    if subtitle:
        content.append(Paragraph(subtitle, styles['Subtitle']))

    content.append(Spacer(1, inch))

    # Campaign stats table
    stats_data = [
        ["Generated:", campaign_data['generated_at'][:10]],
        ["Sections:", str(len(campaign_data['sections']))],
        ["Images:", str(campaign_data['images_generated'])],
        ["Content Length:", f"{campaign_data['total_content_length']} chars"]
    ]

    stats_table = Table(stats_data, colWidths=[2*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(stats_table)
    content.append(PageBreak())

    # Table of Contents
    content.append(Paragraph("Table of Contents", styles['SectionHeader']))
    content.append(Spacer(1, 0.3*inch))

    for i, section in enumerate(campaign_data['sections'], 1):
        toc_entry = f"{i}. {section['name']}"
        content.append(Paragraph(toc_entry, styles['TOCEntry']))

    content.append(PageBreak())

    # Content sections
    for section in campaign_data['sections']:
        # Section header
        content.append(Paragraph(section['name'], styles['SectionHeader']))

        # Read section content
        section_file = images_dir.parent / section['file']
        if section_file.exists():
            with open(section_file, 'r') as f:
                section_content = f.read()

            # Skip the title line if it exists
            lines = section_content.strip().split('\n')
            if len(lines) > 1 and '"' in lines[0]:
                section_content = '\n'.join(lines[1:])

            # Split into paragraphs and add to PDF
            paragraphs = section_content.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    content.append(Paragraph(para, styles['BodyText']))

        content.append(Spacer(1, 0.2*inch))

        # Add relevant images for this section
        image_files = list(images_dir.glob("*.png"))
        if image_files:
            # Simple logic to add images based on section type
            section_images = []
            if "concept" in section['file'].lower():
                # Find cover image
                for img in image_files:
                    if "cover" in img.name.lower():
                        section_images = [img]
                        break
                if not section_images and image_files:
                    section_images = [image_files[0]]  # First image as cover
            elif "world" in section['file'].lower():
                # Find world map
                for img in image_files:
                    if "world" in img.name.lower() or "map" in img.name.lower():
                        section_images = [img]
                        break
            elif "npc" in section['file'].lower():
                # Find NPC portraits
                npc_images = [img for img in image_files if "npc" in img.name.lower()]
                section_images = npc_images[:2]  # Up to 2 NPC images
            elif "location" in section['file'].lower():
                # Find location images
                loc_images = [img for img in image_files if "location" in img.name.lower()]
                section_images = loc_images

            for img_path in section_images:
                try:
                    content.append(Spacer(1, 0.2*inch))
                    img = Image(str(img_path))
                    img.drawHeight = 3*inch
                    img.drawWidth = 4*inch
                    img.hAlign = 'CENTER'
                    content.append(img)

                    # Add caption
                    caption = img_path.stem.replace('_', ' ').replace('-', ' ').title()
                    content.append(Paragraph(f"<i>{caption}</i>", styles['BodyText']))
                    content.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    print(f"Warning: Could not add image {img_path}: {e}")

        content.append(PageBreak())

    # Generate PDF
    doc.build(content)
    return str(output_path)


def main():
    """Generate PDF for the current campaign"""
    campaign_dir = Path("campaign_output/The_Twilight_Crown_V1")
    summary_file = campaign_dir / "campaign_summary.json"

    if not summary_file.exists():
        print("❌ Campaign summary not found")
        return

    # Load campaign data
    with open(summary_file, 'r') as f:
        campaign_data = json.load(f)

    # Update image count
    images_dir = campaign_dir / "images"
    campaign_data['images_generated'] = len(list(images_dir.glob("*.png")))

    # Generate PDF
    pdf_file = campaign_dir / f"{campaign_data['folder']}.pdf"
    print("📄 Generating campaign PDF booklet...")

    try:
        pdf_path = generate_campaign_pdf(campaign_data, pdf_file, images_dir)
        print(f"✅ PDF generated: {pdf_path}")

        # Update summary with PDF info
        campaign_data['pdf_generated'] = True
        campaign_data['pdf_path'] = str(pdf_file)

        with open(summary_file, 'w') as f:
            json.dump(campaign_data, f, indent=2)

        print("✅ Campaign summary updated with PDF info")

    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
