#!/usr/bin/env python3
"""
Watchdog Service Demo

This script demonstrates the Watchdog service monitoring AI content generation.
"""

import json
import time
from src.services.watchdog_service import WatchdogService, AlertSeverity


def demo_alert_callback(alert):
    """Demo callback for alerts"""
    print(f"🚨 ALERT: {alert.message} (Severity: {alert.severity.value})")
    if alert.details:
        print(f"   Details: {alert.details}")


def main():
    """Run the Watchdog service demo"""
    print("🔍 Watchdog Service Demo")
    print("=" * 50)

    # Initialize Watchdog
    print("\n1. Initializing Watchdog Service...")
    watchdog = WatchdogService()

    # Register alert callback
    watchdog.register_alert_callback(demo_alert_callback)

    print("✅ Watchdog initialized successfully")

    # Demo API call tracking
    print("\n2. Tracking API calls...")

    # Simulate Claude API call
    print("   📡 Tracking Claude API call...")
    watchdog.track_api_call(
        api_name="claude",
        token_count=1200,
        response_time=3.2,
        cost=0.024
    )

    # Simulate OpenAI API call
    print("   📡 Tracking OpenAI API call...")
    watchdog.track_api_call(
        api_name="chatgpt",
        token_count=800,
        response_time=2.1,
        cost=0.016
    )

    print("✅ API calls tracked")

    # Demo content verification
    print("\n3. Testing content verification...")

    # Test valid monster content
    print("   🔍 Verifying valid monster content...")
    valid_monster = """
    # Cave Troll

    *Large giant, chaotic evil*

    **Armor Class** 15 (natural armor)
    **Hit Points** 84 (8d10 + 40)
    **Speed** 30 ft.

    | STR | DEX | CON | INT | WIS | CHA |
    |:---:|:---:|:---:|:---:|:---:|:---:|
    | 18 (+4) | 8 (-1) | 16 (+3) | 7 (-2) | 9 (-1) | 7 (-2) |

    **Skills** Perception +2
    **Senses** darkvision 60 ft., passive Perception 12
    **Languages** Giant
    **Challenge** 5 (1,800 XP)
    """

    is_valid, issues = watchdog.verify_ai_response(valid_monster, "monster", "claude")
    print(f"   ✅ Valid monster content: {is_valid}")
    if issues:
        print(f"   Issues: {issues}")

    # Test invalid content with fallback
    print("   🔍 Verifying content with fallback phrase...")
    invalid_content = "I'm sorry, I cannot generate that content for you at this time."

    is_valid, issues = watchdog.verify_ai_response(invalid_content, "monster", "claude")
    print(f"   ❌ Content with fallback: {is_valid}")
    if issues:
        print(f"   Issues: {issues}")

    # Demo quality score tracking
    print("\n4. Tracking quality scores...")

    print("   📊 Tracking campaign generation quality...")
    watchdog.track_quality_score("campaign_generation", 0.87, {"campaign_id": "demo-123"})

    print("   📊 Tracking NPC generation quality...")
    watchdog.track_quality_score("npc_generation", 0.92, {"npc_count": 3})

    print("   📊 Tracking low quality score...")
    watchdog.track_quality_score("location_generation", 0.35, {"location_type": "dungeon"})

    # Demo API usage summary
    print("\n5. API Usage Summary:")
    usage_summary = watchdog.get_api_usage_summary()
    print(f"   Total API calls: {usage_summary['total_calls']}")
    print(f"   Calls by API: {usage_summary['calls_by_api']}")
    print(f"   Total estimated cost: ${usage_summary['total_estimated_cost']:.4f}")
    print("   Token usage by API:")
    for api, stats in usage_summary['token_usage'].items():
        if stats['total_calls'] > 0:
            print(f"     {api}: {stats['total_calls']} calls, "
                  f"{stats['avg_tokens_per_call']:.0f} avg tokens, "
                  f"${stats['estimated_cost']:.4f}")

    # Demo quality summary
    print("\n6. Quality Summary:")
    quality_summary = watchdog.get_quality_summary()
    print(f"   Average quality: {quality_summary['average_quality']:.2f}")
    print(f"   Components measured: {quality_summary['total_components_measured']}")
    print("   Quality by component:")
    for component, stats in quality_summary['quality_by_component'].items():
        print(f"     {component}: {stats['avg_score']:.2f} "
              f"({stats['samples']} samples)")

    # Demo error summary
    print("\n7. Error Summary:")
    error_summary = watchdog.get_error_summary()
    print(f"   Total errors: {error_summary['total_errors']}")
    print(f"   Overall error rate: {error_summary['overall_error_rate']:.2%}")
    if error_summary['error_by_component']:
        print("   Errors by component:")
        for component, stats in error_summary['error_by_component'].items():
            print(f"     {component}: {stats['error_rate']:.2%} "
                  f"({stats['error_count']}/{stats['samples']} samples)")

    # Demo alert summary
    print("\n8. Alert Summary:")
    print(f"   Total alerts: {len(watchdog.alerts)}")
    for i, alert in enumerate(watchdog.alerts, 1):
        print(f"   {i}. [{alert.severity.value.upper()}] {alert.message}")
        print(f"      Source: {alert.source}")

    # Save metrics
    print("\n9. Saving metrics...")
    watchdog._save_metrics()
    watchdog.save_alerts()
    print("✅ Metrics and alerts saved")

    print("\n" + "=" * 50)
    print("🎉 Watchdog Demo Complete!")
    print("\nThe Watchdog service is now integrated into your campaign generator")
    print("and will monitor AI content generation for quality and reliability.")


if __name__ == "__main__":
    main()
