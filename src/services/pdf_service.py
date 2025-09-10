"""
Enhanced PDF Generation Service for creating professional D&D campaign booklets
with fantasy typography, celestial theming, and comprehensive layout features
"""
import os
import logging
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether, Flowable, Frame, PageTemplate,
    BaseDocTemplate, NextPageTemplate, Preformatted, HRFlowable,
    BalancedColumns, KeepInFrame
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Polygon, String, Group
from reportlab.graphics import renderPDF
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.colors import Color

from domain.entities import Campaign

logger = logging.getLogger(__name__)


class EnhancedPDFGenerationService:
    """Enhanced service for generating professional D&D campaign booklets"""

    # Twilight Crown/Celestial Theme Color Palette
    THEME_COLORS = {
        # Primary palette - Deep blues and cosmic purples
        'deep_blue': colors.HexColor('#1a237e'),       # Deep cosmic blue
        'royal_blue': colors.HexColor('#283593'),      # Royal blue
        'bright_blue': colors.HexColor('#3949ab'),     # Bright blue
        'deep_purple': colors.HexColor('#4a148c'),     # Deep cosmic purple
        'royal_purple': colors.HexColor('#6a1b9a'),    # Royal purple
        'bright_purple': colors.HexColor('#7b1fa2'),   # Bright purple

        # Accent colors - Golds and silvers
        'antique_gold': colors.HexColor('#ffd700'),    # Antique gold
        'bright_gold': colors.HexColor('#ffb300'),     # Bright gold
        'star_silver': colors.HexColor('#e0e0e0'),     # Silver highlights
        'bright_silver': colors.HexColor('#f5f5f5'),   # Bright silver

        # Text colors
        'text_gold': colors.HexColor('#ffd700'),       # Gold text
        'text_silver': colors.HexColor('#f5f5f5'),     # Silver text
        'text_dark': colors.HexColor('#212121'),      # Dark text on light backgrounds
        'text_light': colors.HexColor('#f5f5f5'),      # Light text on dark backgrounds

        # Background gradients
        'dark_sky_start': colors.HexColor('#0d1b2a'),  # Dark sky gradient start
        'dark_sky_end': colors.HexColor('#1b263b'),    # Dark sky gradient end
        'twilight_start': colors.HexColor('#392F5A'),  # Twilight gradient start
        'twilight_end': colors.HexColor('#20639B'),    # Twilight gradient end

        # Border and accent colors
        'border_gold': colors.HexColor('#ffd700'),     # Gold borders
        'border_silver': colors.HexColor('#c0c0c0'),   # Silver borders
        'border_purple': colors.HexColor('#7b1fa2'),   # Purple borders
    }

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Page dimensions
        self.page_width, self.page_height = A4
        self.margin = 1.5 * cm
        self.gutter = 0.8 * cm

        # Initialize styles and fonts
        self.styles = getSampleStyleSheet()
        self._setup_fonts()
        self._setup_custom_styles()
        self._setup_page_templates()

    def _setup_fonts(self):
        """Setup fantasy-appropriate fonts with proper fallbacks"""
        try:
            # Try to load fantasy fonts (fallback to system fonts if not available)
            font_dir = Path(__file__).parent.parent / "assets" / "fonts"
            font_dir.mkdir(parents=True, exist_ok=True)

            # Fantasy font hierarchy - Headers
            self._register_font("Modesto", "Modesto-Regular.ttf", "Helvetica-Bold")  # Fantasy display font
            self._register_font("Bookmania", "Bookmania-Regular.ttf", "Times-Bold")  # Serif with character
            self._register_font("Trajan", "TrajanPro-Regular.otf", "Helvetica-Bold")  # Alternative fantasy display

            # Ensure all fonts are properly mapped
            self._ensure_font_fallbacks()

            # Body text fonts
            self._register_font("ScalaSans", "ScalaSans-Regular.ttf", "Helvetica")  # Readable fantasy-friendly
            self._register_font("ScalaSans", "ScalaSans-Bold.ttf", "Helvetica")  # Use regular as fallback for bold
            self._register_font("ScalaSans-Italic", "ScalaSans-Italic.ttf", "Helvetica-Oblique")

            # Fallback fonts for enhanced readability
            self._register_font("Garamond", "EBGaramond-Regular.ttf", "Times-Roman")
            self._register_font("Garamond-Bold", "EBGaramond-Bold.ttf", "Times-Bold")
            self._register_font("Garamond-Italic", "EBGaramond-Italic.ttf", "Times-Italic")

            logger.info("Fantasy typography system loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load custom fonts: {e}. Using system defaults.")

    def _register_font(self, font_name: str, font_file: str, fallback: str):
        """Register a font with fallback"""
        try:
            font_path = Path(__file__).parent.parent / "assets" / "fonts" / font_file
            if font_path.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                addMapping(font_name, 0, 0, font_name)
                # For bold variants, try to register separately or use fallback
                if "Bold" in font_file:
                    try:
                        pdfmetrics.registerFont(TTFont(f"{font_name}-Bold", str(font_path)))
                        addMapping(font_name, 1, 0, f"{font_name}-Bold")
                    except:
                        addMapping(font_name, 1, 0, font_name)  # Use regular as bold
                else:
                    addMapping(font_name, 1, 0, font_name)  # Bold maps to regular
                addMapping(font_name, 0, 1, font_name)  # Italic
                addMapping(font_name, 1, 1, font_name)  # Bold-Italic
            else:
                # Use fallback for all variants
                addMapping(fallback, 0, 0, font_name)
                addMapping(fallback, 1, 0, font_name)
                addMapping(fallback, 0, 1, font_name)
                addMapping(fallback, 1, 1, font_name)
        except Exception as e:
            logger.warning(f"Could not register font {font_name}: {e}")
            # Use fallback
            try:
                addMapping(fallback, 0, 0, font_name)
                addMapping(fallback, 1, 0, font_name)
                addMapping(fallback, 0, 1, font_name)
                addMapping(fallback, 1, 1, font_name)
            except:
                pass

    def _ensure_font_fallbacks(self):
        """Ensure all custom fonts have proper fallbacks"""
        font_fallbacks = {
            'Modesto': 'Helvetica-Bold',
            'Bookmania': 'Times-Bold',
            'Trajan': 'Helvetica-Bold',
            'ScalaSans': 'Helvetica',
            'ScalaSans-Bold': 'Helvetica-Bold',
            'ScalaSans-Italic': 'Helvetica-Oblique',
            'Garamond': 'Times-Roman',
            'Garamond-Bold': 'Times-Bold',
            'Garamond-Italic': 'Times-Italic'
        }

        # Also register the problematic fonts directly
        for font_name, fallback in font_fallbacks.items():
            try:
                addMapping(fallback, 0, 0, font_name)
                addMapping(fallback, 1, 0, font_name)
                addMapping(fallback, 0, 1, font_name)
                addMapping(fallback, 1, 1, font_name)
            except Exception as e:
                logger.debug(f"Could not register fallback mapping for {font_name}: {e}")

        for font_name, fallback in font_fallbacks.items():
            try:
                # Check if font is registered, if not, register fallback
                pdfmetrics.getFont(font_name)
            except KeyError:
                try:
                    addMapping(fallback, 0, 0, font_name)
                    addMapping(fallback, 1, 0, font_name)
                    addMapping(fallback, 0, 1, font_name)
                    addMapping(fallback, 1, 1, font_name)
                    logger.info(f"Using fallback font {fallback} for {font_name}")
                except Exception as e:
                    logger.warning(f"Could not set fallback for {font_name}: {e}")

    def _setup_custom_styles(self):
        """Set up enhanced fantasy typography system with proper hierarchy"""

        # Chapter Titles - 24pt, bold, with decorative elements
        self.styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',  # Use standard font
            fontSize=24,
            spaceAfter=30,
            spaceBefore=40,
            alignment=TA_CENTER,
            textColor=self.THEME_COLORS['text_gold'],
            leading=28,
            borderColor=self.THEME_COLORS['border_gold'],
            borderWidth=1,
            borderPadding=12,
            backColor=self.THEME_COLORS['twilight_start'],
        ))

        # Campaign Title - Heroic, fantasy-style
        self.styles.add(ParagraphStyle(
            name='CampaignTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',  # Use standard font
            fontSize=32,
            spaceAfter=40,
            alignment=TA_CENTER,
            textColor=self.THEME_COLORS['text_gold'],
            leading=36,
            borderColor=self.THEME_COLORS['border_gold'],
            borderWidth=2,
            borderPadding=15,
            backColor=self.THEME_COLORS['deep_purple'],
        ))

        # Section Headers - 18pt, bold, with underline or border
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontName='Times-Bold',  # Use standard font
            fontSize=18,
            spaceAfter=25,
            spaceBefore=30,
            textColor=self.THEME_COLORS['text_silver'],
            leading=22,
            borderColor=self.THEME_COLORS['border_purple'],
            borderWidth=0.5,
            borderPadding=8,
            backColor=self.THEME_COLORS['royal_blue'],
        ))

        # Subsection Headers - 14pt, bold or italic
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontName='Times-Bold',  # Use standard font
            fontSize=14,
            spaceAfter=18,
            spaceBefore=20,
            textColor=self.THEME_COLORS['text_silver'],
            leading=18,
        ))

        # Body Text - 10-11pt, optimized for readability (modify existing)
        if 'BodyText' in self.styles:
            body_style = self.styles['BodyText']
            body_style.fontName = 'Times-Roman'
            body_style.fontSize = 10.5
            body_style.spaceAfter = 12
            body_style.alignment = TA_JUSTIFY
            body_style.textColor = self.THEME_COLORS['text_light']
            body_style.leading = 15
        else:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontName='Times-Roman',
                fontSize=10.5,
                spaceAfter=12,
                alignment=TA_JUSTIFY,
                textColor=self.THEME_COLORS['text_light'],
                leading=15,
            ))

        # NPC Names - Distinctive styling with celestial theme
        self.styles.add(ParagraphStyle(
            name='NPCName',
            parent=self.styles['Normal'],
            fontName='Bookmania',  # Fantasy serif
            fontSize=14,
            textColor=self.THEME_COLORS['text_gold'],
            spaceAfter=8,
            leading=18,
        ))

        # Callout Box Style - Highlighted with backgrounds
        self.styles.add(ParagraphStyle(
            name='CalloutText',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=9.5,
            textColor=self.THEME_COLORS['text_light'],
            backgroundColor=self.THEME_COLORS['royal_purple'],
            borderColor=self.THEME_COLORS['border_gold'],
            borderWidth=1.5,
            borderPadding=10,
            leading=13,
            spaceAfter=15,
        ))

        # Sidebar Box Style
        self.styles.add(ParagraphStyle(
            name='SidebarText',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=9,
            textColor=self.THEME_COLORS['text_dark'],
            backgroundColor=self.THEME_COLORS['bright_silver'],
            borderColor=self.THEME_COLORS['border_purple'],
            borderWidth=1,
            borderPadding=8,
            leading=12,
            spaceAfter=10,
        ))

        # Flavor Text - Italic, atmospheric
        self.styles.add(ParagraphStyle(
            name='FlavorText',
            parent=self.styles['Normal'],
            fontName='Times-Italic',
            fontSize=10,
            textColor=self.THEME_COLORS['text_silver'],
            spaceAfter=16,
            leading=14,
        ))

        # Drop Cap Style
        self.styles.add(ParagraphStyle(
            name='DropCap',
            parent=self.styles['Normal'],
            fontName='Times-Bold',  # Use standard font
            fontSize=36,
            textColor=self.THEME_COLORS['text_gold'],
            leading=32,
            spaceAfter=8,
        ))

        # Footer Text
        self.styles.add(ParagraphStyle(
            name='FooterText',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=8,
            textColor=self.THEME_COLORS['text_silver'],
            alignment=TA_CENTER,
            leading=10,
        ))

    def _setup_page_templates(self):
        """Setup professional page templates with enhanced two-column layout"""
        self.templates = {}

        # Cover page template
        self.templates['cover'] = PageTemplate(
            id='cover',
            frames=[
                Frame(
                    self.margin, self.margin,
                    self.page_width - 2 * self.margin,
                    self.page_height - 2 * self.margin,
                    id='cover_frame'
                )
            ],
            onPage=self._draw_cover_background
        )

        # Enhanced two-column content page template
        content_width = self.page_width - 2 * self.margin
        column_width = (content_width - self.gutter) / 2
        column_height = self.page_height - 4 * self.margin  # More space for footer

        self.templates['content'] = PageTemplate(
            id='content',
            frames=[
                Frame(
                    self.margin, 3 * self.margin,  # Higher top margin for header space
                    column_width, column_height,
                    id='left_column'
                ),
                Frame(
                    self.margin + column_width + self.gutter, 3 * self.margin,
                    column_width, column_height,
                    id='right_column'
                )
            ],
            onPage=self._draw_content_background
        )

        # Single column template for special content
        self.templates['single_column'] = PageTemplate(
            id='single_column',
            frames=[
                Frame(
                    self.margin, 3 * self.margin,
                    content_width, column_height,
                    id='single_column_frame'
                )
            ],
            onPage=self._draw_content_background
        )

        # Full page art template
        self.templates['full_art'] = PageTemplate(
            id='full_art',
            frames=[
                Frame(
                    self.margin, self.margin,
                    self.page_width - 2 * self.margin,
                    self.page_height - 2 * self.margin,
                    id='full_art_frame'
                )
            ],
            onPage=self._draw_full_art_background
        )

        # Chapter opener template (single column with space for illustration)
        self.templates['chapter_opener'] = PageTemplate(
            id='chapter_opener',
            frames=[
                Frame(
                    self.margin, self.margin,
                    content_width, self.page_height - 2 * self.margin,
                    id='chapter_frame'
                )
            ],
            onPage=self._draw_chapter_background
        )

    def _draw_cover_background(self, canvas, doc):
        """Draw enhanced celestial-themed cover background"""
        canvas.saveState()

        # Draw twilight gradient background
        self._draw_twilight_gradient(canvas, self.page_width, self.page_height)

        # Draw enhanced star field with nebula effects
        self._draw_enhanced_star_field(canvas, 80)

        # Draw nebula clouds
        self._draw_nebula_clouds(canvas, 5)

        # Draw decorative celestial border
        self._draw_enhanced_celestial_border(canvas, self.margin * 0.7)

        canvas.restoreState()

    def _draw_content_background(self, canvas, doc):
        """Draw content page background with sophisticated celestial elements"""
        canvas.saveState()

        # Draw dark sky gradient background
        self._draw_dark_sky_background(canvas, self.page_width, self.page_height)

        # Draw subtle star field
        self._draw_enhanced_star_field(canvas, 25, alpha=0.3)

        # Draw decorative page border with cosmic motifs
        self._draw_cosmic_page_border(canvas)

        # Draw header with celestial design
        self._draw_celestial_header(canvas)

        # Draw footer with campaign info
        self._draw_enhanced_footer(canvas, doc)

        canvas.restoreState()

    def _draw_full_art_background(self, canvas, doc):
        """Draw full art page background with minimal decorative elements"""
        canvas.saveState()

        # Subtle dark background for art pages
        self._draw_dark_sky_background(canvas, self.page_width, self.page_height)

        # Very subtle border
        self._draw_minimal_cosmic_border(canvas)

        canvas.restoreState()

    def _draw_chapter_background(self, canvas, doc):
        """Draw chapter opener background"""
        canvas.saveState()

        # Draw enhanced twilight gradient
        self._draw_twilight_gradient(canvas, self.page_width, self.page_height)

        # Draw moderate star field
        self._draw_enhanced_star_field(canvas, 40, alpha=0.5)

        # Draw decorative border
        self._draw_cosmic_page_border(canvas)

        canvas.restoreState()

    def _draw_twilight_gradient(self, canvas, width, height):
        """Draw twilight gradient background"""
        for i in range(0, int(height), 3):
            alpha = i / height
            color = self._interpolate_color(
                self.THEME_COLORS['twilight_start'],
                self.THEME_COLORS['twilight_end'],
                alpha
            )
            canvas.setFillColor(color)
            canvas.rect(0, i, width, 3, fill=1)

    def _draw_dark_sky_background(self, canvas, width, height):
        """Draw dark sky gradient background"""
        for i in range(0, int(height), 3):
            alpha = i / height
            color = self._interpolate_color(
                self.THEME_COLORS['dark_sky_start'],
                self.THEME_COLORS['dark_sky_end'],
                alpha * 0.7  # Softer gradient
            )
            canvas.setFillColor(color)
            canvas.rect(0, i, width, 3, fill=1)

    def _draw_enhanced_star_field(self, canvas, num_stars, alpha=0.8):
        """Draw enhanced star field with different star types"""
        canvas.setFillColor(colors.white, alpha)

        for _ in range(num_stars):
            x = random.random() * self.page_width
            y = random.random() * self.page_height

            # Random star size and type
            star_type = random.choice(['small', 'medium', 'large', 'cluster'])
            brightness = random.random() * 0.5 + 0.5  # 0.5 to 1.0

            if star_type == 'small':
                size = random.random() * 1.5 + 0.5
                canvas.setFillColor(colors.white, alpha * brightness)
                canvas.circle(x, y, size, fill=1)
            elif star_type == 'medium':
                size = random.random() * 2.5 + 1.5
                canvas.setFillColor(colors.white, alpha * brightness)
                self._draw_star_shape(canvas, x, y, size)
            elif star_type == 'large':
                size = random.random() * 4 + 2
                canvas.setFillColor(colors.white, alpha * brightness * 0.8)
                self._draw_star_shape(canvas, x, y, size)
            else:  # cluster
                cluster_size = random.random() * 8 + 4
                num_cluster_stars = random.randint(3, 7)
                for _ in range(num_cluster_stars):
                    offset_x = (random.random() - 0.5) * cluster_size
                    offset_y = (random.random() - 0.5) * cluster_size
                    star_size = random.random() * 1.5 + 0.5
                    canvas.setFillColor(colors.white, alpha * brightness * 0.6)
                    canvas.circle(x + offset_x, y + offset_y, star_size, fill=1)

    def _draw_nebula_clouds(self, canvas, num_clouds):
        """Draw nebula cloud effects"""
        for _ in range(num_clouds):
            x = random.random() * self.page_width
            y = random.random() * self.page_height
            size = random.random() * 100 + 50

            # Create nebula effect with multiple overlapping circles
            for i in range(5):
                nebula_color = self._interpolate_color(
                    self.THEME_COLORS['deep_purple'],
                    self.THEME_COLORS['bright_purple'],
                    random.random()
                )
                canvas.setFillColor(nebula_color, random.random() * 0.1 + 0.05)
                cloud_size = size * (random.random() * 0.5 + 0.5)
                canvas.circle(x + random.random() * size - size/2,
                            y + random.random() * size - size/2,
                            cloud_size, fill=1)

    def _draw_star_shape(self, canvas, x, y, size):
        """Draw a proper star shape"""
        canvas.setFillColor(colors.white, 0.8)
        canvas.setStrokeColor(colors.white, 0.8)

        # Draw star as a series of triangles
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.5
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))

        # Draw filled triangles to create star shape
        for i in range(0, 10, 2):
            p1 = points[i]
            p2 = points[(i + 2) % 10]
            p3 = points[(i + 5) % 10]

            path = canvas.beginPath()
            path.moveTo(p1[0], p1[1])
            path.lineTo(p2[0], p2[1])
            path.lineTo(p3[0], p3[1])
            path.close()
            canvas.drawPath(path, fill=1, stroke=0)

    def _draw_star(self, canvas, x, y, size):
        """Draw a star shape using lines"""
        canvas.setFillColor(colors.white, 0.6)
        canvas.setStrokeColor(colors.white, 0.6)

        # Draw star as a series of triangles
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.5
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))

        # Draw filled triangles to create star shape
        for i in range(0, 10, 2):
            p1 = points[i]
            p2 = points[(i + 2) % 10]
            p3 = points[(i + 5) % 10]

            path = canvas.beginPath()
            path.moveTo(p1[0], p1[1])
            path.lineTo(p2[0], p2[1])
            path.lineTo(p3[0], p3[1])
            path.close()
            canvas.drawPath(path, fill=1, stroke=0)

    def _draw_enhanced_celestial_border(self, canvas, margin):
        """Draw enhanced celestial-themed border with cosmic motifs"""
        # Outer gold border
        canvas.setStrokeColor(self.THEME_COLORS['border_gold'], 0.9)
        canvas.setLineWidth(3)
        canvas.rect(margin, margin,
                   self.page_width - 2 * margin,
                   self.page_height - 2 * margin)

        # Inner purple accent border
        inner_margin = margin + 6
        canvas.setStrokeColor(self.THEME_COLORS['border_purple'], 0.6)
        canvas.setLineWidth(1.5)
        canvas.rect(inner_margin, inner_margin,
                   self.page_width - 2 * inner_margin,
                   self.page_height - 2 * inner_margin)

        # Add corner star motifs
        self._draw_corner_stars(canvas, margin)

    def _draw_cosmic_page_border(self, canvas):
        """Draw cosmic-themed page border with star patterns"""
        border_margin = self.margin * 0.7

        # Main border
        canvas.setStrokeColor(self.THEME_COLORS['border_silver'], 0.4)
        canvas.setLineWidth(1)
        canvas.rect(border_margin, border_margin,
                   self.page_width - 2 * border_margin,
                   self.page_height - 2 * border_margin)

        # Add subtle star decorations along the border
        self._draw_border_stars(canvas, border_margin)

    def _draw_corner_stars(self, canvas, margin):
        """Draw decorative stars at corners"""
        star_size = 8
        corners = [
            (margin + star_size, self.page_height - margin - star_size),
            (self.page_width - margin - star_size, self.page_height - margin - star_size),
            (margin + star_size, margin + star_size),
            (self.page_width - margin - star_size, margin + star_size)
        ]

        canvas.setFillColor(self.THEME_COLORS['star_silver'], 0.8)
        for x, y in corners:
            self._draw_star_shape(canvas, x, y, star_size)

    def _draw_border_stars(self, canvas, margin):
        """Draw small stars along the border"""
        canvas.setFillColor(self.THEME_COLORS['star_silver'], 0.3)

        # Top and bottom borders
        for side in ['top', 'bottom']:
            y = self.page_height - margin if side == 'top' else margin
            for x in range(int(margin), int(self.page_width - margin), 30):
                if random.random() > 0.7:  # Only draw some stars for subtle effect
                    self._draw_star_shape(canvas, x, y, 2)

        # Left and right borders
        for side in ['left', 'right']:
            x = margin if side == 'left' else self.page_width - margin
            for y in range(int(margin), int(self.page_height - margin), 30):
                if random.random() > 0.7:
                    self._draw_star_shape(canvas, x, y, 2)

    def _draw_celestial_header(self, canvas):
        """Draw celestial-themed header with decorative elements"""
        header_y = self.page_height - 2 * self.margin

        # Draw decorative separator line
        canvas.setStrokeColor(self.THEME_COLORS['border_gold'], 0.6)
        canvas.setLineWidth(2)
        canvas.line(self.margin, header_y, self.page_width - self.margin, header_y)

        # Add small stars along the separator
        canvas.setFillColor(self.THEME_COLORS['star_silver'], 0.5)
        for x in range(int(self.margin + 20), int(self.page_width - self.margin - 20), 40):
            if random.random() > 0.5:
                self._draw_star_shape(canvas, x, header_y + 3, 3)

    def _draw_enhanced_footer(self, canvas, doc):
        """Draw enhanced footer with campaign name, page number, and decorative elements"""
        footer_y = self.margin * 0.8

        # Draw decorative separator line above footer
        canvas.setStrokeColor(self.THEME_COLORS['border_silver'], 0.4)
        canvas.setLineWidth(1)
        canvas.line(self.margin, footer_y + 15, self.page_width - self.margin, footer_y + 15)

        # Campaign name on left
        canvas.setFont('Times-Roman', 8)
        canvas.setFillColor(self.THEME_COLORS['text_silver'])
        campaign_name = getattr(doc, 'campaign_name', 'D&D Campaign')
        canvas.drawString(self.margin, footer_y, campaign_name)

        # Page number on right with celestial styling
        page_num = canvas.getPageNumber()
        page_text = f"✦ {page_num} ✦"
        canvas.setFont('Times-Roman', 8)
        text_width = canvas.stringWidth(page_text, 'Times-Roman', 8)
        canvas.drawString(self.page_width - self.margin - text_width, footer_y, page_text)

        # Add small constellation pattern in footer
        canvas.setFillColor(self.THEME_COLORS['star_silver'], 0.3)
        center_x = self.page_width / 2
        for i in range(5):
            angle = i * 2 * math.pi / 5
            x = center_x + 30 * math.cos(angle)
            y = footer_y + 8 + 5 * math.sin(angle)
            canvas.circle(x, y, 1, fill=1)

    def _draw_minimal_border(self, canvas):
        """Draw minimal border for full art pages"""
        canvas.setStrokeColor(self.THEME_COLORS['border_silver'], 0.2)
        canvas.setLineWidth(0.5)
        canvas.rect(self.margin * 0.5, self.margin * 0.5,
                   self.page_width - self.margin,
                   self.page_height - self.margin)

    def _interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        r1, g1, b1 = color1.red, color1.green, color1.blue
        r2, g2, b2 = color2.red, color2.green, color2.blue

        r = r1 + (r2 - r1) * factor
        g = g1 + (g2 - g1) * factor
        b = b1 + (b2 - b1) * factor

        return colors.Color(r, g, b)

    async def generate_campaign_pdf(self, campaign: Campaign, output_filename: Optional[str] = None, mode: str = "production") -> str:
        """Generate a professional PDF booklet for the campaign"""
        if not output_filename:
            safe_name = "".join(c for c in campaign.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_filename = f"{safe_name.replace(' ', '_')}_{campaign.id}.pdf"
            output_path = self.output_dir / output_filename
        else:
            # Handle absolute paths
            output_path = Path(output_filename)
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Create enhanced PDF document with templates
            doc = BaseDocTemplate(
                str(output_path),
                pagesize=A4,
                pageTemplates=list(self.templates.values()),
                showBoundary=0  # Hide frame boundaries in production
            )

            # Set campaign name for footer
            doc.campaign_name = campaign.name

            # Build PDF content
            content = self._build_enhanced_pdf_content(campaign, mode)

            # Generate PDF
            doc.build(content)

            logger.info(f"Enhanced PDF generated successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate enhanced PDF: {e}")
            raise

    def _build_enhanced_pdf_content(self, campaign: Campaign, mode: str = "production") -> List[Flowable]:
        """Build enhanced PDF content with professional layout"""
        content = []

        # Cover page with template switch
        content.extend(self._create_enhanced_title_page(campaign))
        content.append(NextPageTemplate('content'))  # Switch to content template

        # Table of contents
        content.extend(self._create_enhanced_table_of_contents(campaign))
        content.append(PageBreak())

        # Generate enhanced content from campaign sections based on mode
        if campaign.sections:
            # Adjust sections based on mode
            if mode == "test":
                # Test mode: Include only key sections for quick validation (25-30 pages)
                key_section_ids = ["introduction", "setting", "locations", "npcs", "encounters"]
                sections_to_include = [s for s in campaign.sections if s.section_id in key_section_ids][:5]  # Limit to 5 sections max
            else:
                # Production mode: Include all sections (30-70 pages)
                sections_to_include = campaign.sections

            for section in sections_to_include:
                content.extend(self._create_enhanced_section_content(section, mode))
                content.append(PageBreak())
        else:
            # Enhanced fallback structure
            content.extend(self._create_enhanced_campaign_overview(campaign))
            content.append(PageBreak())

            # World setting with full art page (only in production mode)
            if campaign.world and mode == "production":
                content.append(NextPageTemplate('full_art'))
                content.extend(self._create_enhanced_world_section(campaign.world))
                content.append(NextPageTemplate('content'))
                content.append(PageBreak())

            # Story elements
            content.extend(self._create_enhanced_story_elements(campaign))
            content.append(PageBreak())

            # NPCs with portraits (limit in test mode)
            if campaign.key_npcs:
                if mode == "test":
                    # Test mode: Include only 2-3 NPCs
                    limited_npcs = campaign.key_npcs[:3]
                    content.extend(self._create_enhanced_npcs_section(limited_npcs))
                else:
                    # Production mode: Include all NPCs
                    content.extend(self._create_enhanced_npcs_section(campaign.key_npcs))
                content.append(PageBreak())

            # Locations with illustrations (limit in test mode)
            if campaign.key_locations:
                if mode == "test":
                    # Test mode: Include only 2-3 locations
                    limited_locations = campaign.key_locations[:3]
                    content.extend(self._create_enhanced_locations_section(limited_locations))
                else:
                    # Production mode: Include all locations
                    content.extend(self._create_enhanced_locations_section(campaign.key_locations))
                content.append(PageBreak())

        # Enhanced appendices (simplified in test mode)
        content.extend(self._create_enhanced_appendices(campaign, mode))

        return content

    def _create_enhanced_title_page(self, campaign: Campaign) -> List[Flowable]:
        """Create enhanced title page with Twilight Crown theme"""
        content = []

        # Add vertical spacing for centered layout
        content.append(Spacer(1, 2*inch))

        # Main title: "The Twilight Crown"
        main_title = Paragraph("The Twilight Crown", self.styles['CampaignTitle'])
        content.append(main_title)

        # Subtitle: "Legacy of the Starborn Dynasty"
        subtitle = Paragraph("Legacy of the Starborn Dynasty", self.styles['SubsectionHeader'])
        content.append(subtitle)

        content.append(Spacer(1, 1.5*inch))

        # Campaign details with celestial styling
        level_range = f"{campaign.starting_level}+"
        details_data = [
            ["Theme:", campaign.theme.value.title()],
            ["Difficulty:", campaign.difficulty.value.title()],
            ["Level Range:", level_range],
            ["Duration:", campaign.expected_duration.value.replace('_', ' ').title()],
            ["Party Size:", campaign.party_size.value.title()],
            ["Generated:", campaign.generated_at.strftime("%B %d, %Y")]
        ]

        details_table = Table(details_data, colWidths=[2.5*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.THEME_COLORS['royal_blue']),
            ('BACKGROUND', (1, 0), (-1, -1), self.THEME_COLORS['deep_blue']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.THEME_COLORS['text_gold']),
            ('TEXTCOLOR', (1, 0), (-1, -1), self.THEME_COLORS['text_silver']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Bookmania'),
            ('FONTNAME', (1, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.THEME_COLORS['border_gold']),
            ('INNERGRID', (0, 0), (-1, -1), 1, self.THEME_COLORS['border_silver']),
        ]))

        content.append(details_table)

        content.append(Spacer(1, inch))

        # Enhanced description with flavor text styling
        if campaign.description:
            content.append(Paragraph("Campaign Premise", self.styles['SectionHeader']))
            content.append(Spacer(1, 0.2*inch))

            # Create drop cap for the first paragraph
            first_para = campaign.description.split('\n\n')[0]
            if first_para:
                drop_cap_content = self._create_drop_cap_paragraph(first_para)
                content.append(drop_cap_content)

            # Add remaining paragraphs normally
            remaining_paras = campaign.description.split('\n\n')[1:]
            for para in remaining_paras:
                if para.strip():
                    content.append(Paragraph(para.strip(), self.styles['FlavorText']))

        # Add cover image with celestial artwork
        cover_image_path = self.output_dir.parent / "images" / "cover_image.png"
        if cover_image_path.exists():
            content.append(Spacer(1, inch))
            try:
                img = Image(str(cover_image_path))
                img.drawHeight = 4*inch
                img.drawWidth = 5*inch
                img.hAlign = 'CENTER'
                content.append(img)

                # Add caption for cover art
                content.append(Spacer(1, 0.2*inch))
                caption = "The Twilight Crown - A cosmic artifact of unimaginable power"
                content.append(Paragraph(caption, self.styles['FlavorText']))

            except Exception as e:
                logger.warning(f"Could not add cover image: {e}")

        return content

    def _create_drop_cap_paragraph(self, text: str) -> Flowable:
        """Create a paragraph with a drop cap at the beginning"""
        if not text or len(text) < 2:
            return Paragraph(text, self.styles['FlavorText'])

        # Extract first character for drop cap
        first_char = text[0]
        remaining_text = text[1:]

        # Create table with drop cap and text
        drop_cap_data = [[
            Paragraph(first_char, self.styles['DropCap']),
            Paragraph(remaining_text, self.styles['FlavorText'])
        ]]

        drop_cap_table = Table(drop_cap_data, colWidths=[0.8*inch, 5*inch])
        drop_cap_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        return drop_cap_table

    def _create_custom_bullet_list(self, items: List[str]) -> List[Flowable]:
        """Create a list with custom star bullet points"""
        content = []
        for item in items:
            # Create bullet with star symbol
            bullet_text = f"✦ {item}"
            content.append(Paragraph(bullet_text, self.styles['BodyText']))
            content.append(Spacer(1, 0.1*inch))
        return content

    def _create_decorative_section_divider(self) -> Flowable:
        """Create a decorative section divider with celestial motifs"""
        # Create a drawing with decorative elements
        drawing = Drawing(self.page_width - 2*self.margin, 20)

        # Draw decorative line with stars
        line_y = 10
        drawing.add(Line(self.margin, line_y, self.page_width - self.margin, line_y,
                        strokeColor=self.THEME_COLORS['border_gold'],
                        strokeWidth=2))

        # Add star decorations
        for i in range(3):
            x_pos = self.margin + (self.page_width - 2*self.margin) * (i + 1) / 4
            # Add star shape using polygon
            star_points = []
            for j in range(10):
                angle = j * math.pi / 5
                radius = 4 if j % 2 == 0 else 2
                star_points.extend([
                    x_pos + radius * math.cos(angle),
                    line_y + radius * math.sin(angle) + 5
                ])

            star = Polygon(star_points,
                          fillColor=self.THEME_COLORS['star_silver'],
                          strokeColor=self.THEME_COLORS['border_gold'],
                          strokeWidth=0.5)
            drawing.add(star)

        return drawing

    def _create_callout_box(self, text: str, title: str = None) -> Flowable:
        """Create a highlighted callout box with celestial styling"""
        content = []

        if title:
            content.append(Paragraph(f"**{title}**", self.styles['CalloutText']))
            content.append(Spacer(1, 0.1*inch))

        content.append(Paragraph(text, self.styles['CalloutText']))

        # Wrap in KeepTogether to keep the callout together
        return KeepTogether(content)

    def _create_sidebar_box(self, text: str, title: str = None) -> Flowable:
        """Create a sidebar box for additional information"""
        content = []

        if title:
            content.append(Paragraph(title, self.styles['SidebarText']))
            content.append(Spacer(1, 0.05*inch))

        content.append(Paragraph(text, self.styles['SidebarText']))

        return KeepTogether(content)

    def _create_enhanced_table_of_contents(self, campaign: Campaign) -> List[Flowable]:
        """Create enhanced table of contents with celestial styling"""
        content = []

        # TOC header with decorative styling
        toc_title = Paragraph("Campaign Contents", self.styles['SectionHeader'])
        content.append(toc_title)

        content.append(Spacer(1, 0.3*inch))

        # Create TOC entries with enhanced styling
        toc_entries = []

        if campaign.sections:
            for i, section in enumerate(campaign.sections, 1):
                toc_entries.append([f"{i}. {section.title}", ""])
                # Add subsections
                if hasattr(section, 'subsections') and section.subsections:
                    for j, subsection in enumerate(section.subsections, 1):
                        toc_entries.append([f"   {i}.{j}. {subsection.title}", ""])
        else:
            # Fallback TOC structure
            toc_entries = [
                ["1. Campaign Overview", ""],
                ["2. World Setting", ""],
                ["3. Story Elements", ""],
                ["4. Key Characters", ""],
                ["5. Important Locations", ""],
                ["6. Appendices", ""]
            ]

        # Create enhanced TOC table
        toc_table = Table(toc_entries, colWidths=[5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), self.THEME_COLORS['text_dark']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))

        content.append(toc_table)

        return content

    def _create_enhanced_section_content(self, section: Any, mode: str = "production") -> List[Flowable]:
        """Create enhanced content for a campaign section with visual elements"""
        content = []

        # Enhanced section header with celestial styling
        section_header = Paragraph(section.title, self.styles['SectionHeader'])
        content.append(section_header)

        # Add decorative section divider
        content.append(Spacer(1, 0.1*inch))
        content.append(self._create_decorative_section_divider())
        content.append(Spacer(1, 0.2*inch))

        # Section content with enhanced formatting
        if section.content:
            paragraphs = section.content.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    # Check for callout boxes (marked with ** or ***)
                    if para.strip().startswith('**') and para.strip().endswith('**'):
                        callout_text = para.strip().strip('*')
                        content.append(self._create_callout_box(callout_text))
                        content.append(Spacer(1, 0.2*inch))
                    # Check for bullet lists (marked with - or *)
                    elif para.strip().startswith('- ') or para.strip().startswith('* '):
                        bullet_items = [line.strip()[2:] for line in para.split('\n') if line.strip()]
                        content.extend(self._create_custom_bullet_list(bullet_items))
                    else:
                        # Use drop cap for the first paragraph of sections
                        if i == 0 and len(para.strip()) > 50:
                            content.append(self._create_drop_cap_paragraph(para.strip()))
                        else:
                            content.append(Paragraph(para.strip(), self.styles['BodyText']))
                        content.append(Spacer(1, 0.15*inch))

        # Enhanced image handling with better integration
        if hasattr(section, 'images') and section.images:
            for i, image_info in enumerate(section.images):
                if isinstance(image_info, dict) and 'path' in image_info:
                    try:
                        content.append(Spacer(1, 0.3*inch))

                        # Enhanced image sizing and positioning
                        img = Image(image_info['path'])
                        img.drawHeight = 2.5*inch
                        img.drawWidth = 3.5*inch
                        img.hAlign = 'CENTER'
                        content.append(img)

                        # Enhanced caption with celestial styling
                        if 'type' in image_info:
                            caption = image_info['type'].replace('_', ' ').title()
                            content.append(Paragraph(f"<i>{caption}</i>", self.styles['FlavorText']))

                        content.append(Spacer(1, 0.2*inch))

                    except Exception as e:
                        logger.warning(f"Failed to add enhanced image {image_info.get('path', 'unknown')}: {e}")

        # Enhanced subsections
        if hasattr(section, 'subsections') and section.subsections:
            for subsection in section.subsections:
                content.append(Paragraph(subsection.title, self.styles['SubsectionHeader']))
                content.append(Spacer(1, 0.1*inch))

                if subsection.content:
                    sub_paragraphs = subsection.content.split('\n\n')
                    for para in sub_paragraphs:
                        if para.strip():
                            content.append(Paragraph(para.strip(), self.styles['BodyText']))
                            content.append(Spacer(1, 0.1*inch))

                # Enhanced subsection images
                if hasattr(subsection, 'images') and subsection.images:
                    for image_info in subsection.images:
                        if isinstance(image_info, dict) and 'path' in image_info:
                            try:
                                content.append(Spacer(1, 0.15*inch))
                                img = Image(image_info['path'])
                                img.drawHeight = 2*inch
                                img.drawWidth = 2.5*inch
                                img.hAlign = 'CENTER'
                                content.append(img)
                                content.append(Spacer(1, 0.1*inch))
                            except Exception as e:
                                logger.warning(f"Failed to add enhanced subsection image: {e}")

        return content

    def _create_enhanced_campaign_overview(self, campaign: Campaign) -> List[Flowable]:
        """Create enhanced campaign overview with celestial styling"""
        content = []

        # Enhanced header
        content.append(Paragraph("Campaign Overview", self.styles['SectionHeader']))

        # Enhanced overview with callout box
        overview_data = [
            ["Theme:", campaign.theme.value.title()],
            ["Difficulty:", campaign.difficulty.value.title()],
            ["Starting Level:", str(campaign.starting_level)],
            ["Party Size:", campaign.party_size.value.title()],
            ["Duration:", campaign.expected_duration.value.replace('_', ' ').title()],
            ["Quality Score:", ".1f"]
        ]

        overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.THEME_COLORS['royal_blue']),
            ('BACKGROUND', (1, 0), (-1, -1), self.THEME_COLORS['dark_sky_start']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.THEME_COLORS['text_light']),
            ('TEXTCOLOR', (1, 0), (-1, -1), self.THEME_COLORS['text_dark']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, self.THEME_COLORS['antique_gold']),
        ]))

        content.append(overview_table)
        content.append(Spacer(1, 0.3*inch))

        # Enhanced description with flavor text
        if campaign.description:
            content.append(Paragraph("Campaign Premise", self.styles['SubsectionHeader']))
            content.append(Spacer(1, 0.1*inch))
            content.append(Paragraph(campaign.description, self.styles['FlavorText']))

        return content

    def _create_enhanced_world_section(self, world) -> List[Flowable]:
        """Create enhanced world setting section with full art page"""
        content = []

        # Full page world map if available
        world_map_path = self.output_dir.parent / "images" / "world_map.png"
        if world_map_path.exists():
            try:
                content.append(Spacer(1, 2*inch))
                img = Image(str(world_map_path))
                img.drawHeight = 6*inch
                img.drawWidth = 7*inch
                img.hAlign = 'CENTER'
                content.append(img)
                content.append(Spacer(1, inch))

                # World map caption
                content.append(Paragraph("<i>Celestial Map of the Campaign World</i>", self.styles['FlavorText']))
                content.append(Spacer(1, 0.5*inch))
            except Exception as e:
                logger.warning(f"Could not add world map: {e}")

        # Enhanced world information
        content.append(Paragraph("World Setting", self.styles['SectionHeader']))

        if world.name:
            content.append(Paragraph(world.name, self.styles['SubsectionHeader']))

        if world.description:
            content.append(Paragraph(world.description, self.styles['BodyText']))

        # Enhanced geography section
        if hasattr(world, 'geography') and world.geography:
            content.append(Paragraph("Geography", self.styles['SubsectionHeader']))
            geo_info = world.geography
            if isinstance(geo_info, dict):
                for key, value in geo_info.items():
                    content.append(Paragraph(f"<b>{key.title()}:</b> {value}", self.styles['BodyText']))

        # Enhanced cultures section
        if hasattr(world, 'cultures') and world.cultures:
            content.append(Paragraph("Cultures", self.styles['SubsectionHeader']))
            for culture in world.cultures:
                if isinstance(culture, dict):
                    culture_name = culture.get('name', 'Unknown Culture')
                    culture_desc = culture.get('description', '')
                    content.append(Paragraph(f"<b>{culture_name}:</b> {culture_desc}", self.styles['BodyText']))

        # Enhanced magic system section
        if hasattr(world, 'magic_system') and world.magic_system:
            content.append(Paragraph("Magic System", self.styles['SubsectionHeader']))
            magic_info = world.magic_system
            if isinstance(magic_info, dict):
                for key, value in magic_info.items():
                    content.append(Paragraph(f"<b>{key.title()}:</b> {value}", self.styles['BodyText']))

        return content

    def _create_enhanced_story_elements(self, campaign: Campaign) -> List[Flowable]:
        """Create enhanced story elements section"""
        content = []

        content.append(Paragraph("Story Elements", self.styles['SectionHeader']))

        # Enhanced story hook with callout
        if campaign.story_hook:
            content.append(Paragraph("The Hook", self.styles['SubsectionHeader']))
            hook = campaign.story_hook

            if hook.title:
                content.append(Paragraph(hook.title, self.styles['NPCName']))

            if hook.description:
                content.append(Paragraph(hook.description, self.styles['BodyText']))

            # Enhanced stakes as callout box
            if hook.stakes:
                content.append(Spacer(1, 0.1*inch))
                content.append(Paragraph(f"**STAKES: {hook.stakes}**", self.styles['CalloutText']))

        # Enhanced story arcs
        if campaign.story_arcs:
            content.append(Paragraph("Story Arcs", self.styles['SubsectionHeader']))

            for arc in campaign.story_arcs:
                content.append(Paragraph(arc.title, self.styles['NPCName']))

                if arc.description:
                    content.append(Paragraph(arc.description, self.styles['BodyText']))

                # Enhanced climax and resolution with better formatting
                if arc.climax:
                    content.append(Paragraph(f"<b>Climax:</b> {arc.climax}", self.styles['BodyText']))

                if arc.resolution:
                    content.append(Paragraph(f"<b>Resolution:</b> {arc.resolution}", self.styles['BodyText']))

                content.append(Spacer(1, 0.2*inch))

        return content

    def _create_enhanced_npcs_section(self, npcs) -> List[Flowable]:
        """Create enhanced NPCs section with portraits and celestial styling"""
        content = []

        # Enhanced section header
        content.append(Paragraph("Key Characters", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.1*inch))
        content.append(self._create_decorative_section_divider())
        content.append(Spacer(1, 0.3*inch))

        for i, npc in enumerate(npcs):
            # Enhanced NPC header with celestial styling
            npc_header = f"{npc.name} - {npc.race.title()} {npc.character_class.title()}"
            content.append(Paragraph(npc_header, self.styles['NPCName']))

            # Try to add NPC portrait
            npc_portrait_path = self.output_dir.parent / "images" / f"npc_{i+1}_{npc.name.replace(' ', '_')}.png"
            if not npc_portrait_path.exists():
                # Try generic NPC portrait
                npc_portrait_path = self.output_dir.parent / "images" / f"npc_{i+1}.png"

            if npc_portrait_path.exists():
                try:
                    content.append(Spacer(1, 0.2*inch))
                    img = Image(str(npc_portrait_path))
                    img.drawHeight = 2.5*inch
                    img.drawWidth = 2.5*inch
                    img.hAlign = 'CENTER'
                    content.append(img)

                    # Add portrait caption
                    portrait_caption = f"Portrait of {npc.name}"
                    content.append(Paragraph(f"<i>{portrait_caption}</i>", self.styles['FlavorText']))
                    content.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    logger.warning(f"Could not add NPC portrait for {npc.name}: {e}")

            # Enhanced NPC information with custom styling
            npc_info = []
            if npc.background:
                npc_info.append(["Background:", npc.background.title()])
            if hasattr(npc, 'personality') and npc.personality:
                for trait_type, traits in npc.personality.items():
                    if isinstance(traits, list):
                        npc_info.append([f"{trait_type.title()}:", ', '.join(traits)])
                    else:
                        npc_info.append([f"{trait_type.title()}:", traits])
            if npc.motivation:
                npc_info.append(["Motivation:", npc.motivation])
            if npc.role_in_story:
                npc_info.append(["Role:", npc.role_in_story])

            if npc_info:
                npc_table = Table(npc_info, colWidths=[1.8*inch, 4*inch])
                npc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), self.THEME_COLORS['royal_blue']),
                    ('BACKGROUND', (1, 0), (-1, -1), self.THEME_COLORS['deep_blue']),
                    ('TEXTCOLOR', (0, 0), (0, -1), self.THEME_COLORS['text_gold']),
                    ('TEXTCOLOR', (1, 0), (-1, -1), self.THEME_COLORS['text_silver']),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Bookmania'),
                    ('FONTNAME', (1, 0), (-1, -1), 'Times-Roman'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('BOX', (0, 0), (-1, -1), 1, self.THEME_COLORS['border_gold']),
                    ('INNERGRID', (0, 0), (-1, -1), 1, self.THEME_COLORS['border_silver']),
                ]))
                content.append(npc_table)

            content.append(Spacer(1, 0.4*inch))

        return content

    def _create_enhanced_locations_section(self, locations) -> List[Flowable]:
        """Create enhanced locations section with illustrations and celestial styling"""
        content = []

        # Enhanced section header
        content.append(Paragraph("Important Locations", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.1*inch))
        content.append(self._create_decorative_section_divider())
        content.append(Spacer(1, 0.3*inch))

        for i, location in enumerate(locations):
            # Enhanced location header with celestial styling
            loc_header = f"{location.name} ({location.type.title()})"
            content.append(Paragraph(loc_header, self.styles['NPCName']))

            # Try to add location illustration
            location_image_path = self.output_dir.parent / "images" / f"location_{i+1}_{location.name.replace(' ', '_')}.png"
            if not location_image_path.exists():
                # Try generic location image
                location_image_path = self.output_dir.parent / "images" / f"location_{i+1}.png"

            if location_image_path.exists():
                try:
                    content.append(Spacer(1, 0.2*inch))
                    img = Image(str(location_image_path))
                    img.drawHeight = 3*inch
                    img.drawWidth = 4*inch
                    img.hAlign = 'CENTER'
                    content.append(img)

                    # Add illustration caption
                    illustration_caption = f"Illustration of {location.name}"
                    content.append(Paragraph(f"<i>{illustration_caption}</i>", self.styles['FlavorText']))
                    content.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    logger.warning(f"Could not add location image for {location.name}: {e}")

            # Enhanced description with drop cap
            if location.description:
                if len(location.description) > 50:
                    content.append(self._create_drop_cap_paragraph(location.description))
                else:
                    content.append(Paragraph(location.description, self.styles['BodyText']))
                content.append(Spacer(1, 0.2*inch))

            # Enhanced significance as callout box
            if location.significance:
                significance_callout = self._create_callout_box(
                    location.significance,
                    "Location Significance"
                )
                content.append(significance_callout)
                content.append(Spacer(1, 0.2*inch))

            # Enhanced encounters with custom bullets
            if hasattr(location, 'encounters') and location.encounters:
                content.append(Paragraph("Notable Encounters", self.styles['SubsectionHeader']))
                content.append(Spacer(1, 0.1*inch))

                encounter_items = []
                for encounter in location.encounters:
                    if isinstance(encounter, dict):
                        encounter_desc = encounter.get('description', 'Unknown encounter')
                        encounter_type = encounter.get('type', 'unknown')
                        encounter_items.append(f"<b>{encounter_type.title()}:</b> {encounter_desc}")

                if encounter_items:
                    content.extend(self._create_custom_bullet_list(encounter_items))
                    content.append(Spacer(1, 0.2*inch))

            content.append(Spacer(1, 0.4*inch))

        return content

    def _create_enhanced_appendices(self, campaign: Campaign, mode: str = "production") -> List[Flowable]:
        """Create enhanced appendices section with celestial styling"""
        content = []

        content.append(Paragraph("Appendices", self.styles['SectionHeader']))

        # Enhanced campaign statistics (simplified in test mode)
        if mode == "test":
            content.append(Paragraph("Test Campaign Summary", self.styles['SubsectionHeader']))
            summary_text = f"""
            This is a test campaign generation with {len(campaign.sections) if campaign.sections else 0} sections.
            Mode: Test (Quick validation)
            Images: {campaign.get_total_image_count() if campaign.sections else 0} generated
            """
            content.append(Paragraph(summary_text, self.styles['BodyText']))
        else:
            content.append(Paragraph("Campaign Statistics", self.styles['SubsectionHeader']))

            # Enhanced stats with celestial theming
            stats_data = [
                ["Total NPCs:", str(len(campaign.key_npcs))],
                ["Total Locations:", str(len(campaign.key_locations))],
                ["Story Arcs:", str(len(campaign.story_arcs))],
                ["Campaign Sections:", str(len(campaign.sections)) if campaign.sections else "0"],
                ["Total Content Length:", f"{campaign.get_total_content_length()} chars" if campaign.sections else "N/A"],
                ["Total Images:", str(campaign.get_total_image_count()) if campaign.sections else "0"],
                ["Difficulty Modifier:", ".2f"],
                ["Quality Score:", ".1f"]
            ]

            stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.THEME_COLORS['royal_blue']),
                ('BACKGROUND', (1, 0), (-1, -1), self.THEME_COLORS['dark_sky_start']),
                ('TEXTCOLOR', (0, 0), (0, -1), self.THEME_COLORS['text_light']),
                ('TEXTCOLOR', (1, 0), (-1, -1), self.THEME_COLORS['text_dark']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
                ('FONTNAME', (1, 0), (-1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 2, self.THEME_COLORS['antique_gold']),
                ('INNERGRID', (0, 0), (-1, -1), 1, self.THEME_COLORS['bright_purple']),
            ]))

            content.append(stats_table)

        # Production mode: Include detailed appendices content
        if mode == "production":
            # Player preferences with enhanced styling
            if campaign.player_preferences and campaign.player_preferences.has_preferences():
                content.append(Spacer(1, 0.3*inch))
                content.append(Paragraph("Player Preferences Used", self.styles['SubsectionHeader']))

                prefs_summary = campaign.player_preferences.get_preference_summary()
                for key, value in prefs_summary.items():
                    content.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['BodyText']))

            # Enhanced generation info with callout box
            content.append(Spacer(1, 0.3*inch))
            content.append(Paragraph("Generation Information", self.styles['SubsectionHeader']))

            gen_info = f"""
            **This celestial campaign was generated on {campaign.generated_at.strftime('%B %d, %Y at %I:%M %p')}.
            Quality Score: {campaign.quality_score.value}/5.0**

            """

            if campaign.sections:
                gen_info += f"Content Sections: {len(campaign.sections)}\n"
                gen_info += f"Total Content: {campaign.get_total_content_length()} characters\n"
                gen_info += f"Images Generated: {campaign.get_total_image_count()}"

            content.append(Paragraph(gen_info, self.styles['BodyText']))

            # Add celestial blessing as flavor text
            content.append(Spacer(1, 0.2*inch))
            blessing = """
            *May the stars guide your adventurers through this celestial realm,
            and may your campaign shine brightly in the annals of D&D history.*
            """
            content.append(Paragraph(blessing, self.styles['FlavorText']))

        return content
