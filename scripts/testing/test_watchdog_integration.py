"""
Integration Test for Watchdog Service

This test verifies that the Watchdog service integrates properly
with the existing AI service and container infrastructure.
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, AsyncMock

from src.services.watchdog_service import WatchdogService, AlertSeverity, MetricType
from src.services.ai_service import ClaudeAIService


class TestWatchdogIntegration(unittest.TestCase):
    """Integration tests for Watchdog service"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for metrics
        self.temp_dir = tempfile.mkdtemp()
        self.watchdog = WatchdogService(metrics_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_watchdog_initialization(self):
        """Test that Watchdog service initializes correctly"""
        self.assertIsInstance(self.watchdog, WatchdogService)
        self.assertIsInstance(self.watchdog.content_verifier, object)
        self.assertEqual(len(self.watchdog.metrics), 0)
        self.assertEqual(len(self.watchdog.alerts), 0)
        self.assertEqual(self.watchdog.error_count, 0)

    def test_api_call_tracking(self):
        """Test API call tracking functionality"""
        # Track an API call
        self.watchdog.track_api_call(
            api_name="claude",
            token_count=500,
            response_time=2.5,
            cost=0.02
        )

        # Verify API call was tracked
        self.assertEqual(self.watchdog.api_calls["claude"], 1)
        self.assertEqual(self.watchdog.cost_estimates["claude"], 0.02)
        self.assertEqual(self.watchdog.cost_estimates["total"], 0.02)

        # Verify metric was recorded
        token_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.TOKEN_USAGE]
        latency_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.API_LATENCY]
        cost_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.COST]

        self.assertEqual(len(token_metrics), 1)
        self.assertEqual(len(latency_metrics), 1)
        self.assertEqual(len(cost_metrics), 1)

        self.assertEqual(token_metrics[0].value, 500)
        self.assertEqual(latency_metrics[0].value, 2.5)
        self.assertEqual(cost_metrics[0].value, 0.02)

    def test_content_verification(self):
        """Test content verification functionality"""
        # Test valid content
        valid_content = """
        # Ancient Dragon

        *Large dragon, chaotic neutral*

        **Armor Class** 18 (natural armor)
        **Hit Points** 200 (16d10 + 112)
        **Speed** 40 ft., fly 80 ft.

        | STR | DEX | CON | INT | WIS | CHA |
        |:---:|:---:|:---:|:---:|:---:|:---:|
        | 23 (+6) | 14 (+2) | 20 (+5) | 16 (+3) | 15 (+2) | 19 (+4) |

        **Saving Throws** Dex +7, Con +10, Wis +7, Cha +9
        **Skills** Perception +12, Stealth +7
        **Damage Immunities** fire
        **Senses** blindsight 60 ft., darkvision 120 ft., passive Perception 22
        **Languages** Common, Draconic
        **Challenge** 15 (13,000 XP)
        """

        is_valid, issues = self.watchdog.verify_ai_response(valid_content, "monster", "claude")
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)

        # Test invalid content with fallback phrases
        invalid_content = "I'm sorry, I cannot generate monster content for you."

        is_valid, issues = self.watchdog.verify_ai_response(invalid_content, "monster", "claude")
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn("fallback", issues[0].lower())

        # Test invalid content with placeholders
        placeholder_content = "This is a {placeholder} monster with [placeholder] stats."

        is_valid, issues = self.watchdog.verify_ai_response(placeholder_content, "monster", "claude")
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn("placeholder", issues[0].lower())

    def test_alert_creation(self):
        """Test alert creation and tracking"""
        # Create a test alert
        self.watchdog._create_alert(
            message="Test alert",
            severity=AlertSeverity.WARNING,
            source="test_component",
            details={"test_key": "test_value"}
        )

        # Verify alert was created
        self.assertEqual(len(self.watchdog.alerts), 1)
        alert = self.watchdog.alerts[0]
        self.assertEqual(alert.message, "Test alert")
        self.assertEqual(alert.severity, AlertSeverity.WARNING)
        self.assertEqual(alert.source, "test_component")
        self.assertEqual(alert.details["test_key"], "test_value")
        self.assertFalse(alert.resolved)

    def test_quality_score_tracking(self):
        """Test quality score tracking"""
        # Track a quality score
        self.watchdog.track_quality_score(
            component="campaign_generation",
            score=0.85,
            details={"campaign_id": "test-123"}
        )

        # Verify metric was recorded
        quality_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.QUALITY_SCORE]
        self.assertEqual(len(quality_metrics), 1)
        self.assertEqual(quality_metrics[0].value, 0.85)
        self.assertEqual(quality_metrics[0].component, "campaign_generation")

    def test_api_usage_summary(self):
        """Test API usage summary generation"""
        # Track some API calls
        self.watchdog.track_api_call("claude", 500, 2.5, 0.02)
        self.watchdog.track_api_call("claude", 300, 1.8, 0.015)
        self.watchdog.track_api_call("chatgpt", 400, 3.2, 0.03)

        # Get usage summary
        summary = self.watchdog.get_api_usage_summary()

        # Verify summary structure
        self.assertIn("total_calls", summary)
        self.assertIn("calls_by_api", summary)
        self.assertIn("token_usage", summary)
        self.assertIn("total_estimated_cost", summary)

        # Verify values
        self.assertEqual(summary["total_calls"], 3)
        self.assertEqual(summary["calls_by_api"]["claude"], 2)
        self.assertEqual(summary["calls_by_api"]["chatgpt"], 1)
        self.assertAlmostEqual(summary["total_estimated_cost"], 0.065, places=3)

    def test_quality_summary(self):
        """Test quality metrics summary"""
        # Track some quality scores
        self.watchdog.track_quality_score("campaign", 0.8)
        self.watchdog.track_quality_score("campaign", 0.9)
        self.watchdog.track_quality_score("npc", 0.7)

        # Get quality summary
        summary = self.watchdog.get_quality_summary()

        # Verify summary structure
        self.assertIn("average_quality", summary)
        self.assertIn("quality_by_component", summary)
        self.assertIn("total_components_measured", summary)

        # Verify values
        expected_avg = (0.8 + 0.9 + 0.7) / 3
        self.assertAlmostEqual(summary["average_quality"], expected_avg, places=3)
        self.assertEqual(summary["total_components_measured"], 2)  # campaign and npc


class TestClaudeAIServiceIntegration(unittest.TestCase):
    """Integration tests for ClaudeAI service with Watchdog"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.watchdog = WatchdogService(metrics_path=self.temp_dir)
        self.ai_service = ClaudeAIService(
            api_key="test-key",
            watchdog_service=self.watchdog
        )

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ai_service_initialization_with_watchdog(self):
        """Test that AI service initializes with Watchdog"""
        self.assertIsNotNone(self.ai_service.watchdog_service)
        self.assertEqual(self.ai_service.watchdog_service, self.watchdog)

    @patch('src.services.ai_service.anthropic')
    def test_mock_api_call_tracking(self, mock_anthropic):
        """Test that mock API calls are tracked by Watchdog"""
        # Setup mock
        mock_anthropic.Anthropic.side_effect = ImportError("Mock import error")

        # Make a call that should use mock response
        import asyncio
        async def test_call():
            result = await self.ai_service._call_claude_api("test prompt")
            return result

        # Run the async call
        result = asyncio.run(test_call())

        # Parse the result
        data = json.loads(result)

        # Verify it returned mock response
        self.assertIn("Mock Claude response", data["content"])

        # Verify API call was tracked
        self.assertEqual(self.watchdog.api_calls["claude"], 1)
        self.assertEqual(self.watchdog.cost_estimates["claude"], 0.0)

        # Verify metrics were recorded
        token_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.TOKEN_USAGE]
        latency_metrics = [m for m in self.watchdog.metrics if m.metric_type == MetricType.API_LATENCY]

        self.assertEqual(len(token_metrics), 1)
        self.assertEqual(len(latency_metrics), 1)


if __name__ == "__main__":
    unittest.main()
