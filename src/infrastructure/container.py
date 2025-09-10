"""
Dependency Injection Container for the Campaign Generator
"""
import os
import logging
from typing import Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession

# Import domain service interfaces - using direct import to avoid conflicts
# These are abstract base classes, we don't need to instantiate them here
from abc import ABC
from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog
from services.campaign_generation_service import CompleteCampaignGenerationService
from services.campaign_service import CampaignRetrievalServiceImpl
from services.ai_service import ClaudeAIService
from services.pdf_service import EnhancedPDFGenerationService
from services.image_service import ImageGenerationService
from services.cache_service import ImageCacheService, ContentCacheService
from services.cursor_rules_service import CursorRulesService
from services.watchdog_service import WatchdogService
from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog
from infrastructure.repositories import (
    CampaignRepositoryImpl, GenerationRequestRepositoryImpl,
    ContentCacheRepositoryImpl, UserPreferencesRepositoryImpl
)
from .database import get_db_session

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Simple dependency injection container"""

    def __init__(self):
        self._services = {}
        self._session = None

    async def initialize(self):
        """Initialize the container and all services"""
        try:
            # Initialize database session
            async for session in get_db_session():
                self._session = session
                break

            # Initialize core services
            await self._initialize_core_services()
            await self._initialize_infrastructure_services()
            await self._initialize_domain_services()

            logger.info("Dependency container initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize dependency container: {e}")
            raise

    async def _initialize_core_services(self):
        """Initialize core AI and external services"""
        # Content Integrity Watchdog (must be initialized first for validation)
        self._services["content_integrity_watchdog"] = ContentIntegrityWatchdog(is_active=True)

        # Watchdog Service (must be initialized first)
        self._services["watchdog_service"] = WatchdogService()

        # Claude AI Service
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            self._services["claude_service"] = ClaudeAIService(
                claude_key,
                watchdog_service=self._services["watchdog_service"],
                content_integrity_watchdog=self._services["content_integrity_watchdog"]
            )
        else:
            logger.warning("ANTHROPIC_API_KEY not set, using mock Claude service")
            self._services["claude_service"] = ClaudeAIService(
                "mock-key",
                watchdog_service=self._services["watchdog_service"],
                content_integrity_watchdog=self._services["content_integrity_watchdog"]
            )

        # OpenAI DALL-E Service
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self._services["image_service"] = ImageGenerationService(openai_key)
        else:
            logger.warning("OPENAI_API_KEY not set, image generation will be disabled")
            self._services["image_service"] = None

    async def _initialize_infrastructure_services(self):
        """Initialize infrastructure services"""
        # Repositories
        if self._session:
            self._services["campaign_repo"] = CampaignRepositoryImpl(self._session)
            self._services["generation_repo"] = GenerationRequestRepositoryImpl(self._session)
            self._services["cache_repo"] = ContentCacheRepositoryImpl(self._session)
            self._services["preferences_repo"] = UserPreferencesRepositoryImpl(self._session)

        # Cache services
        self._services["image_cache"] = ImageCacheService()
        self._services["content_cache"] = ContentCacheService()

        # Enhanced PDF service
        self._services["pdf_service"] = EnhancedPDFGenerationService()

        # Validation service
        self._services["cursor_rules"] = CursorRulesService()

    async def _initialize_domain_services(self):
        """Initialize domain services"""
        # Campaign services
        self._services["campaign_generation"] = CompleteCampaignGenerationService(
            ai_service=self._services["claude_service"],
            image_service=self._services["image_service"],
            watchdog_service=self._services["watchdog_service"],
            content_cache=self._services["content_cache"],
            image_cache=self._services["image_cache"],
            content_integrity_watchdog=self._services["content_integrity_watchdog"]
        )

        self._services["campaign_retrieval"] = CampaignRetrievalServiceImpl(
            campaign_repo=self._services["campaign_repo"]
        )

    # Service getters
    @property
    def claude_service(self):
        return self._services.get("claude_service")

    @property
    def image_service(self):
        return self._services.get("image_service")

    @property
    def pdf_service(self):
        return self._services.get("pdf_service")

    @property
    def image_cache(self):
        return self._services.get("image_cache")

    @property
    def content_cache(self):
        return self._services.get("content_cache")

    @property
    def cursor_rules(self):
        return self._services.get("cursor_rules")

    @property
    def content_integrity_watchdog(self):
        return self._services.get("content_integrity_watchdog")

    @property
    def watchdog_service(self):
        return self._services.get("watchdog_service")

    @property
    def campaign_generation_service(self):
        return self._services.get("campaign_generation")

    @property
    def campaign_retrieval_service(self):
        return self._services.get("campaign_retrieval")

    def get_service(self, name: str):
        """Get a service by name"""
        return self._services.get(name)

    async def close(self):
        """Clean up resources"""
        if self._session:
            await self._session.close()

        # Close any services that need cleanup
        if self.image_service and hasattr(self.image_service, '__aexit__'):
            await self.image_service.__aexit__(None, None, None)


# Global container instance
_container: Optional[DependencyContainer] = None


async def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    global _container
    if _container is None:
        _container = await DependencyContainer().initialize()
    return _container


async def get_service(service_name: str):
    """Get a service from the global container"""
    container = await get_container()
    return container.get_service(service_name)


# Convenience functions for common services
async def get_claude_service():
    container = await get_container()
    return container.claude_service

async def get_image_service():
    container = await get_container()
    return container.image_service

async def get_pdf_service():
    container = await get_container()
    return container.pdf_service

async def get_campaign_generation_service():
    container = await get_container()
    return container.campaign_generation_service

async def get_content_integrity_watchdog():
    container = await get_container()
    return container.content_integrity_watchdog

async def get_watchdog_service():
    container = await get_container()
    return container.watchdog_service
