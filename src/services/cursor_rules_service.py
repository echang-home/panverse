"""
CursorRules Service for D&D 5e validation and compliance checking

This module provides comprehensive rule validation for generated campaign content,
ensuring compliance with D&D 5e rules and preventing AI drift.
"""
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

from domain.value_objects import (
    RuleCategory, ValidationSeverity, ValidationStatus,
    ValidationIssue, ValidationResult
)

logger = logging.getLogger(__name__)


class CursorRulesService:
    """Service for validating D&D 5e rules compliance"""

    # Valid D&D 5e races, classes, backgrounds, etc.
    VALID_RACES = {
        'human', 'elf', 'dwarf', 'halfling', 'dragonborn',
        'tiefling', 'half-elf', 'half-orc', 'gnome'
    }

    VALID_CLASSES = {
        'barbarian', 'bard', 'cleric', 'druid', 'fighter',
        'monk', 'paladin', 'ranger', 'rogue', 'sorcerer',
        'warlock', 'wizard'
    }

    VALID_BACKGROUNDS = {
        'acolyte', 'criminal', 'entertainer', 'folk_hero',
        'guild_artisan', 'hermit', 'noble', 'outlander',
        'sage', 'sailor', 'soldier', 'urchin'
    }

    VALID_SKILLS = {
        'acrobatics', 'animal_handling', 'arcana', 'athletics',
        'deception', 'history', 'insight', 'intimidation',
        'investigation', 'medicine', 'nature', 'perception',
        'performance', 'persuasion', 'religion', 'sleight_of_hand',
        'stealth', 'survival'
    }

    VALID_LANGUAGES = {
        'common', 'dwarvish', 'elvish', 'giant', 'gnomish',
        'goblin', 'halfling', 'orc', 'abyssal', 'celestial',
        'draconic', 'deep_speech', 'infernal', 'primordial',
        'sylvan', 'undercommon'
    }

    # Challenge rating to XP conversion
    CR_TO_XP = {
        0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450,
        3: 700, 4: 1100, 5: 1800, 6: 2300, 7: 2900, 8: 3900,
        9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000,
        14: 11500, 15: 13000, 16: 15000, 17: 18000, 18: 20000,
        19: 22000, 20: 25000, 21: 33000, 22: 41000, 23: 50000,
        24: 62000, 30: 155000
    }

    def __init__(self):
        self.violations = []

    def validate_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire campaign for D&D 5e compliance"""
        self.violations = []

        # Validate basic campaign structure
        self._validate_campaign_structure(campaign_data)

        # Validate starting level
        if "starting_level" in campaign_data:
            self._validate_level(campaign_data["starting_level"])

        # Validate NPCs
        if "npcs" in campaign_data:
            for npc in campaign_data["npcs"]:
                self._validate_npc(npc)

        # Validate locations and encounters
        if "locations" in campaign_data:
            for location in campaign_data["locations"]:
                self._validate_location(location)

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score()

        return {
            "is_compliant": len(self.violations) == 0,
            "compliance_score": compliance_score,
            "violations": self.violations,
            "recommendations": self._generate_recommendations()
        }

    def _validate_campaign_structure(self, campaign_data: Dict[str, Any]):
        """Validate basic campaign structure"""
        required_fields = ["name", "description", "theme", "difficulty", "party_size"]

        for field in required_fields:
            if field not in campaign_data:
                self.violations.append({
                    "type": "missing_field",
                    "severity": "high",
                    "field": field,
                    "message": f"Required field '{field}' is missing from campaign"
                })

        # Check for minimum content
        if "description" in campaign_data and len(campaign_data["description"]) < 50:
            self.violations.append({
                "type": "insufficient_content",
                "severity": "medium",
                "field": "description",
                "message": "Campaign description is too short (minimum 50 characters)"
            })

    def _validate_level(self, level: int):
        """Validate character level"""
        if not isinstance(level, int) or not (1 <= level <= 20):
            self.violations.append({
                "type": "invalid_level",
                "severity": "high",
                "field": "starting_level",
                "message": f"Starting level {level} is invalid. Must be between 1 and 20."
            })

    def _validate_npc(self, npc: Dict[str, Any]):
        """Validate NPC data"""
        # Validate race
        if "race" in npc:
            race = npc["race"].lower()
            if race not in self.VALID_RACES:
                self.violations.append({
                    "type": "invalid_race",
                    "severity": "medium",
                    "field": f"npc.{npc.get('name', 'unknown')}.race",
                    "message": f"Race '{npc['race']}' is not a valid D&D 5e race",
                    "suggestion": f"Use one of: {', '.join(sorted(self.VALID_RACES))}"
                })

        # Validate class
        if "character_class" in npc:
            char_class = npc["character_class"].lower()
            if char_class not in self.VALID_CLASSES:
                self.violations.append({
                    "type": "invalid_class",
                    "severity": "medium",
                    "field": f"npc.{npc.get('name', 'unknown')}.character_class",
                    "message": f"Class '{npc['character_class']}' is not a valid D&D 5e class",
                    "suggestion": f"Use one of: {', '.join(sorted(self.VALID_CLASSES))}"
                })

        # Validate background
        if "background" in npc:
            background = npc["background"].lower()
            if background not in self.VALID_BACKGROUNDS:
                self.violations.append({
                    "type": "invalid_background",
                    "severity": "low",
                    "field": f"npc.{npc.get('name', 'unknown')}.background",
                    "message": f"Background '{npc['background']}' is not a valid D&D 5e background",
                    "suggestion": f"Use one of: {', '.join(sorted(self.VALID_BACKGROUNDS))}"
                })

        # Validate personality structure
        if "personality" in npc:
            personality = npc["personality"]
            if isinstance(personality, dict):
                required_keys = ["traits", "ideals", "bonds", "flaws"]
                for key in required_keys:
                    if key not in personality:
                        self.violations.append({
                            "type": "missing_personality",
                            "severity": "low",
                            "field": f"npc.{npc.get('name', 'unknown')}.personality.{key}",
                            "message": f"NPC personality missing required field: {key}"
                        })

    def _validate_location(self, location: Dict[str, Any]):
        """Validate location data"""
        # Check for encounters
        if "encounters" in location and location["encounters"]:
            for encounter in location["encounters"]:
                if isinstance(encounter, dict):
                    self._validate_encounter(encounter, location.get("name", "unknown"))

    def _validate_encounter(self, encounter: Dict[str, Any], location_name: str):
        """Validate encounter data"""
        encounter_type = encounter.get("type", "").lower()

        if encounter_type == "combat":
            # Validate combat encounter
            if "difficulty" in encounter:
                difficulty = encounter["difficulty"].lower()
                valid_difficulties = ["easy", "medium", "hard", "deadly"]
                if difficulty not in valid_difficulties:
                    self.violations.append({
                        "type": "invalid_difficulty",
                        "severity": "medium",
                        "field": f"location.{location_name}.encounter.difficulty",
                        "message": f"Encounter difficulty '{difficulty}' is invalid",
                        "suggestion": f"Use one of: {', '.join(valid_difficulties)}"
                    })

    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        if not self.violations:
            return 1.0

        # Weight violations by severity
        severity_weights = {
            "high": 1.0,
            "medium": 0.5,
            "low": 0.25
        }

        total_weight = sum(severity_weights.get(v.get("severity", "medium"), 0.5) for v in self.violations)
        max_possible_score = 1.0

        # Reduce score based on violations
        compliance_score = max(0.0, max_possible_score - (total_weight * 0.1))

        return round(compliance_score, 2)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        violation_types = {}
        for violation in self.violations:
            v_type = violation.get("type", "unknown")
            if v_type not in violation_types:
                violation_types[v_type] = []
            violation_types[v_type].append(violation)

        # Generate specific recommendations
        if "invalid_race" in violation_types:
            recommendations.append("Review NPC races to ensure they match official D&D 5e races")

        if "invalid_class" in violation_types:
            recommendations.append("Review NPC classes to ensure they match official D&D 5e classes")

        if "invalid_background" in violation_types:
            recommendations.append("Consider using official D&D 5e backgrounds for better compatibility")

        if "invalid_level" in violation_types:
            recommendations.append("Ensure all character levels are between 1 and 20")

        if "missing_field" in violation_types:
            recommendations.append("Add missing required fields to complete the campaign structure")

        if "insufficient_content" in violation_types:
            recommendations.append("Expand descriptions and content for better campaign quality")

        # General recommendations
        if len(self.violations) > 5:
            recommendations.append("Consider regenerating content to reduce rule violations")

        if not recommendations:
            recommendations.append("Campaign structure looks good!")

        return recommendations

    def validate_encounter_balance(self, party_level: int, party_size: int,
                                 encounter_cr: float, monster_count: int) -> Dict[str, Any]:
        """Validate encounter balance using D&D 5e XP budget system"""
        # Calculate XP budget for the party
        base_xp_budget = self._get_xp_budget(party_level)
        adjusted_budget = self._adjust_budget_for_party_size(base_xp_budget, party_size)

        # Calculate encounter XP
        monster_xp = self.CR_TO_XP.get(encounter_cr, 0)
        total_encounter_xp = monster_xp * monster_count

        # Determine difficulty
        difficulty = self._calculate_difficulty(adjusted_budget, total_encounter_xp)

        # Calculate balance score
        balance_score = self._calculate_balance_score(adjusted_budget, total_encounter_xp)

        return {
            "difficulty": difficulty,
            "xp_budget": adjusted_budget,
            "encounter_xp": total_encounter_xp,
            "balance_score": balance_score,
            "is_balanced": balance_score >= 0.7,
            "recommendations": self._generate_balance_recommendations(difficulty, balance_score)
        }

    def _get_xp_budget(self, level: int) -> int:
        """Get base XP budget for party level"""
        xp_budgets = {
            1: 25, 2: 50, 3: 75, 4: 125, 5: 250, 6: 300, 7: 350, 8: 450,
            9: 550, 10: 600, 11: 800, 12: 1000, 13: 1100, 14: 1250,
            15: 1400, 16: 1600, 17: 2000, 18: 2100, 19: 2400, 20: 2800
        }
        return xp_budgets.get(level, 2800)

    def _adjust_budget_for_party_size(self, base_budget: int, party_size: int) -> int:
        """Adjust XP budget based on party size"""
        size_multipliers = {
            1: 1.0,    # Solo
            2: 1.5,    # Duo
            3: 2.0,    # Small party
            4: 2.0,    # Small party
            5: 3.0,    # Medium party
            6: 3.0,    # Medium party
            7: 4.0,    # Large party
            8: 4.0     # Large party
        }
        multiplier = size_multipliers.get(party_size, 2.0)
        return int(base_budget * multiplier)

    def _calculate_difficulty(self, budget: int, encounter_xp: int) -> str:
        """Calculate encounter difficulty"""
        ratio = encounter_xp / budget

        if ratio <= 0.5:
            return "easy"
        elif ratio <= 1.0:
            return "medium"
        elif ratio <= 1.5:
            return "hard"
        elif ratio <= 2.0:
            return "deadly"
        else:
            return "impossible"

    def _calculate_balance_score(self, budget: int, encounter_xp: int) -> float:
        """Calculate balance score (0-1)"""
        ratio = encounter_xp / budget

        # Optimal balance is around 1.0 (medium difficulty)
        if ratio <= 1.0:
            # Scale from 0 to 1.0
            return min(1.0, ratio / 1.0)
        else:
            # Scale from 1.0 to 2.0, then decrease
            over_budget_ratio = (ratio - 1.0) / 1.0  # 0 to 1 for 1x to 2x budget
            return max(0.0, 1.0 - over_budget_ratio)

    def _generate_balance_recommendations(self, difficulty: str, balance_score: float) -> List[str]:
        """Generate recommendations for encounter balance"""
        recommendations = []

        if difficulty == "easy":
            recommendations.append("This encounter may be too easy for the party")
            recommendations.append("Consider adding more monsters or higher CR creatures")
        elif difficulty == "medium":
            recommendations.append("Good balance for a standard encounter")
        elif difficulty == "hard":
            recommendations.append("Challenging encounter - ensure party has resources")
        elif difficulty == "deadly":
            recommendations.append("Very dangerous encounter - party may need preparation")
            recommendations.append("Consider adding easier encounters before this one")
        elif difficulty == "impossible":
            recommendations.append("This encounter is likely too difficult")
            recommendations.append("Reduce monster count or use lower CR creatures")

        if balance_score < 0.5:
            recommendations.append("Major balance issues detected - consider redesigning the encounter")

        return recommendations

    # Legacy compatibility methods for existing code

    def validate_campaign_legacy(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy validation method for backward compatibility"""
        result = self.validate_campaign(campaign_data)

        # Convert new format to legacy format
        return {
            "is_compliant": result.is_valid,
            "compliance_score": result.score,
            "violations": [
                {
                    "type": issue.category.value,
                    "severity": issue.severity.value,
                    "field": f"{issue.context.get('field', 'unknown')}",
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in result.issues
            ],
            "recommendations": [issue.suggestion for issue in result.issues if issue.suggestion]
        }

    # Legacy methods for basic validation (keeping for compatibility)

    VALID_RACES = [
        'human', 'elf', 'dwarf', 'halfling', 'dragonborn',
        'tiefling', 'half-elf', 'half-orc', 'gnome'
    ]

    VALID_CLASSES = [
        'barbarian', 'bard', 'cleric', 'druid', 'fighter',
        'monk', 'paladin', 'ranger', 'rogue', 'sorcerer',
        'warlock', 'wizard'
    ]

    VALID_BACKGROUNDS = [
        'acolyte', 'criminal', 'entertainer', 'folk_hero',
        'guild_artisan', 'hermit', 'noble', 'outlander',
        'sage', 'sailor', 'soldier', 'urchin'
    ]

    def validate_campaign_old(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy campaign validation method - simplified version for compatibility"""
        violations = []

        # Validate basic campaign structure
        required_fields = ["name", "description", "theme", "difficulty", "party_size"]
        for field in required_fields:
            if field not in campaign_data:
                violations.append({
                    "type": "missing_field",
                    "severity": "high",
                    "field": field,
                    "message": f"Required field '{field}' is missing from campaign"
                })

        # Validate starting level
        if "starting_level" in campaign_data:
            level = campaign_data["starting_level"]
            if not isinstance(level, int) or not (1 <= level <= 20):
                violations.append({
                    "type": "invalid_level",
                    "severity": "high",
                    "field": "starting_level",
                    "message": f"Starting level {level} is invalid. Must be between 1 and 20."
                })

        # Validate NPCs
        if "npcs" in campaign_data:
            for npc in campaign_data["npcs"]:
                self._validate_npc_legacy(npc, violations)

        # Calculate compliance score
        compliance_score = 1.0 - (len(violations) * 0.1)
        compliance_score = max(0.0, compliance_score)

        return {
            "is_compliant": len(violations) == 0,
            "compliance_score": round(compliance_score, 2),
            "violations": violations,
            "recommendations": self._generate_recommendations_legacy(violations)
        }

    def _validate_npc_legacy(self, npc: Dict[str, Any], violations: List[Dict[str, Any]]):
        """Legacy NPC validation for compatibility"""
        # Validate race
        if "race" in npc:
            race = npc["race"].lower()
            if race not in self.VALID_RACES:
                violations.append({
                    "type": "invalid_race",
                    "severity": "medium",
                    "field": f"npc.{npc.get('name', 'unknown')}.race",
                    "message": f"Race '{npc['race']}' is not a valid D&D 5e race",
                    "suggestion": f"Use one of: {', '.join(sorted(self.VALID_RACES))}"
                })

        # Validate class
        if "character_class" in npc:
            char_class = npc["character_class"].lower()
            if char_class not in self.VALID_CLASSES:
                violations.append({
                    "type": "invalid_class",
                    "severity": "medium",
                    "field": f"npc.{npc.get('name', 'unknown')}.character_class",
                    "message": f"Class '{npc['character_class']}' is not a valid D&D 5e class",
                    "suggestion": f"Use one of: {', '.join(sorted(self.VALID_CLASSES))}"
                })

    def _generate_recommendations_legacy(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations from legacy violations"""
        recommendations = []

        violation_types = {}
        for violation in violations:
            v_type = violation.get("type", "unknown")
            if v_type not in violation_types:
                violation_types[v_type] = []
            violation_types[v_type].append(violation)

        # Generate specific recommendations
        if "invalid_race" in violation_types:
            recommendations.append("Review NPC races to ensure they match official D&D 5e races")

        if "invalid_class" in violation_types:
            recommendations.append("Review NPC classes to ensure they match official D&D 5e classes")

        if "invalid_level" in violation_types:
            recommendations.append("Ensure all character levels are between 1 and 20")

        if "missing_field" in violation_types:
            recommendations.append("Add missing required fields to complete the campaign structure")

        if not recommendations:
            recommendations.append("Campaign structure looks good!")

        return recommendations
