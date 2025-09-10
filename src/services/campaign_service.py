"""
Campaign Generation Service Implementation
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from domain.entities import Campaign, World, StoryHook, StoryArc, NPC, Location
# Import domain service interfaces
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("domain_services", os.path.join(parent_dir, "domain", "services.py"))
domain_services = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain_services)

CampaignGenerationService = domain_services.CampaignGenerationService
CampaignRetrievalService = domain_services.CampaignRetrievalService
from domain.repositories import (
    CampaignRepository, WorldRepository, StoryRepository,
    CharacterRepository, LocationRepository, GenerationRequestRepository
)
from domain.value_objects import (
    CampaignTheme, DifficultyLevel, PartySize, Duration,
    GenerationStatus, QualityScore
)
from .ai_service import AIService

logger = logging.getLogger(__name__)


class CampaignGenerationServiceImpl(CampaignGenerationService):
    """Implementation of campaign generation service"""

    def __init__(
        self,
        ai_service: AIService,
        campaign_repo: CampaignRepository,
        world_repo: WorldRepository,
        story_repo: StoryRepository,
        character_repo: CharacterRepository,
        location_repo: LocationRepository,
        generation_repo: GenerationRequestRepository
    ):
        self.ai_service = ai_service
        self.campaign_repo = campaign_repo
        self.world_repo = world_repo
        self.story_repo = story_repo
        self.character_repo = character_repo
        self.location_repo = location_repo
        self.generation_repo = generation_repo

    async def generate_campaign(
        self,
        theme: CampaignTheme,
        difficulty: DifficultyLevel,
        party_size: PartySize,
        starting_level: int,
        duration: str,
        user_id: UUID,
        custom_instructions: Optional[str] = None
    ) -> UUID:
        """Generate a new campaign asynchronously"""
        request_id = await self.generation_repo.create_request(
            user_id=user_id,
            request_data={
                "theme": theme.value,
                "difficulty": difficulty.value,
                "party_size": party_size.value,
                "starting_level": starting_level,
                "duration": duration,
                "custom_instructions": custom_instructions
            }
        )

        # Start async generation process
        # In a real implementation, this would queue the task
        logger.info(f"Starting campaign generation for request {request_id}")

        # For now, we'll simulate the generation
        await self._generate_campaign_async(
            request_id, theme, difficulty, party_size,
            starting_level, duration, user_id, custom_instructions
        )

        return request_id

    async def get_generation_status(self, request_id: UUID) -> Dict[str, Any]:
        """Get status of campaign generation"""
        request = await self.generation_repo.get_request(request_id)
        if not request:
            raise ValueError(f"Generation request {request_id} not found")

        return {
            "request_id": request_id,
            "status": request.get("status"),
            "campaign_id": request.get("campaign_id"),
            "error_message": request.get("error_message"),
            "created_at": request.get("created_at"),
            "completed_at": request.get("completed_at")
        }

    async def regenerate_campaign_section(
        self,
        campaign_id: UUID,
        section: str,
        custom_instructions: Optional[str] = None
    ) -> bool:
        """Regenerate a specific section of a campaign"""
        # Implementation for regenerating specific sections
        logger.info(f"Regenerating section {section} for campaign {campaign_id}")
        return True

    async def extend_campaign(
        self,
        campaign_id: UUID,
        extension_type: str,
        custom_instructions: Optional[str] = None
    ) -> UUID:
        """Extend an existing campaign with new content"""
        # Implementation for extending campaigns
        logger.info(f"Extending campaign {campaign_id} with type {extension_type}")
        return uuid4()

    async def _generate_campaign_async(
        self,
        request_id: UUID,
        theme: CampaignTheme,
        difficulty: DifficultyLevel,
        party_size: PartySize,
        starting_level: int,
        duration: str,
        user_id: UUID,
        custom_instructions: Optional[str] = None
    ) -> None:
        """Async campaign generation process"""
        try:
            # Update status to processing
            await self.generation_repo.update_request_status(request_id, "processing")

            # Generate campaign components
            campaign_data = await self._generate_campaign_components(
                theme, difficulty, party_size, starting_level, duration, custom_instructions
            )

            # Create campaign entity
            campaign = await self._create_campaign_entity(
                campaign_data, user_id, theme, difficulty, party_size, starting_level, duration
            )

            # Save campaign and components
            saved_campaign = await self.campaign_repo.save(campaign)

            # Update request with success
            await self.generation_repo.update_request_status(
                request_id, "completed", campaign_id=saved_campaign.id
            )

            logger.info(f"Campaign generation completed for request {request_id}")

        except Exception as e:
            logger.error(f"Campaign generation failed for request {request_id}: {e}")
            await self.generation_repo.update_request_status(
                request_id, "failed", error_message=str(e)
            )

    async def _generate_campaign_components(
        self,
        theme: CampaignTheme,
        difficulty: DifficultyLevel,
        party_size: PartySize,
        starting_level: int,
        duration: str,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate all campaign components"""
        # Generate campaign overview
        overview = await self.ai_service.generate_campaign_overview(
            theme=theme.value,
            difficulty=difficulty.value,
            party_size=party_size.value,
            starting_level=starting_level,
            duration=duration,
            custom_instructions=custom_instructions
        )

        # Generate world
        world = await self.ai_service.generate_world_setting(
            theme=theme.value,
            setting_type="medieval_fantasy",
            complexity="medium"
        )

        # Generate story hook
        hook = await self.ai_service.generate_story_hook(
            theme=theme.value,
            difficulty=difficulty.value,
            party_level=starting_level
        )

        # Generate story arcs
        arcs = await self.ai_service.generate_story_arcs(
            campaign_overview=overview,
            duration=duration
        )

        # Generate NPCs
        npcs = await self.ai_service.generate_npcs(
            count=5,
            campaign_context={"description": overview.get("description", ""), "theme": theme.value}
        )

        # Generate locations
        locations = await self.ai_service.generate_locations(
            count=4,
            campaign_context={"description": overview.get("description", ""), "theme": theme.value}
        )

        return {
            "overview": overview,
            "world": world,
            "hook": hook,
            "arcs": arcs,
            "npcs": npcs,
            "locations": locations
        }

    async def _create_campaign_entity(
        self,
        campaign_data: Dict[str, Any],
        user_id: UUID,
        theme: CampaignTheme,
        difficulty: DifficultyLevel,
        party_size: PartySize,
        starting_level: int,
        duration: str
    ) -> Campaign:
        """Create campaign entity from generated data"""
        # Create world entity
        world = World(
            id=uuid4(),
            name=campaign_data["world"].get("name", "Unknown World"),
            description=campaign_data["world"].get("description", ""),
            geography=campaign_data["world"].get("geography", {}),
            cultures=campaign_data["world"].get("cultures", []),
            magic_system=campaign_data["world"].get("magic_system", {}),
            factions=campaign_data["world"].get("factions", []),
            history=campaign_data["world"].get("history", ""),
            campaign_id=uuid4()  # Will be set when campaign is saved
        )

        # Create story hook
        hook = StoryHook(
            id=uuid4(),
            title=campaign_data["hook"].get("title", "Unknown Hook"),
            description=campaign_data["hook"].get("description", ""),
            hook_type=campaign_data["hook"].get("hook_type", "mysterious"),
            stakes=campaign_data["hook"].get("stakes", ""),
            complications=campaign_data["hook"].get("complications", []),
            campaign_id=uuid4()  # Will be set when campaign is saved
        )

        # Create story arcs
        arcs = []
        for i, arc_data in enumerate(campaign_data["arcs"]):
            arc = StoryArc(
                id=uuid4(),
                title=arc_data.get("title", f"Arc {i+1}"),
                description=arc_data.get("description", ""),
                acts=arc_data.get("acts", []),
                climax=arc_data.get("climax", ""),
                resolution=arc_data.get("resolution", ""),
                arc_order=i + 1,
                campaign_id=uuid4()  # Will be set when campaign is saved
            )
            arcs.append(arc)

        # Create NPCs
        npcs = []
        for npc_data in campaign_data["npcs"]:
            npc = NPC(
                id=uuid4(),
                name=npc_data.get("name", "Unknown NPC"),
                race=npc_data.get("race", "human"),
                character_class=npc_data.get("character_class", "commoner"),
                background=npc_data.get("background", "commoner"),
                personality=npc_data.get("personality", {}),
                motivation=npc_data.get("motivation", ""),
                role_in_story=npc_data.get("role_in_story", ""),
                campaign_id=uuid4()  # Will be set when campaign is saved
            )
            npcs.append(npc)

        # Create locations
        locations = []
        for location_data in campaign_data["locations"]:
            location = Location(
                id=uuid4(),
                name=location_data.get("name", "Unknown Location"),
                type=location_data.get("type", "town"),
                description=location_data.get("description", ""),
                significance=location_data.get("significance", ""),
                encounters=location_data.get("encounters", []),
                campaign_id=uuid4()  # Will be set when campaign is saved
            )
            locations.append(location)

        # Create campaign
        campaign = Campaign(
            id=uuid4(),
            name=campaign_data["overview"].get("name", "Unnamed Campaign"),
            description=campaign_data["overview"].get("description", ""),
            theme=theme,
            difficulty=difficulty,
            world=world,
            story_hook=hook,
            story_arcs=arcs,
            key_npcs=npcs,
            key_locations=locations,
            starting_level=starting_level,
            party_size=party_size,
            expected_duration=Duration(duration),
            quality_score=QualityScore(4.0),  # Placeholder quality score
            generated_at=datetime.utcnow(),
            user_preferences=None,
            status=GenerationStatus.COMPLETED,
            user_id=user_id
        )

        return campaign


class CampaignRetrievalServiceImpl(CampaignRetrievalService):
    """Implementation of campaign retrieval service"""

    def __init__(self, campaign_repo: CampaignRepository):
        self.campaign_repo = campaign_repo

    async def get_campaign(self, campaign_id: UUID, user_id: UUID) -> Campaign:
        """Retrieve a specific campaign"""
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        if campaign.user_id != user_id:
            raise ValueError("Access denied")

        return campaign

    async def list_user_campaigns(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List campaigns for a user"""
        campaigns = await self.campaign_repo.get_by_user_id(
            user_id, limit, offset, status_filter
        )
        total = await self.campaign_repo.count_by_user_id(user_id)

        return {
            "campaigns": campaigns,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def delete_campaign(self, campaign_id: UUID, user_id: UUID) -> bool:
        """Delete a campaign"""
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            return False

        if campaign.user_id != user_id:
            raise ValueError("Access denied")

        return await self.campaign_repo.delete(campaign_id)

    async def update_campaign(
        self,
        campaign_id: UUID,
        updates: Dict[str, Any],
        user_id: UUID
    ) -> Campaign:
        """Update campaign details"""
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        if campaign.user_id != user_id:
            raise ValueError("Access denied")

        return await self.campaign_repo.update(campaign_id, updates)
