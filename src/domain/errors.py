"""
Domain Errors and Exceptions

This module defines custom exceptions and error handling for the Campaign Generator domain.
All exceptions follow clean architecture principles and provide meaningful error information.
"""

from typing import Dict, Any, Optional


class DomainError(Exception):
    """Base class for all domain-related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ValidationError(DomainError):
    """Raised when domain validation fails"""
    pass


class CampaignGenerationError(DomainError):
    """Raised when campaign generation fails"""
    pass


class AIIntegrationError(DomainError):
    """Raised when AI service integration fails"""
    pass


class ContentQualityError(DomainError):
    """Raised when content quality validation fails"""
    pass


class ResourceNotFoundError(DomainError):
    """Raised when a requested resource is not found"""
    pass


class ConfigurationError(DomainError):
    """Raised when configuration is invalid or missing"""
    pass


class ExternalServiceError(DomainError):
    """Raised when external service calls fail"""
    pass


class CacheError(DomainError):
    """Raised when caching operations fail"""
    pass


class PDFGenerationError(DomainError):
    """Raised when PDF generation fails"""
    pass


class ImageGenerationError(DomainError):
    """Raised when image generation fails"""
    pass


class PreferenceValidationError(ValidationError):
    """Raised when user preferences are invalid"""
    pass


class CampaignValidationError(ValidationError):
    """Raised when campaign data is invalid"""
    pass


class NPCValidationError(ValidationError):
    """Raised when NPC data is invalid"""
    pass


class LocationValidationError(ValidationError):
    """Raised when location data is invalid"""
    pass


class StoryValidationError(ValidationError):
    """Raised when story elements are invalid"""
    pass


class ClaudeAPIError(ExternalServiceError):
    """Raised when Claude API calls fail"""
    pass


class DALLAPIError(ExternalServiceError):
    """Raised when DALL-E API calls fail"""
    pass


class ChatGPTAPIError(ExternalServiceError):
    """Raised when ChatGPT API calls fail"""
    pass


class QualityThresholdError(ContentQualityError):
    """Raised when content quality falls below threshold"""
    pass


class FallbackDetectedError(ContentQualityError):
    """Raised when AI fallback content is detected"""
    pass


class PlaceholderContentError(ContentQualityError):
    """Raised when placeholder content is detected"""
    pass


class ContentIntegrityError(ContentQualityError):
    """Raised when content integrity validation fails"""
    pass


# Error handling utilities

def handle_domain_error(error: DomainError) -> Dict[str, Any]:
    """
    Handle domain errors and return appropriate response

    Args:
        error: The domain error to handle

    Returns:
        Dictionary with error response data
    """
    if isinstance(error, ValidationError):
        status_code = 400
    elif isinstance(error, ResourceNotFoundError):
        status_code = 404
    elif isinstance(error, ConfigurationError):
        status_code = 500
    elif isinstance(error, ExternalServiceError):
        status_code = 502
    else:
        status_code = 500

    return {
        "status_code": status_code,
        "error": error.to_dict()
    }


def create_error_response(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized error response

    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details

    Returns:
        Standardized error response dictionary
    """
    return {
        "error": error_type,
        "message": message,
        "details": details or {},
        "timestamp": "2024-01-01T00:00:00Z"  # Would be actual timestamp
    }


def validate_preferences(preferences: Any) -> None:
    """
    Validate user preferences

    Args:
        preferences: User preferences to validate

    Raises:
        PreferenceValidationError: If preferences are invalid
    """
    if not preferences:
        raise PreferenceValidationError("Preferences cannot be empty")

    # Validate theme if provided
    if hasattr(preferences, 'theme') and preferences.theme is not None:
        from .value_objects import CampaignTheme
        if not isinstance(preferences.theme, CampaignTheme):
            raise PreferenceValidationError("Invalid theme type")

    # Validate difficulty if provided
    if hasattr(preferences, 'difficulty') and preferences.difficulty is not None:
        from .value_objects import DifficultyLevel
        if not isinstance(preferences.difficulty, DifficultyLevel):
            raise PreferenceValidationError("Invalid difficulty type")

    # Validate specific elements if provided
    if hasattr(preferences, 'specific_elements') and preferences.specific_elements:
        if not isinstance(preferences.specific_elements, list):
            raise PreferenceValidationError("Specific elements must be a list")
        if len(preferences.specific_elements) > 10:
            raise PreferenceValidationError("Too many specific elements (max 10)")


def validate_campaign_data(campaign: Any) -> None:
    """
    Validate campaign data

    Args:
        campaign: Campaign data to validate

    Raises:
        CampaignValidationError: If campaign data is invalid
    """
    if not campaign:
        raise CampaignValidationError("Campaign cannot be empty")

    required_fields = ['id', 'name', 'description', 'theme', 'difficulty']
    for field in required_fields:
        if not hasattr(campaign, field) or getattr(campaign, field) is None:
            raise CampaignValidationError(f"Missing required field: {field}")

    # Validate starting level
    if hasattr(campaign, 'starting_level'):
        level = getattr(campaign, 'starting_level')
        if not isinstance(level, int) or not (1 <= level <= 20):
            raise CampaignValidationError("Starting level must be between 1 and 20")

    # Validate party size
    if hasattr(campaign, 'party_size'):
        from .value_objects import PartySize
        party_size = getattr(campaign, 'party_size')
        if not isinstance(party_size, PartySize):
            raise CampaignValidationError("Invalid party size")


def validate_content_quality(content: str, content_type: str, min_length: int = 50) -> None:
    """
    Validate content quality

    Args:
        content: Content to validate
        content_type: Type of content
        min_length: Minimum content length

    Raises:
        ContentQualityError: If content quality is insufficient
    """
    if not content or not content.strip():
        raise ContentQualityError(f"Empty {content_type} content")

    if len(content.strip()) < min_length:
        raise ContentQualityError(f"{content_type} content too short (minimum {min_length} characters)")

    # Check for placeholder content
    placeholder_patterns = ["[placeholder", "[insert", "PLACEHOLDER", "TODO:"]
    for pattern in placeholder_patterns:
        if pattern.lower() in content.lower():
            raise PlaceholderContentError(f"Placeholder content detected in {content_type}")

    # Check for fallback phrases
    fallback_phrases = [
        "I'm sorry, I cannot",
        "I apologize, but I",
        "I don't have enough information"
    ]
    for phrase in fallback_phrases:
        if phrase.lower() in content.lower():
            raise FallbackDetectedError(f"Fallback content detected in {content_type}")
