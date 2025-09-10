"""
Domain Entities for the Campaign Generator
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .value_objects import (
    CampaignTheme, DifficultyLevel, PartySize, Duration,
    GenerationStatus, QualityScore, HookType, Race,
    CharacterClass, Background, LocationType, CharacterFocus,
    NPCStyle, GameplayBalance, StoryTone, PlayerPreferences
)


@dataclass
class Campaign:
    """Core campaign entity representing a generated D&D campaign"""
    id: UUID
    name: str
    description: str
    theme: CampaignTheme
    difficulty: DifficultyLevel
    world: 'World'
    story_hook: 'StoryHook'
    story_arcs: List['StoryArc']
    key_npcs: List['NPC']
    key_locations: List['Location']
    starting_level: int
    party_size: PartySize
    expected_duration: Duration
    quality_score: QualityScore
    generated_at: datetime
    user_preferences: Optional['UserPreferences']
    status: GenerationStatus
    user_id: UUID
    # Additional fields from the provided implementation
    sections: Optional[List['CampaignSection']] = None
    images: Optional[dict] = None
    metadata: Optional[dict] = None
    player_preferences: Optional[PlayerPreferences] = None

    def __post_init__(self):
        """Validate campaign data after initialization"""
        # Initialize default values for new fields
        if self.sections is None:
            self.sections = []
        if self.images is None:
            self.images = {}
        if self.metadata is None:
            self.metadata = {}

        self._validate()

    def _validate(self):
        """Validate campaign data integrity"""
        if not (1 <= self.starting_level <= 20):
            raise ValueError("Starting level must be between 1 and 20")

        if self.quality_score.value < 0 or self.quality_score.value > 5:
            raise ValueError("Quality score must be between 0 and 5")

        if len(self.story_arcs) < 1:
            raise ValueError("Campaign must have at least one story arc")

        if len(self.key_npcs) < 2:
            raise ValueError("Campaign must have at least 2 key NPCs")

        if len(self.key_locations) < 2:
            raise ValueError("Campaign must have at least 2 key locations")

        # Optional validation for new fields
        if self.sections:
            for section in self.sections:
                if not section.section_id or not section.title:
                    raise ValueError("All sections must have valid section_id and title")

    def is_complete(self) -> bool:
        """Check if campaign generation is complete"""
        return self.status == GenerationStatus.COMPLETED

    def calculate_difficulty_modifier(self) -> float:
        """Calculate difficulty modifier based on campaign parameters"""
        base_modifier = 1.0

        # Adjust for party size
        if self.party_size == PartySize.SOLO:
            base_modifier *= 0.7
        elif self.party_size == PartySize.LARGE:
            base_modifier *= 1.3

        # Adjust for difficulty
        difficulty_multipliers = {
            DifficultyLevel.EASY: 0.8,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 1.2,
            DifficultyLevel.DEADLY: 1.5
        }
        base_modifier *= difficulty_multipliers[self.difficulty]

        return base_modifier

    def get_estimated_session_count(self) -> int:
        """Get estimated number of sessions based on duration"""
        duration_sessions = {
            Duration.ONE_SHOT: 1,
            Duration.SHORT: 4,
            Duration.MEDIUM: 10,
            Duration.LONG: 18,
            Duration.EPIC: 30
        }
        return duration_sessions[self.expected_duration]

    def add_section(self, section: 'CampaignSection') -> None:
        """Add a section to the campaign"""
        self.sections.append(section)

    def get_section_by_id(self, section_id: str) -> Optional['CampaignSection']:
        """Get a section by its ID"""
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None

    def get_total_content_length(self) -> int:
        """Get the total content length of all sections"""
        return sum(section.get_content_length() for section in self.sections)

    def get_total_image_count(self) -> int:
        """Get the total number of images in all sections"""
        return sum(section.get_image_count() for section in self.sections)

    def has_cover_image(self) -> bool:
        """Check if the campaign has a cover image"""
        return "cover" in self.images and self.images["cover"] is not None

    def get_generation_metadata(self) -> dict:
        """Get generation metadata as a dictionary"""
        metadata = self.metadata.copy()
        if self.player_preferences:
            metadata["player_preferences"] = self.player_preferences.get_preference_summary()
        metadata["total_sections"] = len(self.sections)
        metadata["total_content_length"] = self.get_total_content_length()
        metadata["total_images"] = self.get_total_image_count()
        return metadata


@dataclass
class World:
    """World setting entity containing geography, cultures, and lore"""
    id: UUID
    name: str
    description: str
    geography: dict
    cultures: List[dict]
    magic_system: dict
    factions: List[dict]
    history: str
    campaign_id: UUID

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate world data"""
        if len(self.name.strip()) < 3:
            raise ValueError("World name must be at least 3 characters")

        if len(self.description.strip()) < 50:
            raise ValueError("World description must be at least 50 characters")

        if not self.geography:
            raise ValueError("World must have geography information")

        if not self.cultures:
            raise ValueError("World must have at least one culture")

    def get_major_regions(self) -> List[str]:
        """Get list of major geographical regions"""
        return self.geography.get('regions', [])

    def get_dominant_cultures(self) -> List[str]:
        """Get list of dominant cultures"""
        return [culture['name'] for culture in self.cultures[:3]]

    def get_magic_traditions(self) -> List[str]:
        """Get available magical traditions"""
        return self.magic_system.get('traditions', [])

    def has_active_conflicts(self) -> bool:
        """Check if world has active faction conflicts"""
        return any(faction.get('status') == 'conflicting'
                  for faction in self.factions)


@dataclass
class StoryHook:
    """Story hook entity representing the campaign's opening scenario"""
    id: UUID
    title: str
    description: str
    hook_type: HookType
    stakes: str
    complications: List[str]
    campaign_id: UUID

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.title.strip()) < 5:
            raise ValueError("Hook title must be at least 5 characters")

        if len(self.description.strip()) < 100:
            raise ValueError("Hook description must be at least 100 characters")

        if not self.stakes.strip():
            raise ValueError("Hook must have clear stakes")

        if len(self.complications) < 2:
            raise ValueError("Hook must have at least 2 complications")

    def get_complexity_score(self) -> int:
        """Calculate hook complexity based on complications"""
        return len(self.complications)

    def is_high_stakes(self) -> bool:
        """Check if hook involves high-stakes elements"""
        high_stakes_keywords = ['death', 'destruction', 'catastrophe', 'war', 'apocalypse']
        return any(keyword in self.stakes.lower() for keyword in high_stakes_keywords)


@dataclass
class StoryArc:
    """Story arc entity representing major plotlines"""
    id: UUID
    title: str
    description: str
    acts: List[dict]
    climax: str
    resolution: str
    arc_order: int
    campaign_id: UUID

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.title.strip()) < 5:
            raise ValueError("Arc title must be at least 5 characters")

        if len(self.acts) < 2:
            raise ValueError("Story arc must have at least 2 acts")

        if not self.climax.strip():
            raise ValueError("Story arc must have a climax")

        if not self.resolution.strip():
            raise ValueError("Story arc must have a resolution")

    def get_act_count(self) -> int:
        """Get number of acts in the story arc"""
        return len(self.acts)

    def is_main_plot(self) -> bool:
        """Check if this is the main story arc"""
        return self.arc_order == 1


@dataclass
class NPC:
    """Non-player character entity"""
    id: UUID
    name: str
    race: Race
    character_class: CharacterClass
    background: Background
    personality: dict
    motivation: str
    role_in_story: str
    campaign_id: UUID

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.name.strip()) < 2:
            raise ValueError("NPC name must be at least 2 characters")

        if not self.motivation.strip():
            raise ValueError("NPC must have a motivation")

        if not self.role_in_story.strip():
            raise ValueError("NPC must have a role in the story")

        required_personality_keys = ['traits', 'ideals', 'bonds', 'flaws']
        for key in required_personality_keys:
            if key not in self.personality:
                raise ValueError(f"NPC personality missing required key: {key}")

    def get_alignment(self) -> str:
        """Get NPC alignment from personality"""
        return self.personality.get('alignment', 'neutral')

    def is_antagonist(self) -> bool:
        """Check if NPC is an antagonist"""
        antagonist_keywords = ['enemy', 'villain', 'antagonist', 'rival']
        return any(keyword in self.role_in_story.lower() for keyword in antagonist_keywords)

    def get_combat_readiness(self) -> str:
        """Determine NPC's combat readiness"""
        if self.character_class in ['barbarian', 'fighter', 'paladin']:
            return 'high'
        elif self.character_class in ['wizard', 'sorcerer', 'druid']:
            return 'medium'
        else:
            return 'low'


@dataclass
class Location:
    """Location entity representing important places in the campaign"""
    id: UUID
    name: str
    type: LocationType
    description: str
    significance: str
    encounters: List[dict]
    campaign_id: UUID

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.name.strip()) < 3:
            raise ValueError("Location name must be at least 3 characters")

        if len(self.description.strip()) < 50:
            raise ValueError("Location description must be at least 50 characters")

        if not self.significance.strip():
            raise ValueError("Location must have significance")

    def has_combat_encounters(self) -> bool:
        """Check if location has combat encounters"""
        return any(encounter.get('type') == 'combat' for encounter in self.encounters)

    def has_social_encounters(self) -> bool:
        """Check if location has social encounters"""
        return any(encounter.get('type') == 'social' for encounter in self.encounters)

    def get_encounter_difficulty_range(self) -> tuple:
        """Get range of encounter difficulties"""
        difficulties = []
        for encounter in self.encounters:
            if 'difficulty' in encounter:
                difficulties.append(encounter['difficulty'])

        if not difficulties:
            return (None, None)

        return (min(difficulties), max(difficulties))


@dataclass
class CampaignSection:
    """A section of the generated campaign"""
    section_id: str
    title: str
    content: str
    images: List[dict] = None
    subsections: List['CampaignSection'] = None
    metadata: dict = None

    def __post_init__(self):
        """Initialize default values"""
        if self.images is None:
            self.images = []
        if self.subsections is None:
            self.subsections = []
        if self.metadata is None:
            self.metadata = {}

    def add_image(self, image: dict) -> None:
        """Add an image to this section"""
        self.images.append(image)

    def add_subsection(self, subsection: 'CampaignSection') -> None:
        """Add a subsection to this section"""
        self.subsections.append(subsection)

    def get_content_length(self) -> int:
        """Get the total content length including subsections"""
        total_length = len(self.content)
        for subsection in self.subsections:
            total_length += subsection.get_content_length()
        return total_length

    def get_image_count(self) -> int:
        """Get the total number of images including subsections"""
        total_images = len(self.images)
        for subsection in self.subsections:
            total_images += subsection.get_image_count()
        return total_images
