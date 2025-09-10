"""
Unit Tests for ContentIntegrityWatchdog

Tests the ContentIntegrityWatchdog functionality to ensure it properly
validates content integrity and prevents mock/placeholder content.
"""

import pytest
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog
from domain.errors import ContentIntegrityError


class TestContentIntegrityWatchdog:
    """Test suite for ContentIntegrityWatchdog"""

    def setup_method(self):
        """Set up test fixtures"""
        self.watchdog = ContentIntegrityWatchdog(is_active=True)
        self.inactive_watchdog = ContentIntegrityWatchdog(is_active=False)

    def test_initialization(self):
        """Test ContentIntegrityWatchdog initialization"""
        assert self.watchdog.is_active is True
        assert len(self.watchdog.forbidden_patterns) > 0
        assert len(self.watchdog.min_section_lengths) > 0
        assert len(self.watchdog.forbidden_image_patterns) > 0

    def test_initialization_inactive(self):
        """Test ContentIntegrityWatchdog initialization with inactive mode"""
        assert self.inactive_watchdog.is_active is False

    def test_set_active(self):
        """Test setting active state"""
        self.watchdog.set_active(False)
        assert self.watchdog.is_active is False

        self.watchdog.set_active(True)
        assert self.watchdog.is_active is True

    def test_validate_text_content_valid(self):
        """Test validating valid text content"""
        valid_content = "This is a comprehensive description of a D&D campaign with detailed world-building elements, rich character development opportunities, and immersive storytelling that will engage players for many sessions of adventure."

        # Should not raise exception
        result = self.watchdog.validate_text_content("description", valid_content)
        assert result is True

    def test_validate_text_content_inactive_watchdog(self):
        """Test that inactive watchdog always returns True"""
        invalid_content = "This is placeholder content"

        # Should not raise exception when inactive
        result = self.inactive_watchdog.validate_text_content("description", invalid_content)
        assert result is True

    def test_validate_text_content_forbidden_patterns(self):
        """Test detection of forbidden patterns"""
        forbidden_contents = [
            "This is placeholder content",
            "Please add content here",
            "This is a sample text",
            "TODO: Add real content",
            "This is lorem ipsum text",
            "Content goes here",
            "Example campaign description",
            "Mock data for testing",
        ]

        for content in forbidden_contents:
            with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
                self.watchdog.validate_text_content("description", content)

    def test_validate_text_content_too_short(self):
        """Test detection of content that's too short"""
        short_content = "Hi"

        with pytest.raises(ContentIntegrityError, match="too short"):
            self.watchdog.validate_text_content("description", short_content)

    def test_validate_text_content_minimum_lengths(self):
        """Test minimum length validation for different section types"""
        # Test different section types with their minimum lengths
        test_cases = [
            ("description", 50),  # Should be at least 100, but testing with 50
            ("introduction", 150),  # Should be at least 200, but testing with 150
            ("npc", 100),  # Should be at least 150, but testing with 100
        ]

        for section_type, length in test_cases:
            short_content = "x" * length
            with pytest.raises(ContentIntegrityError, match="too short"):
                self.watchdog.validate_text_content(section_type, short_content)

    def test_validate_text_content_edge_cases(self):
        """Test edge cases for text content validation"""
        # Empty content
        with pytest.raises(ContentIntegrityError):
            self.watchdog.validate_text_content("description", "")

        # None content
        with pytest.raises(ContentIntegrityError):
            self.watchdog.validate_text_content("description", None)

        # Whitespace only
        with pytest.raises(ContentIntegrityError):
            self.watchdog.validate_text_content("description", "   \n\t   ")

    def test_validate_image_prompt_valid(self):
        """Test validating valid image prompt"""
        valid_prompt = "A dramatic fantasy castle on a mountain top with knights and dragons, detailed digital art"

        result = self.watchdog.validate_image_prompt(valid_prompt)
        assert result is True

    def test_validate_image_prompt_inactive_watchdog(self):
        """Test that inactive watchdog always returns True for image prompts"""
        invalid_prompt = "placeholder image"

        result = self.inactive_watchdog.validate_image_prompt(invalid_prompt)
        assert result is True

    def test_validate_image_prompt_forbidden_patterns(self):
        """Test detection of forbidden patterns in image prompts"""
        forbidden_prompts = [
            "placeholder image",
            "sample picture",
            "example illustration",
            "mock artwork",
            "test image",
            "generic fantasy scene",
        ]

        for prompt in forbidden_prompts:
            with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
                self.watchdog.validate_image_prompt(prompt)

    def test_validate_image_prompt_too_short(self):
        """Test detection of image prompts that are too short"""
        short_prompt = "Hi"

        with pytest.raises(ContentIntegrityError, match="too short"):
            self.watchdog.validate_image_prompt(short_prompt)

    def test_validate_image_prompt_template_markers(self):
        """Test detection of template markers in image prompts"""
        template_prompts = [
            "[scene description]",
            "{image prompt}",
            "<placeholder>",
            "Image of [subject]",
        ]

        for prompt in template_prompts:
            with pytest.raises(ContentIntegrityError, match="template markers"):
                self.watchdog.validate_image_prompt(prompt)

    def test_validate_campaign_concept_valid(self):
        """Test validating a valid campaign concept"""
        valid_concept = {
            "title": "The Shadowed Realms",
            "subtitle": "A Journey Through Darkness",
            "description": "This is a comprehensive description of a D&D campaign that explores themes of shadow and light in a richly detailed fantasy world.",
            "level_range": "1-5"
        }

        result = self.watchdog.validate_campaign_concept(valid_concept)
        assert result is True

    def test_validate_campaign_concept_missing_fields(self):
        """Test validation of campaign concept with missing fields"""
        incomplete_concept = {
            "title": "Test Campaign",
            # Missing required fields
        }

        with pytest.raises(ContentIntegrityError, match="missing required field"):
            self.watchdog.validate_campaign_concept(incomplete_concept)

    def test_validate_campaign_concept_forbidden_content(self):
        """Test validation of campaign concept with forbidden content"""
        invalid_concept = {
            "title": "Test Campaign",
            "subtitle": "placeholder subtitle",
            "description": "This is sample text for the campaign",
            "level_range": "1-5"
        }

        with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
            self.watchdog.validate_campaign_concept(invalid_concept)

    def test_validate_entire_campaign_valid(self):
        """Test validating a complete valid campaign"""
        # Create a mock campaign with valid content
        campaign = Mock(spec=Campaign)
        campaign.name = "Test Campaign"
        campaign.description = "This is a comprehensive description of a D&D campaign with detailed world-building."

        # Mock sections
        section1 = Mock(spec=CampaignSection)
        section1.section_id = "introduction"
        section1.content = "This is a detailed introduction to the campaign with proper content."
        section1.images = []

        section2 = Mock(spec=CampaignSection)
        section2.section_id = "setting"
        section2.content = "This is a detailed setting description with world-building elements."
        section2.images = [{"prompt": "A detailed fantasy landscape with mountains and forests"}]

        campaign.sections = [section1, section2]
        campaign.player_preferences = None

        result = self.watchdog.validate_entire_campaign(campaign)
        assert result is True

    def test_validate_entire_campaign_invalid_title(self):
        """Test validation of campaign with invalid title"""
        campaign = Mock(spec=Campaign)
        campaign.name = "placeholder campaign"  # Forbidden pattern
        campaign.description = "Valid description"
        campaign.sections = []
        campaign.player_preferences = None

        with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
            self.watchdog.validate_entire_campaign(campaign)

    def test_validate_entire_campaign_invalid_section(self):
        """Test validation of campaign with invalid section content"""
        campaign = Mock(spec=Campaign)
        campaign.name = "Test Campaign"
        campaign.description = "Valid description"

        section = Mock(spec=CampaignSection)
        section.section_id = "introduction"
        section.content = "sample text"  # Forbidden pattern
        section.images = []

        campaign.sections = [section]
        campaign.player_preferences = None

        with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
            self.watchdog.validate_entire_campaign(campaign)

    def test_validate_entire_campaign_invalid_image_prompt(self):
        """Test validation of campaign with invalid image prompt"""
        campaign = Mock(spec=Campaign)
        campaign.name = "Test Campaign"
        campaign.description = "Valid description"

        section = Mock(spec=CampaignSection)
        section.section_id = "introduction"
        section.content = "Valid content"
        section.images = [{"prompt": "placeholder image"}]  # Forbidden pattern

        campaign.sections = [section]
        campaign.player_preferences = None

        with pytest.raises(ContentIntegrityError, match="forbidden pattern"):
            self.watchdog.validate_entire_campaign(campaign)

    def test_validate_batch_content(self):
        """Test batch content validation"""
        batch = [
            {"type": "description", "content": "Valid description content"},
            {"type": "npc", "content": "sample npc"},  # Invalid
            {"type": "image_prompt", "content": "placeholder image"},  # Invalid
        ]

        result = self.watchdog.validate_batch_content(batch)

        assert result["passed"] == 1
        assert result["failed"] == 2
        assert len(result["details"]) == 3

        # Check details structure
        assert result["details"][0]["status"] == "passed"
        assert result["details"][1]["status"] == "failed"
        assert result["details"][2]["status"] == "failed"

    def test_validate_batch_content_inactive(self):
        """Test batch content validation with inactive watchdog"""
        batch = [
            {"type": "description", "content": "Valid description"},
            {"type": "npc", "content": "sample npc"},  # Would be invalid if active
        ]

        result = self.inactive_watchdog.validate_batch_content(batch)

        assert result["passed"] == 2
        assert result["failed"] == 0

    def test_get_validation_summary(self):
        """Test getting validation summary"""
        summary = self.watchdog.get_validation_summary()

        assert "is_active" in summary
        assert "forbidden_patterns_count" in summary
        assert "section_types_count" in summary
        assert "forbidden_image_patterns_count" in summary
        assert "total_validation_rules" in summary

        assert summary["is_active"] is True
        assert summary["forbidden_patterns_count"] > 0
        assert summary["section_types_count"] > 0
        assert summary["forbidden_image_patterns_count"] > 0
        assert summary["total_validation_rules"] > 0

    def test_content_variety_validation(self):
        """Test that content with insufficient variety is rejected"""
        repetitive_content = "The the the the the the the the the the the the the the the"

        with pytest.raises(ContentIntegrityError, match="lacks sufficient variety"):
            self.watchdog.validate_text_content("description", repetitive_content)


if __name__ == "__main__":
    pytest.main([__file__])
