"""
Content Integrity Watchdog

This module implements strict content integrity rules to prevent mock/placeholder
content in product output. It enforces that ALL generated content is genuine
AI-generated content, never placeholders or mock data.

Key responsibilities:
1. Detect and prevent mock/placeholder content patterns
2. Validate minimum content lengths for different section types
3. Ensure image generation prompts are real and descriptive
4. Provide mode-aware operation (active in production, can be disabled for testing)
5. Log detailed integrity violations for debugging
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..errors import ContentIntegrityError, ContentQualityError
from ..entities import Campaign

logger = logging.getLogger(__name__)


class ContentIntegrityWatchdog:
    """
    Enforces strict content integrity rules to prevent mock/placeholder content
    in product output.

    This watchdog implements comprehensive validation to ensure that ALL generated
    content is genuine AI-generated content, never placeholders, mock data, or
    "example" content.
    """

    def __init__(self, is_active: bool = True):
        """
        Initialize the Content Integrity Watchdog.

        Args:
            is_active: Whether the watchdog is active. Should be True in production,
                      False only for isolated testing scenarios.
        """
        self.is_active = is_active

        # Patterns that indicate mock/placeholder content
        self.forbidden_patterns = [
            "placeholder", "mock", "sample text", "lorem ipsum", "example",
            "would be", "will contain", "to be filled", "[content]", "content here",
            "would go here", "to be generated", "will be filled", "example content",
            "template", "dummy", "fake", "coming soon", "tbd", "todo",
            "to be determined", "sample data", "test content", "demo",
            "illustration of", "example of", "placeholder text",
            "insert content", "replace with", "fill in", "add here",
            "content goes here", "your content", "sample campaign",
            "generic", "standard template", "boilerplate"
        ]

        # Minimum content lengths for different section types (characters)
        self.min_section_lengths = {
            "description": 100,
            "introduction": 200,
            "setting": 300,
            "background": 300,
            "structure": 200,
            "location": 200,
            "npc": 150,
            "encounter": 200,
            "plot": 300,
            "treasure": 150,
            "appendix": 100,
            "campaign_concept": 150,
            "story_arc": 100,
            "default": 100
        }

        # Image prompt validation patterns
        self.forbidden_image_patterns = [
            "placeholder", "mock", "example", "sample", "test", "dummy",
            "generic", "template", "illustration of", "example of",
            "coming soon", "to be generated", "placeholder image"
        ]

        logger.info(f"ContentIntegrityWatchdog initialized (active: {is_active})")

    def validate_text_content(self, section_name: str, content: str) -> bool:
        """
        Validate that content is real and not placeholder text.

        Args:
            section_name: Name of the section being validated
            content: The text content to validate

        Returns:
            True if content passes validation

        Raises:
            ContentIntegrityError: If content appears to be placeholder/mock
        """
        if not self.is_active:
            return True

        if not content or not isinstance(content, str):
            raise ContentIntegrityError(
                f"CRITICAL: Empty or invalid content for section '{section_name}'. "
                f"ALL content must be real AI-generated text."
            )

        # Check for forbidden patterns
        content_lower = content.lower()
        for pattern in self.forbidden_patterns:
            if pattern.lower() in content_lower:
                raise ContentIntegrityError(
                    f"CRITICAL: Found forbidden pattern '{pattern}' indicating mock content "
                    f"in section '{section_name}'. ALL output must be real content."
                )

        # Check minimum content length
        min_length = self.min_section_lengths.get(
            section_name.lower(), self.min_section_lengths["default"]
        )

        if len(content.strip()) < min_length:
            raise ContentIntegrityError(
                f"CRITICAL: Content for '{section_name}' is suspiciously short "
                f"({len(content)} chars). Minimum expected: {min_length} chars. "
                f"This suggests incomplete or mock content."
            )

        # Additional validation: ensure content has some variety
        if len(set(content.lower().split())) < 5:
            raise ContentIntegrityError(
                f"CRITICAL: Content for '{section_name}' lacks sufficient variety. "
                f"This suggests template or boilerplate content."
            )

        logger.debug(f"Content validation passed for section '{section_name}' ({len(content)} chars)")
        return True

    def validate_image_prompt(self, image_prompt: str) -> bool:
        """
        Validate that image generation prompts will create real images.

        Args:
            image_prompt: The prompt for image generation

        Returns:
            True if prompt passes validation

        Raises:
            ContentIntegrityError: If prompt appears to generate placeholder images
        """
        if not self.is_active:
            return True

        if not image_prompt or not isinstance(image_prompt, str):
            raise ContentIntegrityError(
                f"CRITICAL: Empty or invalid image prompt. "
                f"ALL image prompts must be real and descriptive."
            )

        # Check for forbidden patterns
        prompt_lower = image_prompt.lower()
        for pattern in self.forbidden_image_patterns:
            if pattern.lower() in prompt_lower:
                raise ContentIntegrityError(
                    f"CRITICAL: Image prompt contains forbidden pattern '{pattern}' "
                    f"suggesting mock/placeholder image generation."
                )

        # Ensure prompt is descriptive enough
        if len(image_prompt.strip()) < 20:
            raise ContentIntegrityError(
                f"CRITICAL: Image prompt is too short ({len(image_prompt)} chars). "
                f"Image prompts must be descriptive and specific."
            )

        # Ensure prompt doesn't look like a template
        if any(char in image_prompt for char in ["[", "]", "{", "}", "<", ">"]):
            raise ContentIntegrityError(
                f"CRITICAL: Image prompt contains template markers. "
                f"Image prompts must be complete and real."
            )

        logger.debug(f"Image prompt validation passed ({len(image_prompt)} chars)")
        return True

    def validate_entire_campaign(self, campaign: Campaign) -> bool:
        """
        Validate an entire campaign for content integrity.

        Args:
            campaign: Campaign object to validate

        Returns:
            True if campaign passes validation

        Raises:
            ContentIntegrityError: If any part of the campaign appears to be mock
        """
        if not self.is_active:
            return True

        logger.info(f"Validating entire campaign '{campaign.name}' for content integrity")

        try:
            # Validate campaign title and description
            self.validate_text_content("campaign_title", campaign.name)
            self.validate_text_content("campaign_description", campaign.description)

            # Validate each section
            if campaign.sections:
                for section in campaign.sections:
                    self.validate_text_content(section.section_id, section.content)

                    # Validate any image prompts in the section
                    if section.images:
                        for image in section.images:
                            if isinstance(image, dict) and "prompt" in image:
                                self.validate_image_prompt(image["prompt"])

            # Validate player preferences if available
            if campaign.player_preferences and campaign.player_preferences.freeform_input:
                self.validate_text_content("player_input", campaign.player_preferences.freeform_input)

            logger.info(f"Campaign '{campaign.name}' passed complete content integrity validation")
            return True

        except ContentIntegrityError as e:
            logger.error(f"Campaign '{campaign.name}' failed content integrity validation: {e.message}")
            raise

    def validate_campaign_concept(self, concept: Dict[str, Any]) -> bool:
        """
        Validate a campaign concept for content integrity.

        Args:
            concept: Campaign concept dictionary

        Returns:
            True if concept passes validation

        Raises:
            ContentIntegrityError: If concept contains mock content
        """
        if not self.is_active:
            return True

        if not concept or not isinstance(concept, dict):
            raise ContentIntegrityError("CRITICAL: Invalid campaign concept format")

        required_fields = ["title", "description", "level_range"]
        for field in required_fields:
            if field not in concept:
                raise ContentIntegrityError(f"CRITICAL: Campaign concept missing required field '{field}'")

        # Validate each field
        self.validate_text_content("concept_title", concept["title"])
        self.validate_text_content("concept_description", concept["description"])

        if "subtitle" in concept:
            self.validate_text_content("concept_subtitle", concept["subtitle"])

        logger.debug("Campaign concept passed content integrity validation")
        return True

    def set_active(self, active: bool) -> None:
        """
        Set the active state of the watchdog.

        Args:
            active: Whether the watchdog should be active
        """
        self.is_active = active
        logger.info(f"ContentIntegrityWatchdog active state set to: {active}")

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation configuration.

        Returns:
            Dictionary with validation summary
        """
        return {
            "is_active": self.is_active,
            "forbidden_patterns_count": len(self.forbidden_patterns),
            "section_types_count": len(self.min_section_lengths),
            "forbidden_image_patterns_count": len(self.forbidden_image_patterns),
            "total_validation_rules": (
                len(self.forbidden_patterns) +
                len(self.min_section_lengths) +
                len(self.forbidden_image_patterns)
            )
        }

    def validate_batch_content(self, content_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of content items.

        Args:
            content_batch: List of content items to validate

        Returns:
            Dictionary with validation results
        """
        if not self.is_active:
            return {"passed": len(content_batch), "failed": 0, "details": []}

        results = {"passed": 0, "failed": 0, "details": []}

        for i, item in enumerate(content_batch):
            try:
                content_type = item.get("type", "unknown")
                content = item.get("content", "")

                if content_type == "image_prompt":
                    self.validate_image_prompt(content)
                else:
                    self.validate_text_content(content_type, content)

                results["passed"] += 1
                results["details"].append({
                    "index": i,
                    "type": content_type,
                    "status": "passed",
                    "length": len(content) if isinstance(content, str) else 0
                })

            except ContentIntegrityError as e:
                results["failed"] += 1
                results["details"].append({
                    "index": i,
                    "type": item.get("type", "unknown"),
                    "status": "failed",
                    "error": str(e),
                    "length": len(item.get("content", "")) if isinstance(item.get("content"), str) else 0
                })

        return results
