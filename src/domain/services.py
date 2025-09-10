"""
Domain Service Interfaces for the Campaign Generator
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from uuid import UUID

from .entities import Campaign
from .value_objects import CampaignTheme, DifficultyLevel, PartySize


class CampaignGenerationService(ABC):
    """Abstract service for campaign generation"""

    @abstractmethod
    async def generate_campaign(
        self,
        theme: str,
        difficulty: str,
        party_size: str,
        starting_level: int,
        duration: str,
        user_id: str,
        custom_instructions: Optional[str] = None,
        mode: str = "sample"
    ) -> str:
        """Generate a new campaign asynchronously"""
        pass

    @abstractmethod
    async def get_generation_status(self, request_id: UUID) -> Dict[str, Any]:
        """Get status of campaign generation"""
        pass

    @abstractmethod
    async def regenerate_campaign_section(
        self,
        campaign_id: UUID,
        section: str,
        custom_instructions: Optional[str] = None
    ) -> bool:
        """Regenerate a specific section of a campaign"""
        pass

    @abstractmethod
    async def extend_campaign(
        self,
        campaign_id: UUID,
        extension_type: str,
        custom_instructions: Optional[str] = None
    ) -> UUID:
        """Extend an existing campaign with new content"""
        pass


class CampaignRetrievalService(ABC):
    """Abstract service for campaign retrieval and management"""

    @abstractmethod
    async def get_campaign(self, campaign_id: UUID, user_id: UUID) -> Campaign:
        """Retrieve a specific campaign"""
        pass

    @abstractmethod
    async def list_user_campaigns(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List campaigns for a user"""
        pass

    @abstractmethod
    async def delete_campaign(self, campaign_id: UUID, user_id: UUID) -> bool:
        """Delete a campaign"""
        pass

    @abstractmethod
    async def update_campaign(
        self,
        campaign_id: UUID,
        updates: Dict[str, Any],
        user_id: UUID
    ) -> Campaign:
        """Update campaign details"""
        pass


class ContentValidationService(ABC):
    """Abstract service for content validation"""

    @abstractmethod
    async def validate_campaign_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign content for quality and compliance"""
        pass

    @abstractmethod
    async def validate_dnd_compliance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate D&D 5e rule compliance"""
        pass

    @abstractmethod
    async def calculate_quality_score(self, content: Dict[str, Any]) -> float:
        """Calculate overall quality score for content"""
        pass

    @abstractmethod
    async def identify_weak_areas(self, content: Dict[str, Any], quality_score: float) -> List[str]:
        """Identify areas that need improvement"""
        pass


class UserPreferencesService(ABC):
    """Abstract service for user preferences management"""

    @abstractmethod
    async def get_user_preferences(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        pass

    @abstractmethod
    async def update_user_preferences(self, user_id: UUID, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        pass

    @abstractmethod
    async def create_default_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """Create default preferences for new user"""
        pass

    @abstractmethod
    async def apply_preferences_to_generation(
        self,
        generation_params: Dict[str, Any],
        user_id: UUID
    ) -> Dict[str, Any]:
        """Apply user preferences to generation parameters"""
        pass


class MonitoringService(ABC):
    """Abstract service for monitoring AI generation and system health"""

    @abstractmethod
    def track_api_call(self, api_name: str, token_count: int, response_time: float, cost: float = None) -> None:
        """Track an API call with metrics"""
        pass

    @abstractmethod
    def verify_ai_response(self, content: str, content_type: str, source: str) -> tuple[bool, List[str]]:
        """Verify AI-generated content for quality and issues"""
        pass

    @abstractmethod
    def track_quality_score(self, component: str, score: float, details: Dict[str, Any] = None) -> None:
        """Track a quality score for a component"""
        pass

    @abstractmethod
    def register_alert_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback for alerts"""
        pass

    @abstractmethod
    def get_api_usage_summary(self) -> Dict[str, Any]:
        """Get summary of API usage statistics"""
        pass

    @abstractmethod
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get summary of quality metrics"""
        pass

    @abstractmethod
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error metrics"""
        pass


class ContentIntegrityService(ABC):
    """Abstract service for content integrity validation"""

    @abstractmethod
    def validate_text_content(self, section_name: str, content: str) -> bool:
        """Validate that content is real and not placeholder text"""
        pass

    @abstractmethod
    def validate_image_prompt(self, image_prompt: str) -> bool:
        """Validate that image generation prompts will create real images"""
        pass

    @abstractmethod
    def validate_entire_campaign(self, campaign: Campaign) -> bool:
        """Validate an entire campaign for content integrity"""
        pass

    @abstractmethod
    def validate_campaign_concept(self, concept: Dict[str, Any]) -> bool:
        """Validate a campaign concept for content integrity"""
        pass

    @abstractmethod
    def validate_batch_content(self, content_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of content items"""
        pass

    @abstractmethod
    def set_active(self, active: bool) -> None:
        """Set the active state of the integrity service"""
        pass

    @abstractmethod
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation configuration"""
        pass
