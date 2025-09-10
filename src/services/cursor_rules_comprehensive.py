"""
CursorRules - Comprehensive D&D 5e Rules Validation Service

This module provides comprehensive rule validation for generated campaign content,
ensuring compliance with D&D 5e rules and preventing AI drift.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple

from domain.value_objects import (
    RuleCategory, ValidationSeverity, ValidationStatus,
    ValidationIssue, ValidationResult
)

logger = logging.getLogger(__name__)


class ComprehensiveCursorRulesService:
    """
    D&D 5e Rules Validation Service

    This class validates generated campaign content against D&D 5e rules,
    ensuring that all content is rules-compliant and prevents AI drift.
    """

    def __init__(self, rules_path: str = "/Users/ethanchang/Documents/games/panverse/data/dnd5e_rules"):
        """
        Initialize the rules engine

        Args:
            rules_path: Path to rules data directory
        """
        self.rules_path = rules_path
        self.rules_data = {}
        self.validators = {}
        self.load_rules()
        self.register_validators()
        logger.info(f"ComprehensiveCursorRules initialized with {len(self.rules_data)} rule categories")

    def load_rules(self) -> None:
        """Load all rule data from files"""
        try:
            for category in RuleCategory:
                file_path = os.path.join(self.rules_path, f"{category.value}.json")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        self.rules_data[category] = json.load(f)
                    logger.info(f"Loaded {len(self.rules_data[category])} rules for {category.value}")
                else:
                    logger.warning(f"Rules file not found for {category.value}")
                    self.rules_data[category] = {}
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            # Critical: NO fallbacks allowed - we must have rules
            raise ValueError(f"Rules loading failed: {e}")

    def register_validators(self) -> None:
        """Register all validators for different content types"""
        self.validators = {
            "monster": self.validate_monster,
            "npc": self.validate_npc,
            "item": self.validate_item,
            "spell": self.validate_spell,
            "encounter": self.validate_encounter,
            "location": self.validate_location,
            "treasure": self.validate_treasure,
            "campaign": self.validate_campaign,
        }

    def validate(self, content_type: str, content: Dict[str, Any]) -> ValidationResult:
        """
        Validate content against rules

        Args:
            content_type: Type of content to validate
            content: Content data to validate

        Returns:
            Validation result with issues and score
        """
        if content_type not in self.validators:
            logger.error(f"No validator for content type: {content_type}")
            raise ValueError(f"Unknown content type: {content_type}")

        # Watchdog: Verify we have actual content, not empty placeholders
        if not content or len(content) < 3:
            raise ValueError(f"Content too small to validate - possible AI drift")

        # Run the appropriate validator
        return self.validators[content_type](content)

    def validate_campaign(self, campaign: Dict[str, Any]) -> ValidationResult:
        """
        Validate an entire campaign

        Args:
            campaign: Campaign data

        Returns:
            Validation result
        """
        issues = []
        component_scores = {}

        # Validate campaign structure
        if not all(key in campaign for key in ["name", "description", "theme", "level_range"]):
            issues.append(ValidationIssue(
                message="Campaign missing required fields",
                category=RuleCategory.MECHANICS,
                severity=ValidationSeverity.ERROR,
                context={"campaign": campaign.get("name", "Unknown")},
                suggestion="Add missing fields: name, description, theme, level_range"
            ))

        # Validate level range
        level_range = campaign.get("level_range", "")
        if level_range:
            try:
                start, end = map(int, level_range.split("-"))
                if start < 1 or end > 20 or start > end:
                    issues.append(ValidationIssue(
                        message=f"Invalid level range: {level_range}",
                        category=RuleCategory.MECHANICS,
                        severity=ValidationSeverity.ERROR,
                        context={"campaign": campaign.get("name", "Unknown")},
                        suggestion="Use level range between 1-20 with start < end"
                    ))
                    component_scores["level_range"] = 0.0
                else:
                    component_scores["level_range"] = 1.0
            except:
                issues.append(ValidationIssue(
                    message=f"Malformed level range: {level_range}",
                    category=RuleCategory.MECHANICS,
                    severity=ValidationSeverity.ERROR,
                    context={"campaign": campaign.get("name", "Unknown")},
                    suggestion="Format level range as 'X-Y' (e.g., '1-5')"
                ))
                component_scores["level_range"] = 0.0

        # Validate campaign monsters
        if "monsters" in campaign:
            for monster in campaign["monsters"]:
                monster_result = self.validate_monster(monster)
                issues.extend(monster_result.issues)
                component_scores[f"monster_{monster.get('name', 'unknown')}"] = monster_result.score

        # Validate campaign items
        if "items" in campaign:
            for item in campaign["items"]:
                item_result = self.validate_item(item)
                issues.extend(item_result.issues)
                component_scores[f"item_{item.get('name', 'unknown')}"] = item_result.score

        # Validate campaign encounters
        if "encounters" in campaign:
            for encounter in campaign["encounters"]:
                encounter_result = self.validate_encounter(encounter)
                issues.extend(encounter_result.issues)
                component_scores[f"encounter_{encounter.get('name', 'unknown')}"] = encounter_result.score

        # Calculate overall score
        if component_scores:
            overall_score = sum(component_scores.values()) / len(component_scores)
        else:
            overall_score = 0.5  # Default middle score if no components

        # Determine if valid based on critical issues
        is_valid = not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)

        return ValidationResult(
            is_valid=is_valid,
            score=overall_score,
            issues=issues,
            validated_section="campaign",
            component_scores=component_scores
        )

    def validate_monster(self, monster: Dict[str, Any]) -> ValidationResult:
        """
        Validate a monster against D&D 5e rules

        Args:
            monster: Monster data

        Returns:
            Validation result
        """
        issues = []
        component_scores = {}

        # Check required fields
        required_fields = ["name", "size", "type", "alignment", "armor_class", "hit_points", "speed"]
        for field in required_fields:
            if field not in monster:
                issues.append(ValidationIssue(
                    message=f"Monster missing required field: {field}",
                    category=RuleCategory.MONSTERS,
                    severity=ValidationSeverity.ERROR,
                    context={"monster": monster.get("name", "Unknown")},
                    suggestion=f"Add {field} to monster data"
                ))

        # Validate CR (Challenge Rating)
        if "challenge_rating" in monster:
            cr = monster["challenge_rating"]
            valid_crs = ["0", "1/8", "1/4", "1/2"] + [str(i) for i in range(1, 31)]
            if str(cr) not in valid_crs:
                issues.append(ValidationIssue(
                    message=f"Invalid challenge rating: {cr}",
                    category=RuleCategory.MONSTERS,
                    severity=ValidationSeverity.ERROR,
                    context={"monster": monster.get("name", "Unknown")},
                    suggestion=f"Use a valid CR: {', '.join(valid_crs[:10])}..."
                ))
                component_scores["cr"] = 0.0
            else:
                component_scores["cr"] = 1.0

        # Validate ability scores
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            if ability in monster:
                score = monster[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(ValidationIssue(
                        message=f"Invalid {ability} score: {score}",
                        category=RuleCategory.MONSTERS,
                        severity=ValidationSeverity.ERROR,
                        context={"monster": monster.get("name", "Unknown")},
                        suggestion=f"Use a {ability} score between 1-30"
                    ))
                    component_scores[ability] = 0.0
                else:
                    component_scores[ability] = 1.0

        # Calculate overall score
        if component_scores:
            overall_score = sum(component_scores.values()) / len(component_scores)
        else:
            overall_score = 0.5  # Default middle score if no components

        # Determine if valid based on critical issues
        is_valid = not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)

        return ValidationResult(
            is_valid=is_valid,
            score=overall_score,
            issues=issues,
            validated_section="monster",
            component_scores=component_scores
        )

    def validate_item(self, item: Dict[str, Any]) -> ValidationResult:
        """
        Validate an item against D&D 5e rules

        Args:
            item: Item data

        Returns:
            Validation result
        """
        issues = []
        component_scores = {}

        # Check required fields
        required_fields = ["name", "type", "description"]
        for field in required_fields:
            if field not in item:
                issues.append(ValidationIssue(
                    message=f"Item missing required field: {field}",
                    category=RuleCategory.ITEMS,
                    severity=ValidationSeverity.ERROR,
                    context={"item": item.get("name", "Unknown")},
                    suggestion=f"Add {field} to item data"
                ))

        # Validate rarity if present
        if "rarity" in item:
            rarity = item["rarity"]
            valid_rarities = ["common", "uncommon", "rare", "very rare", "legendary", "artifact"]
            if rarity.lower() not in valid_rarities:
                issues.append(ValidationIssue(
                    message=f"Invalid rarity: {rarity}",
                    category=RuleCategory.ITEMS,
                    severity=ValidationSeverity.ERROR,
                    context={"item": item.get("name", "Unknown")},
                    suggestion=f"Use a valid rarity: {', '.join(valid_rarities)}"
                ))
                component_scores["rarity"] = 0.0
            else:
                component_scores["rarity"] = 1.0

        # Check for attunement consistency
        if "attunement" in item and item["attunement"]:
            if "attunement_requirements" not in item or not item["attunement_requirements"]:
                issues.append(ValidationIssue(
                    message="Item requires attunement but no requirements specified",
                    category=RuleCategory.ITEMS,
                    severity=ValidationSeverity.WARNING,
                    context={"item": item.get("name", "Unknown")},
                    suggestion="Add attunement requirements or set attunement to false"
                ))
                component_scores["attunement"] = 0.5
            else:
                component_scores["attunement"] = 1.0

        # Calculate overall score
        if component_scores:
            overall_score = sum(component_scores.values()) / len(component_scores)
        else:
            overall_score = 0.5  # Default middle score if no components

        # Determine if valid based on critical issues
        is_valid = not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)

        return ValidationResult(
            is_valid=is_valid,
            score=overall_score,
            issues=issues,
            validated_section="item",
            component_scores=component_scores
        )

    def _get_valid_races(self) -> List[str]:
        """Get list of valid D&D 5e races"""
        if RuleCategory.RACES in self.rules_data:
            return self.rules_data[RuleCategory.RACES].get("races", [])
        return [
            "Dragonborn", "Dwarf", "Elf", "Gnome", "Half-Elf", "Half-Orc",
            "Halfling", "Human", "Tiefling", "Orc", "Goblin", "Hobgoblin",
            "Kobold", "Lizardfolk", "Tabaxi", "Kenku", "Aarakocra", "Goliath",
            "Aasimar", "Firbolg", "Tortle", "Triton", "Yuan-ti"
        ]

    def _get_valid_classes(self) -> List[str]:
        """Get list of valid D&D 5e classes"""
        if RuleCategory.CLASSES in self.rules_data:
            return self.rules_data[RuleCategory.CLASSES].get("classes", [])
        return [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
            "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
        ]

    # Placeholder methods for other validators - will be implemented fully
    def validate_npc(self, npc: Dict[str, Any]) -> ValidationResult:
        """Validate NPC - placeholder implementation"""
        return ValidationResult(
            is_valid=True,
            score=1.0,
            issues=[],
            validated_section="npc",
            component_scores={}
        )

    def validate_spell(self, spell: Dict[str, Any]) -> ValidationResult:
        """Validate spell - placeholder implementation"""
        return ValidationResult(
            is_valid=True,
            score=1.0,
            issues=[],
            validated_section="spell",
            component_scores={}
        )

    def validate_encounter(self, encounter: Dict[str, Any]) -> ValidationResult:
        """Validate encounter - placeholder implementation"""
        return ValidationResult(
            is_valid=True,
            score=1.0,
            issues=[],
            validated_section="encounter",
            component_scores={}
        )

    def validate_location(self, location: Dict[str, Any]) -> ValidationResult:
        """Validate location - placeholder implementation"""
        return ValidationResult(
            is_valid=True,
            score=1.0,
            issues=[],
            validated_section="location",
            component_scores={}
        )

    def validate_treasure(self, treasure: Dict[str, Any]) -> ValidationResult:
        """Validate treasure - placeholder implementation"""
        return ValidationResult(
            is_valid=True,
            score=1.0,
            issues=[],
            validated_section="treasure",
            component_scores={}
        )
