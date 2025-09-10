"""
Value Objects for the Campaign Generator Domain
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List


class CampaignTheme(Enum):
    """Campaign theme enumeration"""
    FANTASY = "fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    EXPLORATION = "exploration"
    POLITICAL_INTRIGUE = "political_intrigue"
    WAR = "war"
    SUPERNATURAL = "supernatural"
    CUSTOM = "custom"


class DifficultyLevel(Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"


class PartySize(Enum):
    """Party size enumeration"""
    SOLO = "solo"
    DUO = "duo"
    SMALL = "small"  # 3-4 players
    MEDIUM = "medium"  # 5-6 players
    LARGE = "large"  # 7+ players


class Duration(Enum):
    """Campaign duration enumeration"""
    ONE_SHOT = "one_shot"
    SHORT = "short"  # 3-5 sessions
    MEDIUM = "medium"  # 6-12 sessions
    LONG = "long"  # 13-20 sessions
    EPIC = "epic"  # 20+ sessions


class GenerationStatus(Enum):
    """Generation status enumeration"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATING = "validating"


class HookType(Enum):
    """Story hook type enumeration"""
    PERSONAL = "personal"
    MYSTERIOUS = "mysterious"
    THREATENING = "threatening"
    OPPORTUNITY = "opportunity"
    COSMIC = "cosmic"


class Race(Enum):
    """Character race enumeration"""
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    DRAGONBORN = "dragonborn"
    TIEFLING = "tiefling"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    GNOME = "gnome"


class CharacterClass(Enum):
    """Character class enumeration"""
    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"


class Background(Enum):
    """Character background enumeration"""
    ACOLYTE = "acolyte"
    CRIMINAL = "criminal"
    ENTERTAINER = "entertainer"
    FOLK_HERO = "folk_hero"
    GUILD_ARTISAN = "guild_artisan"
    HERMIT = "hermit"
    NOBLE = "noble"
    OUTLANDER = "outlander"
    SAGE = "sage"
    SAILOR = "sailor"
    SOLDIER = "soldier"
    URCHIN = "urchin"


class LocationType(Enum):
    """Location type enumeration"""
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    COAST = "coast"
    UNDERWATER = "underwater"
    PLANAR = "planar"


class SettingType(Enum):
    """Campaign setting type enumeration"""
    MEDIEVAL_FANTASY = "medieval_fantasy"
    DARK_FANTASY = "dark_fantasy"
    HIGH_FANTASY = "high_fantasy"
    URBAN_FANTASY = "urban_fantasy"
    POST_APOCALYPTIC = "post_apocalyptic"
    STEAMPUNK = "steampunk"
    CYBERPUNK = "cyberpunk"


class CharacterFocus(Enum):
    """Character focus options for campaign generation"""
    COMBAT = "combat"
    SOCIAL = "social"
    MAGIC = "magic"
    STEALTH = "stealth"
    BALANCED = "balanced"


class NPCStyle(Enum):
    """NPC relationship styles for campaign generation"""
    FRIENDLY = "friendly"
    HOSTILE = "hostile"
    COMPLEX = "complex"
    NEUTRAL = "neutral"


class GameplayBalance(Enum):
    """Gameplay balance options for campaign generation"""
    COMBAT_HEAVY = "combat_heavy"
    SOCIAL_HEAVY = "social_heavy"
    BALANCED = "balanced"


class StoryTone(Enum):
    """Story tone options for campaign generation"""
    DARK = "dark"
    LIGHT = "light"
    GRITTY = "gritty"
    WHIMSICAL = "whimsical"


@dataclass(frozen=True)
class QualityScore:
    """Value object representing content quality score"""
    value: float

    def __post_init__(self):
        if not (0 <= self.value <= 5):
            raise ValueError("Quality score must be between 0 and 5")

    @property
    def is_excellent(self) -> bool:
        """Check if quality is excellent"""
        return self.value >= 4.5

    @property
    def is_good(self) -> bool:
        """Check if quality is good"""
        return self.value >= 3.5

    @property
    def is_acceptable(self) -> bool:
        """Check if quality is acceptable"""
        return self.value >= 2.5

    @property
    def needs_improvement(self) -> bool:
        """Check if quality needs improvement"""
        return self.value < 2.5


@dataclass(frozen=True)
class UserPreferences:
    """Value object representing user preferences for campaign generation"""
    id: str
    user_id: str
    preferred_themes: List[CampaignTheme]
    preferred_difficulty: DifficultyLevel
    preferred_setting: SettingType
    custom_prompts: List[str]
    created_at: str
    updated_at: str

    def has_preferred_theme(self, theme: CampaignTheme) -> bool:
        """Check if user prefers a specific theme"""
        return theme in self.preferred_themes

    def get_theme_weight(self, theme: CampaignTheme) -> float:
        """Get preference weight for a theme"""
        if theme in self.preferred_themes:
            return 1.2  # 20% boost for preferred themes
        return 1.0


@dataclass
class PlayerPreferences:
    """Player preferences for interactive campaign generation"""
    theme: Optional[CampaignTheme] = None
    difficulty: Optional[DifficultyLevel] = None
    setting: Optional[SettingType] = None
    character_focus: Optional[CharacterFocus] = None
    npc_style: Optional[NPCStyle] = None
    gameplay_balance: Optional[GameplayBalance] = None
    story_length: Optional[Duration] = None  # Using existing Duration enum
    story_tone: Optional[StoryTone] = None
    specific_elements: list[str] = None
    freeform_input: Optional[str] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.specific_elements is None:
            self.specific_elements = []

    def has_preferences(self) -> bool:
        """Check if any preferences are set"""
        return any([
            self.theme is not None,
            self.difficulty is not None,
            self.setting is not None,
            self.character_focus is not None,
            self.npc_style is not None,
            self.gameplay_balance is not None,
            self.story_length is not None,
            self.story_tone is not None,
            len(self.specific_elements) > 0,
            self.freeform_input is not None
        ])

    def get_preference_summary(self) -> Dict[str, Any]:
        """Get a summary of set preferences"""
        summary = {}
        if self.theme:
            summary["theme"] = self.theme.value
        if self.difficulty:
            summary["difficulty"] = self.difficulty.value
        if self.setting:
            summary["setting"] = self.setting.value
        if self.character_focus:
            summary["character_focus"] = self.character_focus.value
        if self.npc_style:
            summary["npc_style"] = self.npc_style.value
        if self.gameplay_balance:
            summary["gameplay_balance"] = self.gameplay_balance.value
        if self.story_length:
            summary["story_length"] = self.story_length.value
        if self.story_tone:
            summary["story_tone"] = self.story_tone.value
        if self.specific_elements:
            summary["specific_elements"] = self.specific_elements
        if self.freeform_input:
            summary["freeform_input"] = self.freeform_input
        return summary


@dataclass(frozen=True)
class CampaignRequest:
    """Value object representing a campaign generation request"""
    theme: CampaignTheme
    difficulty: DifficultyLevel
    party_size: PartySize
    starting_level: int
    duration: Duration
    custom_theme: str = ""
    setting: SettingType = SettingType.MEDIEVAL_FANTASY
    user_prompt: str = ""

    def __post_init__(self):
        """Validate campaign request"""
        if not (1 <= self.starting_level <= 20):
            raise ValueError("Starting level must be between 1 and 20")

        if self.custom_theme and len(self.custom_theme.strip()) > 100:
            raise ValueError("Custom theme must be 100 characters or less")

        if self.user_prompt and len(self.user_prompt.strip()) > 500:
            raise ValueError("User prompt must be 500 characters or less")

    def get_generation_complexity(self) -> float:
        """Calculate generation complexity score"""
        complexity = 1.0

        # Duration affects complexity
        duration_multipliers = {
            Duration.ONE_SHOT: 0.8,
            Duration.SHORT: 1.0,
            Duration.MEDIUM: 1.2,
            Duration.LONG: 1.4,
            Duration.EPIC: 1.6
        }
        complexity *= duration_multipliers[self.duration]

        # Difficulty affects complexity
        difficulty_multipliers = {
            DifficultyLevel.EASY: 0.9,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 1.1,
            DifficultyLevel.DEADLY: 1.2
        }
        complexity *= difficulty_multipliers[self.difficulty]

        # Custom elements increase complexity
        if self.custom_theme:
            complexity *= 1.1
        if self.user_prompt:
            complexity *= 1.1

        return complexity


# Validation-related value objects for CursorRules

class RuleCategory(Enum):
    """Categories of D&D 5e rules for validation"""
    SPELLS = "spells"
    MONSTERS = "monsters"
    ITEMS = "items"
    CLASSES = "classes"
    RACES = "races"
    EQUIPMENT = "equipment"
    MECHANICS = "mechanics"


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Status of rule validation"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation issue found during content validation"""
    message: str
    category: RuleCategory
    severity: ValidationSeverity
    context: Dict[str, Any]
    suggestion: str = ""

    def __post_init__(self):
        """Validate validation issue data"""
        if not self.message.strip():
            raise ValueError("Validation issue message cannot be empty")

        if not isinstance(self.context, dict):
            raise ValueError("Context must be a dictionary")

    def is_critical(self) -> bool:
        """Check if this is a critical issue"""
        return self.severity == ValidationSeverity.CRITICAL

    def is_error(self) -> bool:
        """Check if this is an error-level issue"""
        return self.severity == ValidationSeverity.ERROR

    def is_warning(self) -> bool:
        """Check if this is a warning-level issue"""
        return self.severity == ValidationSeverity.WARNING


@dataclass(frozen=True)
class ValidationResult:
    """Result of content validation against D&D 5e rules"""
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: list[ValidationIssue]
    validated_section: str
    component_scores: Dict[str, float]

    def __post_init__(self):
        """Validate validation result data"""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("Validation score must be between 0.0 and 1.0")

        if not self.validated_section.strip():
            raise ValueError("Validated section cannot be empty")

    def get_critical_issues(self) -> list[ValidationIssue]:
        """Get all critical issues"""
        return [issue for issue in self.issues if issue.is_critical()]

    def get_error_issues(self) -> list[ValidationIssue]:
        """Get all error-level issues"""
        return [issue for issue in self.issues if issue.is_error()]

    def get_warning_issues(self) -> list[ValidationIssue]:
        """Get all warning-level issues"""
        return [issue for issue in self.issues if issue.is_warning()]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues"""
        return len(self.get_critical_issues()) > 0

    def get_overall_severity(self) -> ValidationSeverity:
        """Get the overall severity of all issues"""
        if self.has_critical_issues():
            return ValidationSeverity.CRITICAL
        elif self.get_error_issues():
            return ValidationSeverity.ERROR
        elif self.get_warning_issues():
            return ValidationSeverity.WARNING
        else:
            return ValidationSeverity.INFO
