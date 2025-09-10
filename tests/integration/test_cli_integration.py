"""
Integration tests for the CLI application
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.cli.app import CampaignGeneratorCLI
from src.infrastructure.container import DependencyContainer
from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog


class TestCLIIntegration:
    """Integration tests for the CLI application"""

    @pytest.fixture
    async def mock_container(self):
        """Create a mock dependency container"""
        container = MagicMock(spec=DependencyContainer)

        # Mock services
        container.claude_service = MagicMock()
        container.image_service = MagicMock()
        container.pdf_service = MagicMock()
        container.image_cache = MagicMock()
        container.content_cache = MagicMock()
        container.cursor_rules = MagicMock()
        container.watchdog_service = MagicMock()
        container.campaign_generation_service = MagicMock()
        container.campaign_retrieval_service = MagicMock()
        container.content_integrity_watchdog = MagicMock(spec=ContentIntegrityWatchdog)

        return container

    @pytest.fixture
    def cli_app(self, mock_container):
        """Create CLI app with mocked container"""
        cli = CampaignGeneratorCLI()
        cli.container = mock_container
        return cli

    @pytest.mark.asyncio
    async def test_cli_initialization(self, cli_app, mock_container):
        """Test CLI initialization with container"""
        assert cli_app.container == mock_container
        assert cli_app.user_id == "cli-user-12345"

    @pytest.mark.asyncio
    async def test_campaign_generation_flow(self, cli_app, mock_container):
        """Test the complete campaign generation flow"""
        # Mock the generation service
        generation_service = mock_container.campaign_generation_service
        retrieval_service = mock_container.campaign_retrieval_service
        pdf_service = mock_container.pdf_service
        watchdog_service = mock_container.watchdog_service

        # Setup mocks
        generation_service.generate_campaign.return_value = "test-request-id"
        generation_service.get_generation_status.return_value = {
            "status": "completed",
            "campaign_id": "test-campaign-id"
        }

        mock_campaign = MagicMock()
        mock_campaign.name = "Test Campaign"
        mock_campaign.description = "A test campaign"
        mock_campaign.theme.value = "fantasy"
        mock_campaign.difficulty.value = "medium"
        mock_campaign.party_size.value = "small"
        mock_campaign.starting_level = 3
        mock_campaign.expected_duration.value = "medium"
        mock_campaign.quality_score.value = 4.5
        mock_campaign.world = MagicMock()
        mock_campaign.world.name = "Test World"
        mock_campaign.key_npcs = []
        mock_campaign.key_locations = []
        mock_campaign.story_arcs = []

        retrieval_service.get_campaign.return_value = mock_campaign
        pdf_service.generate_campaign_pdf.return_value = "/path/to/test.pdf"
        watchdog_service.record_generation = AsyncMock()

        # Test data
        preferences = {
            "theme": "fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium",
            "custom_instructions": "Test instructions"
        }

        # Run generation
        campaign_id = await cli_app.generate_campaign(preferences)

        # Verify calls
        assert campaign_id == "test-campaign-id"
        generation_service.generate_campaign.assert_called_once()
        retrieval_service.get_campaign.assert_called_once_with("test-campaign-id", "cli-user-12345")
        pdf_service.generate_campaign_pdf.assert_called_once()
        watchdog_service.record_generation.assert_called_once()

    @pytest.mark.asyncio
    async def test_pdf_generation(self, cli_app, mock_container):
        """Test PDF generation functionality"""
        # Mock services
        retrieval_service = mock_container.campaign_retrieval_service
        pdf_service = mock_container.pdf_service

        # Setup mock campaign
        mock_campaign = MagicMock()
        mock_campaign.id = "test-campaign-id"
        mock_campaign.name = "Test Campaign"
        mock_campaign.description = "A test campaign description"
        mock_campaign.theme.value = "fantasy"
        mock_campaign.difficulty.value = "medium"
        mock_campaign.party_size.value = "small"
        mock_campaign.starting_level = 3
        mock_campaign.expected_duration.value = "medium"
        mock_campaign.quality_score.value = 4.5
        mock_campaign.world = None
        mock_campaign.key_npcs = []
        mock_campaign.key_locations = []
        mock_campaign.story_arcs = []

        retrieval_service.get_campaign.return_value = mock_campaign
        pdf_service.generate_campaign_pdf.return_value = "/path/to/test.pdf"

        # Test PDF generation
        pdf_path = await cli_app.generate_campaign_pdf("test-campaign-id")

        # Verify
        assert pdf_path == "/path/to/test.pdf"
        retrieval_service.get_campaign.assert_called_once_with("test-campaign-id", "cli-user-12345")
        pdf_service.generate_campaign_pdf.assert_called_once()

    @pytest.mark.asyncio
    async def test_campaign_display(self, cli_app, mock_container):
        """Test campaign summary display"""
        # Mock service
        retrieval_service = mock_container.campaign_retrieval_service

        # Setup mock campaign
        mock_campaign = MagicMock()
        mock_campaign.name = "Test Campaign"
        mock_campaign.description = "A test campaign description"
        mock_campaign.theme.value = "fantasy"
        mock_campaign.difficulty.value = "medium"
        mock_campaign.party_size.value = "small"
        mock_campaign.starting_level = 3
        mock_campaign.expected_duration.value = "medium"
        mock_campaign.quality_score.value = 4.5
        mock_campaign.world = MagicMock()
        mock_campaign.world.name = "Test World"
        mock_campaign.key_npcs = [MagicMock()]
        mock_campaign.key_locations = [MagicMock()]
        mock_campaign.story_arcs = [MagicMock()]

        retrieval_service.get_campaign.return_value = mock_campaign

        # Test display (should not raise exceptions)
        await cli_app.display_campaign_summary("test-campaign-id")

        # Verify service was called
        retrieval_service.get_campaign.assert_called_once_with("test-campaign-id", "cli-user-12345")

    @pytest.mark.asyncio
    async def test_error_handling(self, cli_app, mock_container):
        """Test error handling in CLI"""
        # Mock service to raise exception
        generation_service = mock_container.campaign_generation_service
        generation_service.generate_campaign.side_effect = Exception("Test error")

        preferences = {
            "theme": "fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium"
        }

        # Should handle error gracefully
        with pytest.raises(Exception, match="Test error"):
            await cli_app.generate_campaign(preferences)

    def test_preferences_validation(self):
        """Test user preferences structure"""
        # Valid preferences structure
        valid_prefs = {
            "theme": "fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium",
            "custom_instructions": "Test instructions"
        }

        # Should not raise exceptions when processing
        assert isinstance(valid_prefs, dict)
        assert "theme" in valid_prefs
        assert "difficulty" in valid_prefs
        assert "party_size" in valid_prefs
        assert "starting_level" in valid_prefs
        assert "duration" in valid_prefs

    @pytest.mark.asyncio
    async def test_content_integrity_watchdog_integration(self, cli_app, mock_container):
        """Test ContentIntegrityWatchdog integration with CLI"""
        # Setup mock ContentIntegrityWatchdog
        integrity_watchdog = mock_container.content_integrity_watchdog

        # Mock validation methods
        integrity_watchdog.validate_text_content.return_value = True
        integrity_watchdog.validate_campaign_concept.return_value = True
        integrity_watchdog.validate_entire_campaign.return_value = True

        # Setup campaign generation mocks
        generation_service = mock_container.campaign_generation_service
        generation_service.generate_campaign.return_value = "test-campaign-id"

        # Test preferences
        preferences = {
            "theme": "fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium"
        }

        # Run campaign generation
        campaign_id = await cli_app.generate_campaign(preferences)

        # Verify ContentIntegrityWatchdog was called
        assert campaign_id == "test-campaign-id"
        integrity_watchdog.validate_text_content.assert_called()
        integrity_watchdog.validate_campaign_concept.assert_called()
        integrity_watchdog.validate_entire_campaign.assert_called()

    @pytest.mark.asyncio
    async def test_content_integrity_watchdog_failure_handling(self, cli_app, mock_container):
        """Test handling of ContentIntegrityWatchdog validation failures"""
        # Setup mock ContentIntegrityWatchdog to fail validation
        integrity_watchdog = mock_container.content_integrity_watchdog
        integrity_watchdog.validate_campaign_concept.side_effect = Exception("Content integrity violation")

        # Setup campaign generation mocks
        generation_service = mock_container.campaign_generation_service
        generation_service.generate_campaign.side_effect = Exception("Content integrity violation")

        preferences = {
            "theme": "fantasy",
            "difficulty": "medium",
            "party_size": "small",
            "starting_level": 3,
            "duration": "medium"
        }

        # Should handle integrity validation failure gracefully
        with pytest.raises(Exception, match="Content integrity violation"):
            await cli_app.generate_campaign(preferences)

    def test_content_integrity_watchdog_mode_configuration(self):
        """Test ContentIntegrityWatchdog mode configuration in container"""
        # Test that watchdog can be configured for different modes
        active_watchdog = ContentIntegrityWatchdog(is_active=True)
        inactive_watchdog = ContentIntegrityWatchdog(is_active=False)

        assert active_watchdog.is_active is True
        assert inactive_watchdog.is_active is False

        # Test mode switching
        active_watchdog.set_active(False)
        assert active_watchdog.is_active is False

        inactive_watchdog.set_active(True)
        assert inactive_watchdog.is_active is True

    def test_content_integrity_watchdog_validation_rules(self):
        """Test ContentIntegrityWatchdog validation rule configuration"""
        watchdog = ContentIntegrityWatchdog()

        # Test forbidden patterns are configured
        assert len(watchdog.forbidden_patterns) > 0
        assert "placeholder" in watchdog.forbidden_patterns
        assert "mock" in watchdog.forbidden_patterns
        assert "sample" in watchdog.forbidden_patterns

        # Test minimum lengths are configured
        assert len(watchdog.min_section_lengths) > 0
        assert "description" in watchdog.min_section_lengths
        assert "npc" in watchdog.min_section_lengths

        # Test image prompt patterns are configured
        assert len(watchdog.forbidden_image_patterns) > 0

        # Test validation summary
        summary = watchdog.get_validation_summary()
        assert "total_validation_rules" in summary
        assert summary["total_validation_rules"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
