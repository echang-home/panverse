#!/usr/bin/env python3
"""
Test script for the Comprehensive CursorRules Service
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up Django-like module structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'domain'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'services'))

from cursor_rules_comprehensive import ComprehensiveCursorRulesService

def test_monster_validation():
    """Test monster validation"""
    print("Testing monster validation...")

    rules_service = ComprehensiveCursorRulesService()

    # Test valid monster
    valid_monster = {
        "name": "Cave Troll",
        "size": "Large",
        "type": "giant",
        "alignment": "chaotic evil",
        "armor_class": 15,
        "hit_points": 84,
        "speed": "30 ft.",
        "strength": 18,
        "dexterity": 8,
        "constitution": 16,
        "intelligence": 7,
        "wisdom": 9,
        "charisma": 7,
        "challenge_rating": "5"
    }

    result = rules_service.validate("monster", valid_monster)
    print(f"Valid monster result: is_valid={result.is_valid}, score={result.score}")
    for issue in result.issues:
        print(f"  - {issue.severity.value}: {issue.message}")

    # Test invalid monster
    invalid_monster = {
        "name": "Test Monster",
        "size": "Large",
        "type": "giant",
        "alignment": "chaotic evil",
        "armor_class": 15,
        "hit_points": 84,
        "speed": "30 ft.",
        "strength": 35,  # Invalid ability score
        "dexterity": 8,
        "constitution": 16,
        "intelligence": 7,
        "wisdom": 9,
        "charisma": 7,
        "challenge_rating": "99"  # Invalid CR
    }

    result = rules_service.validate("monster", invalid_monster)
    print(f"Invalid monster result: is_valid={result.is_valid}, score={result.score}")
    for issue in result.issues:
        print(f"  - {issue.severity.value}: {issue.message}")

def test_item_validation():
    """Test item validation"""
    print("\nTesting item validation...")

    rules_service = ComprehensiveCursorRulesService()

    # Test valid item
    valid_item = {
        "name": "Sword of Sharpness",
        "type": "weapon",
        "description": "A magical sword that deals extra damage",
        "rarity": "rare"
    }

    result = rules_service.validate("item", valid_item)
    print(f"Valid item result: is_valid={result.is_valid}, score={result.score}")

    # Test invalid item
    invalid_item = {
        "name": "Test Item",
        "type": "weapon",
        "description": "A test item",
        "rarity": "ultra_mega_rare"  # Invalid rarity
    }

    result = rules_service.validate("item", invalid_item)
    print(f"Invalid item result: is_valid={result.is_valid}, score={result.score}")
    for issue in result.issues:
        print(f"  - {issue.severity.value}: {issue.message}")

def test_campaign_validation():
    """Test campaign validation"""
    print("\nTesting campaign validation...")

    rules_service = ComprehensiveCursorRulesService()

    # Define test data
    valid_monster = {
        "name": "Cave Troll",
        "size": "Large",
        "type": "giant",
        "alignment": "chaotic evil",
        "armor_class": 15,
        "hit_points": 84,
        "speed": "30 ft.",
        "strength": 18,
        "dexterity": 8,
        "constitution": 16,
        "intelligence": 7,
        "wisdom": 9,
        "charisma": 7,
        "challenge_rating": "5"
    }

    valid_item = {
        "name": "Sword of Sharpness",
        "type": "weapon",
        "description": "A magical sword that deals extra damage",
        "rarity": "rare"
    }

    # Test valid campaign
    valid_campaign = {
        "name": "The Dragon's Awakening",
        "description": "A tale of political intrigue and ancient magic",
        "theme": "fantasy",
        "level_range": "1-5",
        "monsters": [valid_monster],
        "items": [valid_item]
    }

    result = rules_service.validate("campaign", valid_campaign)
    print(f"Valid campaign result: is_valid={result.is_valid}, score={result.score}")

    # Test invalid campaign
    invalid_campaign = {
        "name": "Test Campaign",
        "description": "A test campaign",
        "theme": "fantasy",
        "level_range": "25-30"  # Invalid level range
    }

    result = rules_service.validate("campaign", invalid_campaign)
    print(f"Invalid campaign result: is_valid={result.is_valid}, score={result.score}")
    for issue in result.issues:
        print(f"  - {issue.severity.value}: {issue.message}")

if __name__ == "__main__":
    print("Testing Comprehensive CursorRules Service")
    print("=" * 50)

    try:
        test_monster_validation()
        test_item_validation()
        test_campaign_validation()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
