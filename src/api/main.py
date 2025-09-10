"""
FastAPI Application for Campaign Generator API
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from uuid import UUID

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
from domain.value_objects import CampaignTheme, DifficultyLevel, PartySize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Campaign Generator API",
    description="AI-powered D&D 5e campaign generation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection placeholders
# In a real implementation, these would be injected via dependency injection framework
generation_service: CampaignGenerationService = None
retrieval_service: CampaignRetrievalService = None


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "VALIDATION_ERROR",
                "message": str(e),
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": request.headers.get("timestamp", "")
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": request.headers.get("timestamp", "")
            }
        )


@app.post("/campaigns", response_model=Dict[str, Any])
async def generate_campaign(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a new D&D 5e campaign

    Request body should contain:
    - theme: Campaign theme (fantasy, horror, mystery, etc.)
    - difficulty: Difficulty level (easy, medium, hard, deadly)
    - party_size: Party size (solo, duo, small, medium, large)
    - starting_level: Starting character level (1-20)
    - duration: Campaign duration (one_shot, short, medium, long, epic)
    - custom_instructions: Optional custom instructions
    """
    try:
        # Validate required fields
        required_fields = ["theme", "difficulty", "party_size"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Parse and validate enums
        try:
            theme = CampaignTheme(request["theme"])
            difficulty = DifficultyLevel(request["difficulty"])
            party_size = PartySize(request["party_size"])
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")

        # Validate starting level
        starting_level = request.get("starting_level", 1)
        if not (1 <= starting_level <= 20):
            raise HTTPException(status_code=400, detail="Starting level must be between 1 and 20")

        # Validate duration
        duration = request.get("duration", "medium")
        valid_durations = ["one_shot", "short", "medium", "long", "epic"]
        if duration not in valid_durations:
            raise HTTPException(status_code=400, detail=f"Invalid duration: {duration}")

        # Get custom instructions
        custom_instructions = request.get("custom_instructions")

        # Mock user ID for now
        user_id = UUID("12345678-1234-5678-9012-123456789012")

        # Start campaign generation
        request_id = await generation_service.generate_campaign(
            theme=theme,
            difficulty=difficulty,
            party_size=party_size,
            starting_level=starting_level,
            duration=duration,
            user_id=user_id,
            custom_instructions=custom_instructions
        )

        return {
            "request_id": str(request_id),
            "status": "pending",
            "estimated_completion_time": 180,  # 3 minutes
            "message": f"Campaign generation started. Check status at /status/{request_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/campaigns", response_model=Dict[str, Any])
async def list_campaigns(
    limit: int = 20,
    offset: int = 0,
    status: str = None
) -> Dict[str, Any]:
    """List user's campaigns with pagination"""
    try:
        # Mock user ID for now
        user_id = UUID("12345678-1234-5678-9012-123456789012")

        result = await retrieval_service.list_user_campaigns(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status_filter=status
        )

        # Convert campaigns to dict format
        campaigns_data = []
        for campaign in result["campaigns"]:
            campaigns_data.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "description": campaign.description,
                "theme": campaign.theme.value,
                "difficulty": campaign.difficulty.value,
                "starting_level": campaign.starting_level,
                "party_size": campaign.party_size.value,
                "expected_duration": campaign.expected_duration.value,
                "quality_score": campaign.quality_score.value,
                "generated_at": campaign.generated_at.isoformat(),
                "status": campaign.status.value
            })

        return {
            "campaigns": campaigns_data,
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"]
        }

    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/campaigns/{campaign_id}", response_model=Dict[str, Any])
async def get_campaign(campaign_id: str) -> Dict[str, Any]:
    """Get detailed campaign information"""
    try:
        campaign_uuid = UUID(campaign_id)
        user_id = UUID("12345678-1234-5678-9012-123456789012")  # Mock user ID

        campaign = await retrieval_service.get_campaign(campaign_uuid, user_id)

        # Convert to response format
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "description": campaign.description,
            "theme": campaign.theme.value,
            "difficulty": campaign.difficulty.value,
            "world": {
                "name": campaign.world.name,
                "description": campaign.world.description,
                "geography": campaign.world.geography,
                "cultures": campaign.world.cultures,
                "magic_system": campaign.world.magic_system,
                "factions": campaign.world.factions,
                "history": campaign.world.history
            },
            "story_hook": {
                "title": campaign.story_hook.title,
                "description": campaign.story_hook.description,
                "hook_type": campaign.story_hook.hook_type,
                "stakes": campaign.story_hook.stakes,
                "complications": campaign.story_hook.complications
            },
            "story_arcs": [
                {
                    "title": arc.title,
                    "description": arc.description,
                    "acts": arc.acts,
                    "climax": arc.climax,
                    "resolution": arc.resolution
                }
                for arc in campaign.story_arcs
            ],
            "key_npcs": [
                {
                    "name": npc.name,
                    "race": npc.race,
                    "character_class": npc.character_class,
                    "background": npc.background,
                    "personality": npc.personality,
                    "motivation": npc.motivation,
                    "role_in_story": npc.role_in_story
                }
                for npc in campaign.key_npcs
            ],
            "key_locations": [
                {
                    "name": location.name,
                    "type": location.type,
                    "description": location.description,
                    "significance": location.significance,
                    "encounters": location.encounters
                }
                for location in campaign.key_locations
            ],
            "starting_level": campaign.starting_level,
            "party_size": campaign.party_size.value,
            "expected_duration": campaign.expected_duration.value,
            "quality_score": campaign.quality_score.value,
            "generated_at": campaign.generated_at.isoformat(),
            "status": campaign.status.value
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/status/{request_id}", response_model=Dict[str, Any])
async def get_generation_status(request_id: str) -> Dict[str, Any]:
    """Check the status of a campaign generation request"""
    try:
        request_uuid = UUID(request_id)

        status = await generation_service.get_generation_status(request_uuid)

        return {
            "request_id": request_id,
            "status": status["status"],
            "campaign_id": str(status["campaign_id"]) if status["campaign_id"] else None,
            "progress": 100 if status["status"] == "completed" else 50,  # Mock progress
            "error_message": status["error_message"],
            "completed_at": status["completed_at"]
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting generation status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


# Initialize services (placeholder for dependency injection)
def init_services():
    """Initialize services - placeholder for real implementation"""
    global generation_service, retrieval_service

    # This would be replaced with actual service initialization
    # using dependency injection framework
    generation_service = None  # Placeholder
    retrieval_service = None   # Placeholder


# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Campaign Generator API")
    init_services()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
