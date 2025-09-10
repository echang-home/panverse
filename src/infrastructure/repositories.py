"""
Repository implementations for data access
"""
from typing import List, Optional, Dict, Any
import uuid
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from domain.entities import Campaign, World, StoryHook, StoryArc, NPC, Location
from domain.repositories import (
    CampaignRepository, WorldRepository, StoryRepository,
    CharacterRepository, LocationRepository, GenerationRequestRepository,
    UserPreferencesRepository, ContentCacheRepository
)
from domain.value_objects import (
    CampaignTheme, DifficultyLevel, PartySize, Duration,
    GenerationStatus, QualityScore, HookType, Race,
    CharacterClass, Background, LocationType
)
from .database import (
    CampaignModel, WorldModel, StoryHookModel, StoryArcModel,
    NPCModel, LocationModel, GenerationRequestModel, UserPreferencesModel
)


class CampaignRepositoryImpl(CampaignRepository):
    """SQLAlchemy implementation of CampaignRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, campaign: Campaign) -> Campaign:
        """Save a campaign"""
        # Create database models
        campaign_model = CampaignModel(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            theme=campaign.theme.value,
            difficulty=campaign.difficulty.value,
            starting_level=campaign.starting_level,
            party_size=campaign.party_size.value,
            expected_duration=campaign.expected_duration.value,
            quality_score=campaign.quality_score.value,
            generated_at=campaign.generated_at,
            user_id=campaign.user_id,
            status=campaign.status.value
        )

        # Save world
        if campaign.world:
            world_model = WorldModel(
                id=campaign.world.id,
                name=campaign.world.name,
                description=campaign.world.description,
                geography=campaign.world.geography,
                cultures=campaign.world.cultures,
                magic_system=campaign.world.magic_system,
                factions=campaign.world.factions,
                history=campaign.world.history,
                campaign_id=campaign.id
            )
            campaign_model.world = world_model

        # Save story hook
        if campaign.story_hook:
            hook_model = StoryHookModel(
                id=campaign.story_hook.id,
                campaign_id=campaign.id,
                title=campaign.story_hook.title,
                description=campaign.story_hook.description,
                hook_type=campaign.story_hook.hook_type,
                stakes=campaign.story_hook.stakes,
                complications=campaign.story_hook.complications
            )
            campaign_model.story_hooks.append(hook_model)

        # Save story arcs
        for arc in campaign.story_arcs:
            arc_model = StoryArcModel(
                id=arc.id,
                campaign_id=campaign.id,
                title=arc.title,
                description=arc.description,
                acts=arc.acts,
                climax=arc.climax,
                resolution=arc.resolution,
                arc_order=arc.arc_order
            )
            campaign_model.story_arcs.append(arc_model)

        # Save NPCs
        for npc in campaign.key_npcs:
            npc_model = NPCModel(
                id=npc.id,
                campaign_id=campaign.id,
                name=npc.name,
                race=npc.race,
                character_class=npc.character_class,
                background=npc.background,
                personality=npc.personality,
                motivation=npc.motivation,
                role_in_story=npc.role_in_story
            )
            campaign_model.npcs.append(npc_model)

        # Save locations
        for location in campaign.key_locations:
            location_model = LocationModel(
                id=location.id,
                campaign_id=campaign.id,
                name=location.name,
                type=location.type.value,
                description=location.description,
                significance=location.significance,
                encounters=location.encounters
            )
            campaign_model.locations.append(location_model)

        self.session.add(campaign_model)
        await self.session.commit()
        await self.session.refresh(campaign_model)

        return campaign

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID"""
        stmt = select(CampaignModel).options(
            selectinload(CampaignModel.world),
            selectinload(CampaignModel.story_hooks),
            selectinload(CampaignModel.story_arcs),
            selectinload(CampaignModel.npcs),
            selectinload(CampaignModel.locations)
        ).where(CampaignModel.id == campaign_id)

        result = await self.session.execute(stmt)
        campaign_model = result.scalar_one_or_none()

        if not campaign_model:
            return None

        return self._model_to_entity(campaign_model)

    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> List[Campaign]:
        """Get campaigns by user ID"""
        stmt = select(CampaignModel).options(
            selectinload(CampaignModel.world),
            selectinload(CampaignModel.story_hooks),
            selectinload(CampaignModel.story_arcs),
            selectinload(CampaignModel.npcs),
            selectinload(CampaignModel.locations)
        ).where(CampaignModel.user_id == user_id)

        if status_filter:
            stmt = stmt.where(CampaignModel.status == status_filter)

        stmt = stmt.limit(limit).offset(offset).order_by(CampaignModel.created_at.desc())

        result = await self.session.execute(stmt)
        campaign_models = result.scalars().all()

        return [self._model_to_entity(model) for model in campaign_models]

    async def update(self, campaign_id: UUID, updates: Dict[str, Any]) -> Campaign:
        """Update a campaign"""
        stmt = (
            update(CampaignModel)
            .where(CampaignModel.id == campaign_id)
            .values(**updates)
        )
        await self.session.execute(stmt)
        await self.session.commit()

        # Return updated campaign
        return await self.get_by_id(campaign_id)

    async def delete(self, campaign_id: UUID) -> bool:
        """Delete a campaign"""
        stmt = delete(CampaignModel).where(CampaignModel.id == campaign_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count campaigns for a user"""
        stmt = select(func.count()).where(CampaignModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    def _model_to_entity(self, model: CampaignModel) -> Campaign:
        """Convert database model to domain entity"""
        # Convert world
        world = None
        if model.world:
            world = World(
                id=model.world.id,
                name=model.world.name,
                description=model.world.description,
                geography=model.world.geography or {},
                cultures=model.world.cultures or [],
                magic_system=model.world.magic_system or {},
                factions=model.world.factions or [],
                history=model.world.history,
                campaign_id=model.id
            )

        # Convert story hook
        story_hook = None
        if model.story_hooks:
            hook_model = model.story_hooks[0]  # Assuming one hook per campaign
            story_hook = StoryHook(
                id=hook_model.id,
                title=hook_model.title,
                description=hook_model.description,
                hook_type=hook_model.hook_type,
                stakes=hook_model.stakes,
                complications=hook_model.complications or [],
                campaign_id=model.id
            )

        # Convert story arcs
        story_arcs = []
        for arc_model in sorted(model.story_arcs, key=lambda x: x.arc_order):
            arc = StoryArc(
                id=arc_model.id,
                title=arc_model.title,
                description=arc_model.description,
                acts=arc_model.acts or [],
                climax=arc_model.climax,
                resolution=arc_model.resolution,
                arc_order=arc_model.arc_order,
                campaign_id=model.id
            )
            story_arcs.append(arc)

        # Convert NPCs
        npcs = []
        for npc_model in model.npcs:
            npc = NPC(
                id=npc_model.id,
                name=npc_model.name,
                race=npc_model.race,
                character_class=npc_model.character_class,
                background=npc_model.background,
                personality=npc_model.personality or {},
                motivation=npc_model.motivation,
                role_in_story=npc_model.role_in_story,
                campaign_id=model.id
            )
            npcs.append(npc)

        # Convert locations
        locations = []
        for location_model in model.locations:
            location = Location(
                id=location_model.id,
                name=location_model.name,
                type=location_model.type,
                description=location_model.description,
                significance=location_model.significance,
                encounters=location_model.encounters or [],
                campaign_id=model.id
            )
            locations.append(location)

        return Campaign(
            id=model.id,
            name=model.name,
            description=model.description,
            theme=CampaignTheme(model.theme),
            difficulty=DifficultyLevel(model.difficulty),
            world=world,
            story_hook=story_hook,
            story_arcs=story_arcs,
            key_npcs=npcs,
            key_locations=locations,
            starting_level=model.starting_level,
            party_size=PartySize(model.party_size),
            expected_duration=Duration(model.expected_duration),
            quality_score=QualityScore(model.quality_score or 4.0),
            generated_at=model.generated_at,
            user_preferences=None,  # Not loaded in this implementation
            status=GenerationStatus(model.status),
            user_id=model.user_id
        )


class GenerationRequestRepositoryImpl(GenerationRequestRepository):
    """SQLAlchemy implementation of GenerationRequestRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(self, user_id: UUID, request_data: Dict[str, Any]) -> UUID:
        """Create a new generation request"""
        request_id = UUID(str(uuid.uuid4()))
        request_model = GenerationRequestModel(
            id=request_id,
            user_id=user_id,
            request_data=request_data,
            status="pending"
        )

        self.session.add(request_model)
        await self.session.commit()

        return request_id

    async def get_request(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """Get generation request by ID"""
        stmt = select(GenerationRequestModel).where(GenerationRequestModel.id == request_id)
        result = await self.session.execute(stmt)
        request_model = result.scalar_one_or_none()

        if not request_model:
            return None

        return {
            "id": str(request_model.id),
            "user_id": str(request_model.user_id),
            "request_data": request_model.request_data,
            "status": request_model.status,
            "campaign_id": str(request_model.campaign_id) if request_model.campaign_id else None,
            "error_message": request_model.error_message,
            "started_at": request_model.started_at.isoformat() if request_model.started_at else None,
            "completed_at": request_model.completed_at.isoformat() if request_model.completed_at else None,
            "created_at": request_model.created_at.isoformat()
        }

    async def update_request_status(
        self,
        request_id: UUID,
        status: str,
        campaign_id: Optional[UUID] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update generation request status"""
        update_data = {"status": status}

        if campaign_id:
            update_data["campaign_id"] = campaign_id

        if error_message:
            update_data["error_message"] = error_message

        if status == "processing":
            update_data["started_at"] = func.now()
        elif status in ["completed", "failed"]:
            update_data["completed_at"] = func.now()

        stmt = (
            update(GenerationRequestModel)
            .where(GenerationRequestModel.id == request_id)
            .values(**update_data)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def get_pending_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending generation requests for processing"""
        stmt = (
            select(GenerationRequestModel)
            .where(GenerationRequestModel.status == "pending")
            .limit(limit)
            .order_by(GenerationRequestModel.created_at)
        )

        result = await self.session.execute(stmt)
        request_models = result.scalars().all()

        return [
            {
                "id": str(model.id),
                "user_id": str(model.user_id),
                "request_data": model.request_data,
                "status": model.status,
                "campaign_id": str(model.campaign_id) if model.campaign_id else None,
                "error_message": model.error_message,
                "started_at": model.started_at.isoformat() if model.started_at else None,
                "completed_at": model.completed_at.isoformat() if model.completed_at else None,
                "created_at": model.created_at.isoformat()
            }
            for model in request_models
        ]


# Placeholder implementations for other repositories
class WorldRepositoryImpl(WorldRepository):
    """Placeholder implementation of WorldRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, world: World) -> World:
        """Save a world"""
        # Implementation would go here
        return world

    async def get_by_campaign_id(self, campaign_id: UUID) -> Optional[World]:
        """Get world by campaign ID"""
        # Implementation would go here
        return None

    async def update(self, world_id: UUID, updates: Dict[str, Any]) -> World:
        """Update a world"""
        # Implementation would go here
        pass


class StoryRepositoryImpl(StoryRepository):
    """Placeholder implementation of StoryRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_hook(self, hook: StoryHook) -> StoryHook:
        """Save a story hook"""
        return hook

    async def save_arc(self, arc: StoryArc) -> StoryArc:
        """Save a story arc"""
        return arc

    async def get_hooks_by_campaign_id(self, campaign_id: UUID) -> List[StoryHook]:
        """Get story hooks by campaign ID"""
        return []

    async def get_arcs_by_campaign_id(self, campaign_id: UUID) -> List[StoryArc]:
        """Get story arcs by campaign ID"""
        return []


class CharacterRepositoryImpl(CharacterRepository):
    """Placeholder implementation of CharacterRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_npc(self, npc: NPC) -> NPC:
        """Save an NPC"""
        return npc

    async def get_npcs_by_campaign_id(self, campaign_id: UUID) -> List[NPC]:
        """Get NPCs by campaign ID"""
        return []

    async def update_npc(self, npc_id: UUID, updates: Dict[str, Any]) -> NPC:
        """Update an NPC"""
        pass


class LocationRepositoryImpl(LocationRepository):
    """Placeholder implementation of LocationRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_location(self, location: Location) -> Location:
        """Save a location"""
        return location

    async def get_locations_by_campaign_id(self, campaign_id: UUID) -> List[Location]:
        """Get locations by campaign ID"""
        return []

    async def update_location(self, location_id: UUID, updates: Dict[str, Any]) -> Location:
        """Update a location"""
        pass


class ContentCacheRepositoryImpl(ContentCacheRepository):
    """Placeholder implementation of ContentCacheRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached content"""
        return None

    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Set cached content with TTL"""
        return True

    async def delete(self, key: str) -> bool:
        """Delete cached content"""
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return False


class UserPreferencesRepositoryImpl(UserPreferencesRepository):
    """Placeholder implementation of UserPreferencesRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user preferences by user ID"""
        return None

    async def save(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Save user preferences"""
        return preferences

    async def update(self, user_id: UUID, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        return updates

    async def delete(self, user_id: UUID) -> bool:
        """Delete user preferences"""
        return True
