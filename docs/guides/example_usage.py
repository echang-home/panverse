#!/usr/bin/env python3
"""
Example usage of the Comprehensive CursorRules Service

This script demonstrates how to use the new comprehensive D&D 5e validation service.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'domain'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'services'))

from cursor_rules_comprehensive import ComprehensiveCursorRulesService

def main():
    print("Comprehensive CursorRules Service - Example Usage")
    print("=" * 55)

    # Initialize the validation service
    rules_service = ComprehensiveCursorRulesService()

    # Example 1: Valid Monster
    print("\n1. Valid Monster Validation:")
    valid_monster = {
        "name": "Ancient Red Dragon",
        "size": "Gargantuan",
        "type": "dragon",
        "alignment": "chaotic evil",
        "armor_class": 22,
        "hit_points": 546,
        "speed": "40 ft., climb 40 ft., fly 80 ft.",
        "strength": 30,
        "dexterity": 10,
        "constitution": 29,
        "intelligence": 18,
        "wisdom": 15,
        "charisma": 23,
        "challenge_rating": "24"
    }

    result = rules_service.validate("monster", valid_monster)
    print(f"   Monster: {valid_monster['name']}")
    print(f"   Valid: {result.is_valid}, Score: {result.score:.2f}")
    if result.issues:
        print(f"   Issues: {len(result.issues)}")

    # Example 2: Invalid Item
    print("\n2. Invalid Item Validation:")
    invalid_item = {
        "name": "Sword of Ultimate Power",
        "type": "weapon",
        "description": "The most powerful sword ever created",
        "rarity": "godlike"  # Invalid rarity
    }

    result = rules_service.validate("item", invalid_item)
    print(f"   Item: {invalid_item['name']}")
    print(f"   Valid: {result.is_valid}, Score: {result.score:.2f}")
    if result.issues:
        for issue in result.issues:
            print(f"   Issue: {issue.message}")
            if issue.suggestion:
                print(f"   Suggestion: {issue.suggestion}")

    # Example 3: Campaign Validation
    print("\n3. Campaign Validation:")
    campaign = {
        "name": "The Dragon's Awakening",
        "description": "A tale of political intrigue and ancient magic in the kingdom of Eldoria",
        "theme": "fantasy",
        "level_range": "1-5",
        "monsters": [valid_monster],
        "items": [invalid_item]
    }

    result = rules_service.validate("campaign", campaign)
    print(f"   Campaign: {campaign['name']}")
    print(f"   Valid: {result.is_valid}, Score: {result.score:.2f}")
    print(f"   Component Scores:")
    for component, score in result.component_scores.items():
        print(f"     {component}: {score:.2f}")

    if result.issues:
        print(f"   Total Issues: {len(result.issues)}")
        for issue in result.issues:
            print(f"     - {issue.category.value}: {issue.message}")

    print("\n" + "=" * 55)
    print("Example completed successfully!")
    print("\nKey Features:")
    print("- Comprehensive D&D 5e rule validation")
    print("- Detailed scoring and issue reporting")
    print("- Prevents AI drift and ensures rule compliance")
    print("- Supports multiple content types (monster, item, campaign, etc.)")
    print("- JSON-based rule configuration")
    print("- Extensible validation framework")

if __name__ == "__main__":
    main()
