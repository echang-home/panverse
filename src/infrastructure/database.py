"""
Database configuration and models for the Campaign Generator
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Text, JSON, TIMESTAMP, UUID, ForeignKey, func
from typing import Optional, List
import uuid
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class CampaignModel(Base):
    """Database model for campaigns"""
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    world_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('worlds.id'))
    starting_level: Mapped[int] = mapped_column(Integer, nullable=False)
    party_size: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_duration: Mapped[str] = mapped_column(String(20), nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    generated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='generating')
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    world: Mapped[Optional["WorldModel"]] = relationship("WorldModel", back_populates="campaign", uselist=False)
    story_hooks: Mapped[List["StoryHookModel"]] = relationship("StoryHookModel", back_populates="campaign")
    story_arcs: Mapped[List["StoryArcModel"]] = relationship("StoryArcModel", back_populates="campaign")
    npcs: Mapped[List["NPCModel"]] = relationship("NPCModel", back_populates="campaign")
    locations: Mapped[List["LocationModel"]] = relationship("LocationModel", back_populates="campaign")


class WorldModel(Base):
    """Database model for worlds"""
    __tablename__ = "worlds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    geography: Mapped[Optional[dict]] = mapped_column(JSON)
    cultures: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    magic_system: Mapped[Optional[dict]] = mapped_column(JSON)
    factions: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    history: Mapped[Optional[str]] = mapped_column(Text)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="world")


class StoryHookModel(Base):
    """Database model for story hooks"""
    __tablename__ = "story_hooks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    hook_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stakes: Mapped[Optional[str]] = mapped_column(Text)
    complications: Mapped[Optional[List[str]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="story_hooks")


class StoryArcModel(Base):
    """Database model for story arcs"""
    __tablename__ = "story_arcs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    acts: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    climax: Mapped[Optional[str]] = mapped_column(Text)
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    arc_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="story_arcs")


class NPCModel(Base):
    """Database model for NPCs"""
    __tablename__ = "npcs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    race: Mapped[str] = mapped_column(String(50))
    character_class: Mapped[str] = mapped_column(String(50))
    background: Mapped[str] = mapped_column(String(50))
    personality: Mapped[Optional[dict]] = mapped_column(JSON)
    motivation: Mapped[Optional[str]] = mapped_column(Text)
    role_in_story: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="npcs")


class LocationModel(Base):
    """Database model for locations"""
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    significance: Mapped[Optional[str]] = mapped_column(Text)
    encounters: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="locations")


class GenerationRequestModel(Base):
    """Database model for generation requests"""
    __tablename__ = "generation_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    request_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    campaign: Mapped[Optional["CampaignModel"]] = relationship("CampaignModel")


class UserPreferencesModel(Base):
    """Database model for user preferences"""
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    preferred_themes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    preferred_difficulty: Mapped[Optional[str]] = mapped_column(String(20))
    preferred_setting: Mapped[Optional[str]] = mapped_column(String(50))
    custom_prompts: Mapped[Optional[List[str]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


# Database connection
DATABASE_URL = "postgresql+asyncpg://campaign_user:campaign_pass@localhost:5432/campaign_db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)


async def get_db_session() -> AsyncSession:
    """Get database session"""
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
