"""
Repository Interfaces for Data Access
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from .entities import Campaign, World, StoryHook, StoryArc, NPC, Location


class CampaignRepository(ABC):
    """Abstract repository for campaign data access"""

    @abstractmethod
    async def save(self, campaign: Campaign) -> Campaign:
        """Save a campaign"""
        pass

    @abstractmethod
    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> List[Campaign]:
        """Get campaigns by user ID"""
        pass

    @abstractmethod
    async def update(self, campaign_id: UUID, updates: Dict[str, Any]) -> Campaign:
        """Update a campaign"""
        pass

    @abstractmethod
    async def delete(self, campaign_id: UUID) -> bool:
        """Delete a campaign"""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count campaigns for a user"""
        pass


class WorldRepository(ABC):
    """Abstract repository for world data access"""

    @abstractmethod
    async def save(self, world: World) -> World:
        """Save a world"""
        pass

    @abstractmethod
    async def get_by_campaign_id(self, campaign_id: UUID) -> Optional[World]:
        """Get world by campaign ID"""
        pass

    @abstractmethod
    async def update(self, world_id: UUID, updates: Dict[str, Any]) -> World:
        """Update a world"""
        pass


class StoryRepository(ABC):
    """Abstract repository for story elements data access"""

    @abstractmethod
    async def save_hook(self, hook: StoryHook) -> StoryHook:
        """Save a story hook"""
        pass

    @abstractmethod
    async def save_arc(self, arc: StoryArc) -> StoryArc:
        """Save a story arc"""
        pass

    @abstractmethod
    async def get_hooks_by_campaign_id(self, campaign_id: UUID) -> List[StoryHook]:
        """Get story hooks by campaign ID"""
        pass

    @abstractmethod
    async def get_arcs_by_campaign_id(self, campaign_id: UUID) -> List[StoryArc]:
        """Get story arcs by campaign ID"""
        pass


class CharacterRepository(ABC):
    """Abstract repository for character data access"""

    @abstractmethod
    async def save_npc(self, npc: NPC) -> NPC:
        """Save an NPC"""
        pass

    @abstractmethod
    async def get_npcs_by_campaign_id(self, campaign_id: UUID) -> List[NPC]:
        """Get NPCs by campaign ID"""
        pass

    @abstractmethod
    async def update_npc(self, npc_id: UUID, updates: Dict[str, Any]) -> NPC:
        """Update an NPC"""
        pass


class LocationRepository(ABC):
    """Abstract repository for location data access"""

    @abstractmethod
    async def save_location(self, location: Location) -> Location:
        """Save a location"""
        pass

    @abstractmethod
    async def get_locations_by_campaign_id(self, campaign_id: UUID) -> List[Location]:
        """Get locations by campaign ID"""
        pass

    @abstractmethod
    async def update_location(self, location_id: UUID, updates: Dict[str, Any]) -> Location:
        """Update a location"""
        pass


class ContentCacheRepository(ABC):
    """Abstract repository for content caching"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached content"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Set cached content with TTL"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cached content"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class GenerationRequestRepository(ABC):
    """Abstract repository for generation request tracking"""

    @abstractmethod
    async def create_request(
        self,
        user_id: UUID,
        request_data: Dict[str, Any]
    ) -> UUID:
        """Create a new generation request"""
        pass

    @abstractmethod
    async def get_request(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """Get generation request by ID"""
        pass

    @abstractmethod
    async def update_request_status(
        self,
        request_id: UUID,
        status: str,
        campaign_id: Optional[UUID] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update generation request status"""
        pass

    @abstractmethod
    async def get_pending_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending generation requests for processing"""
        pass


class UserPreferencesRepository(ABC):
    """Abstract repository for user preferences data access"""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user preferences by user ID"""
        pass

    @abstractmethod
    async def save(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Save user preferences"""
        pass

    @abstractmethod
    async def update(self, user_id: UUID, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user preferences"""
        pass
