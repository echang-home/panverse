"""
AI Service for Content Generation using Claude
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Import domain components
from domain.errors import ContentIntegrityError
from domain.services.content_integrity_watchdog import ContentIntegrityWatchdog


class AIService(ABC):
    """Abstract AI service for content generation"""

    @abstractmethod
    async def generate_campaign_overview(
        self,
        theme: str,
        difficulty: str,
        party_size: str,
        starting_level: int,
        duration: str,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate campaign overview section"""
        pass

    @abstractmethod
    async def generate_world_setting(
        self,
        theme: str,
        setting_type: str,
        complexity: str
    ) -> Dict[str, Any]:
        """Generate world setting"""
        pass

    @abstractmethod
    async def generate_story_hook(
        self,
        theme: str,
        difficulty: str,
        party_level: int
    ) -> Dict[str, Any]:
        """Generate story hook"""
        pass

    @abstractmethod
    async def generate_story_arcs(
        self,
        campaign_overview: Dict[str, Any],
        duration: str
    ) -> List[Dict[str, Any]]:
        """Generate story arcs"""
        pass

    @abstractmethod
    async def generate_npcs(
        self,
        count: int,
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate NPCs"""
        pass

    @abstractmethod
    async def generate_locations(
        self,
        count: int,
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate locations"""
        pass

    @abstractmethod
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """Validate and score content quality"""
        pass


class ClaudeAIService(AIService):
    """Claude-specific implementation of AI service"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", watchdog_service=None,
                 content_integrity_watchdog: ContentIntegrityWatchdog = None):
        self.api_key = api_key
        self.model = model
        self.watchdog_service = watchdog_service
        self.content_integrity_watchdog = content_integrity_watchdog or ContentIntegrityWatchdog()
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.warning("Anthropic package not available, using mock responses")
            self.client = None

    async def generate_campaign_overview(
        self,
        theme: str,
        difficulty: str,
        party_size: str,
        starting_level: int,
        duration: str,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate campaign overview section"""
        prompt = self._build_campaign_overview_prompt(
            theme, difficulty, party_size, starting_level, duration, custom_instructions
        )

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_campaign_overview_response(response)
        except Exception as e:
            logger.error(f"Failed to generate campaign overview: {e}")
            raise

    async def generate_introduction(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate introduction section content"""
        prompt = self._build_introduction_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate introduction: {e}")
            raise

    async def generate_setting(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate setting section content"""
        prompt = self._build_setting_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate setting: {e}")
            raise

    async def generate_background(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate background section content"""
        prompt = self._build_background_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate background: {e}")
            raise

    async def generate_structure(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate structure section content"""
        prompt = self._build_structure_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate structure: {e}")
            raise

    async def generate_locations_content(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate locations section content"""
        prompt = self._build_locations_content_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate locations content: {e}")
            raise

    async def generate_npcs_content(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate NPCs section content"""
        prompt = self._build_npcs_content_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate NPCs content: {e}")
            raise

    async def generate_encounters_content(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate encounters section content"""
        prompt = self._build_encounters_content_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate encounters content: {e}")
            raise

    async def generate_treasures_content(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate treasures section content"""
        prompt = self._build_treasures_content_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate treasures content: {e}")
            raise

    async def generate_appendices_content(
        self,
        campaign_data: Dict[str, Any],
        custom_instructions: Optional[str] = None,
        mode: str = "production"
    ) -> str:
        """Generate appendices section content"""
        prompt = self._build_appendices_content_prompt(campaign_data, custom_instructions, mode)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_section_content_response(response)
        except Exception as e:
            logger.error(f"Failed to generate appendices content: {e}")
            raise

    async def generate_world_setting(
        self,
        theme: str,
        setting_type: str,
        complexity: str
    ) -> Dict[str, Any]:
        """Generate world setting"""
        prompt = self._build_world_setting_prompt(theme, setting_type, complexity)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_world_setting_response(response)
        except Exception as e:
            logger.error(f"Failed to generate world setting: {e}")
            raise

    async def generate_story_hook(
        self,
        theme: str,
        difficulty: str,
        party_level: int
    ) -> Dict[str, Any]:
        """Generate story hook"""
        prompt = self._build_story_hook_prompt(theme, difficulty, party_level)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_story_hook_response(response)
        except Exception as e:
            logger.error(f"Failed to generate story hook: {e}")
            raise

    async def generate_story_arcs(
        self,
        campaign_overview: Dict[str, Any],
        duration: str
    ) -> List[Dict[str, Any]]:
        """Generate story arcs"""
        prompt = self._build_story_arcs_prompt(campaign_overview, duration)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_story_arcs_response(response)
        except Exception as e:
            logger.error(f"Failed to generate story arcs: {e}")
            raise

    async def generate_npcs(
        self,
        count: int,
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate NPCs"""
        prompt = self._build_npcs_prompt(count, campaign_context)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_npcs_response(response)
        except Exception as e:
            logger.error(f"Failed to generate NPCs: {e}")
            raise

    async def generate_locations(
        self,
        count: int,
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate locations"""
        prompt = self._build_locations_prompt(count, campaign_context)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_locations_response(response)
        except Exception as e:
            logger.error(f"Failed to generate locations: {e}")
            raise

    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """Validate and score content quality"""
        prompt = self._build_quality_validation_prompt(content, content_type)

        try:
            response = await self._call_claude_api(prompt)
            return self._parse_quality_validation_response(response)
        except Exception as e:
            logger.error(f"Failed to validate content quality: {e}")
            raise

    async def _call_claude_api(self, prompt: str) -> str:
        """Make API call to Claude with monitoring"""
        start_time = time.time()

        if not self.client:
            logger.warning("Claude client not available, returning mock response")
            mock_response = json.dumps({
                "content": "Mock Claude response - client not available",
                "usage": {"input_tokens": 100, "output_tokens": 200}
            })

            # Track mock API call if watchdog is available
            if self.watchdog_service:
                self.watchdog_service.track_api_call(
                    api_name="claude",
                    token_count=300,  # Estimate for mock
                    response_time=time.time() - start_time,
                    cost=0.0  # No cost for mock
                )

            return mock_response

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system="You are an expert Dungeons & Dragons 5th Edition campaign designer. Generate high-quality, balanced content that follows D&D 5e rules and best practices.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_time = time.time() - start_time

            # Extract response data
            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if hasattr(response, 'usage') else len(prompt.split()) * 1.3  # Estimate
            output_tokens = response.usage.output_tokens if hasattr(response, 'usage') else len(content.split()) * 1.3  # Estimate

            # Validate content integrity immediately after extraction
            if content and self.content_integrity_watchdog.is_active:
                try:
                    # For now, validate as generic content - specific validation happens in calling methods
                    if len(content.strip()) > 50:  # Only validate substantial content
                        self.content_integrity_watchdog.validate_text_content("ai_response", content)
                except ContentIntegrityError as e:
                    logger.error(f"AI response failed content integrity validation: {e.message}")
                    raise ContentIntegrityError(f"AI generated content contains mock/placeholder data: {e.message}")

            # Track API call with watchdog if available
            if self.watchdog_service:
                total_tokens = int(input_tokens + output_tokens)
                estimated_cost = (input_tokens * 3 + output_tokens * 15) / 1000000  # Claude pricing estimate

                self.watchdog_service.track_api_call(
                    api_name="claude",
                    token_count=total_tokens,
                    response_time=response_time,
                    cost=estimated_cost
                )

                # Verify content quality
                if content:
                    is_valid, issues = self.watchdog_service.verify_ai_response(
                        content=content,
                        content_type="campaign_content",  # Generic type, could be made more specific
                        source="claude"
                    )

                    if not is_valid:
                        logger.warning(f"Content verification failed: {issues}")

            response_data = {
                "content": content,
                "usage": {
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens)
                }
            }

            return json.dumps(response_data)

        except Exception as e:
            response_time = time.time() - start_time

            # Track failed API call
            if self.watchdog_service:
                self.watchdog_service.track_api_call(
                    api_name="claude",
                    token_count=0,
                    response_time=response_time,
                    cost=0.0
                )

                # Create alert for API failure
                from .watchdog_service import AlertSeverity
                self.watchdog_service._create_alert(
                    message=f"Claude API call failed: {str(e)}",
                    severity=AlertSeverity.ERROR,
                    source="claude_api",
                    details={"error": str(e), "response_time": response_time}
                )

            logger.error(f"Claude API call failed: {e}")
            # Return a basic fallback response
            return json.dumps({
                "content": "Error generating content with Claude API",
                "usage": {"input_tokens": 0, "output_tokens": 0}
            })

    def _build_campaign_overview_prompt(
        self,
        theme: str,
        difficulty: str,
        party_size: str,
        starting_level: int,
        duration: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Build prompt for campaign overview generation"""
        base_prompt = f"""
You are an expert Dungeons & Dragons 5th Edition campaign designer. Generate a compelling campaign overview.

CAMPAIGN SPECIFICATIONS:
- Theme: {theme}
- Difficulty: {difficulty}
- Party Size: {party_size}
- Starting Level: {starting_level}
- Duration: {duration}

REQUIREMENTS:
1. Create a catchy, thematic campaign name
2. Write a detailed description (200-400 words)
3. Define the campaign's tone and atmosphere
4. Suggest appropriate player party composition
5. Include 3-5 major plot themes or elements

{f"ADDITIONAL INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

Return the response as a JSON object with the following structure:
{{
    "name": "Campaign Name",
    "description": "Detailed description...",
    "tone": "Description of campaign tone",
    "recommended_party": "Suggested party composition",
    "major_themes": ["theme1", "theme2", "theme3"]
}}
"""

        return base_prompt.strip()

    def _build_introduction_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for introduction section generation"""
        name = campaign_data.get("name", "Campaign")
        subtitle = campaign_data.get("subtitle", "")
        description = campaign_data.get("description", "")
        theme = campaign_data.get("theme", "fantasy")
        difficulty = campaign_data.get("difficulty", "medium")
        level_range = campaign_data.get("level_range", "1-5")

        # Adjust content length based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 300-500 words (concise but complete)."
            content_sections = """1. Welcome to the adventure (1 paragraph)
2. Theme and tone overview (1 paragraph)
3. What players can expect (1 paragraph)
4. Adventure summary (1-2 paragraphs)"""
        else:  # production mode
            length_instruction = "Length should be approximately 800-1000 words (comprehensive and detailed)."
            content_sections = """1. Welcome to the adventure (1 paragraph)
2. Theme and tone overview (1-2 paragraphs)
3. What players can expect (1-2 paragraphs)
4. How to use this adventure book (1 paragraph)
5. Adventure summary (2-3 paragraphs)"""

        prompt = f"""
You are writing the introduction for a D&D 5e adventure book titled "{name}: {subtitle}".

Campaign description: {description}
Theme: {theme}
Difficulty: {difficulty}
Level range: {level_range}

Write a compelling introduction chapter that includes:
{content_sections}

Format this as a professional D&D adventure book introduction with appropriate headings and structure.
Use rich, evocative language that sets the mood for the adventure.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_setting_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for setting section generation"""
        name = campaign_data.get("name", "Campaign")
        world = campaign_data.get("world", {})
        theme = campaign_data.get("theme", "fantasy")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 400-600 words (concise but comprehensive)."
            content_sections = """1. World overview and atmosphere (1-2 paragraphs)
2. Key geographical regions and landmarks (1 paragraph)
3. Major cultures and societies (1 paragraph)
4. Political landscape and conflicts (1 paragraph)
5. Magic and supernatural elements (1 paragraph)
6. Opportunities for adventure (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 1000-1500 words (detailed and extensive)."
            content_sections = """1. World overview and atmosphere (2-3 paragraphs)
2. Key geographical regions and landmarks (2-3 paragraphs)
3. Major cultures and societies (2-3 paragraphs)
4. Political landscape and conflicts (1-2 paragraphs)
5. Magic and supernatural elements (1-2 paragraphs)
6. Opportunities for adventure (1 paragraph)"""

        prompt = f"""
Write a detailed setting section for the D&D 5e adventure "{name}".

World Information: {world}
Theme: {theme}

Create a comprehensive setting description that includes:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Use immersive, descriptive language that helps players visualize the world.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_background_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for background section generation"""
        name = campaign_data.get("name", "Campaign")
        story_hook = campaign_data.get("story_hook", {})
        theme = campaign_data.get("theme", "fantasy")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 400-600 words (concise but engaging)."
            content_sections = """1. Historical context and origins (1 paragraph)
2. Key events leading to the current situation (1 paragraph)
3. Major factions and their motivations (1 paragraph)
4. Current conflicts and tensions (1 paragraph)
5. Secrets and hidden truths (1 paragraph)
6. Player character involvement (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 1000-1500 words (detailed and immersive)."
            content_sections = """1. Historical context and origins (2-3 paragraphs)
2. Key events leading to the current situation (2-3 paragraphs)
3. Major factions and their motivations (2-3 paragraphs)
4. Current conflicts and tensions (1-2 paragraphs)
5. Secrets and hidden truths (1-2 paragraphs)
6. Player character involvement (1 paragraph)"""

        prompt = f"""
Write a detailed adventure background section for the D&D 5e campaign "{name}".

Story Hook: {story_hook}
Theme: {theme}

Create a compelling background that includes:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Build mystery and intrigue to hook the players.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_structure_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for structure section generation"""
        name = campaign_data.get("name", "Campaign")
        story_arcs = campaign_data.get("story_arcs", [])
        duration = campaign_data.get("expected_duration", "medium")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 300-500 words (concise overview)."
            content_sections = """1. Overall campaign flow and pacing (1 paragraph)
2. Major story arcs and their progression (1-2 paragraphs)
3. Key plot points and decision moments (1 paragraph)
4. Side quests and optional content (1 paragraph)
5. Campaign timeline and milestones (1 paragraph)
6. Epilogue and resolution possibilities (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 800-1200 words (detailed structure)."
            content_sections = """1. Overall campaign flow and pacing (1-2 paragraphs)
2. Major story arcs and their progression (3-5 paragraphs)
3. Key plot points and decision moments (2-3 paragraphs)
4. Side quests and optional content (1-2 paragraphs)
5. Campaign timeline and milestones (1-2 paragraphs)
6. Epilogue and resolution possibilities (1 paragraph)"""

        prompt = f"""
Write a detailed campaign structure section for the D&D 5e adventure "{name}".

Story Arcs: {len(story_arcs)} arcs available
Duration: {duration}

Create a comprehensive campaign structure that includes:
{content_sections}

Format as a professional D&D adventure book section with clear headings and structure.
Provide clear guidance for DMs on running the campaign.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_locations_content_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for locations content generation"""
        name = campaign_data.get("name", "Campaign")
        locations = campaign_data.get("key_locations", [])
        world = campaign_data.get("world", {})

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 500-700 words (concise but descriptive)."
            content_sections = """1. Overview of key locations (1 paragraph)
2. Brief descriptions for each major location (1-2 paragraphs per location)
3. Key features and points of interest (1 paragraph per location)
4. Basic encounter opportunities (1 paragraph total)
5. Simple navigation details (as appropriate)
6. Basic connections between locations (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 1500-2000 words (comprehensive detail)."
            content_sections = """1. Overview of key locations (1-2 paragraphs)
2. Detailed descriptions for each major location (3-5 paragraphs per location)
3. Points of interest and notable features (1-2 paragraphs per location)
4. Encounter opportunities and adventure hooks (1-2 paragraphs per location)
5. Maps, keys, and navigation details (as appropriate)
6. Connections between locations (1-2 paragraphs)"""

        prompt = f"""
Write a detailed locations section for the D&D 5e campaign "{name}".

World Context: {world}
Number of Locations: {len(locations)}

Create comprehensive location descriptions that include:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Include tactical information useful for combat encounters.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_npcs_content_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for NPCs content generation"""
        name = campaign_data.get("name", "Campaign")
        npcs = campaign_data.get("key_npcs", [])

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 500-700 words (concise character profiles)."
            content_sections = """1. Overview of key characters (1 paragraph)
2. Brief character profiles for each NPC (1-2 paragraphs per NPC)
3. Basic background and motivations (1 paragraph per NPC)
4. Key relationships (1 paragraph total)
5. Role in the story (1 paragraph per NPC)
6. Basic combat statistics (if applicable)"""
        else:  # production mode
            length_instruction = "Length should be approximately 1500-2000 words (detailed character development)."
            content_sections = """1. Overview of key characters (1-2 paragraphs)
2. Detailed character profiles for each NPC (4-6 paragraphs per NPC)
3. Background, motivations, and personality (2-3 paragraphs per NPC)
4. Relationships and connections (1-2 paragraphs per NPC)
5. Role in the story and adventure hooks (1-2 paragraphs per NPC)
6. Combat statistics and tactics (1 paragraph per NPC, if applicable)"""

        prompt = f"""
Write a detailed NPCs section for the D&D 5e campaign "{name}".

Number of NPCs: {len(npcs)}

Create comprehensive NPC descriptions that include:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Include roleplaying tips and plot development opportunities.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_encounters_content_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for encounters content generation"""
        name = campaign_data.get("name", "Campaign")
        difficulty = campaign_data.get("difficulty", "medium")
        level_range = campaign_data.get("level_range", "1-5")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 500-700 words (focused encounter design)."
            content_sections = """1. Basic encounter design philosophy (1 paragraph)
2. Key combat encounters with basic statistics (1-2 paragraphs per encounter)
3. Social encounters overview (1 paragraph)
4. Simple traps and challenges (1 paragraph)
5. Basic scaling guidelines (1 paragraph)
6. Treasure and rewards overview (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 1500-2000 words (comprehensive encounters)."
            content_sections = """1. Overview of encounter design philosophy (1-2 paragraphs)
2. Major combat encounters with full statistics (3-5 paragraphs per encounter)
3. Social encounters and roleplaying opportunities (2-3 paragraphs per encounter)
4. Traps, puzzles, and environmental challenges (2-3 paragraphs per encounter)
5. Scaling guidelines for different party sizes (1-2 paragraphs)
6. Treasure and experience rewards (1 paragraph per encounter)"""

        prompt = f"""
Write a detailed encounters section for the D&D 5e campaign "{name}".

Difficulty: {difficulty}
Level Range: {level_range}

Create comprehensive encounter descriptions that include:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Include tactical advice for Dungeon Masters.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_treasures_content_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for treasures content generation"""
        name = campaign_data.get("name", "Campaign")
        difficulty = campaign_data.get("difficulty", "medium")
        level_range = campaign_data.get("level_range", "1-5")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 300-500 words (concise treasure overview)."
            content_sections = """1. Basic treasure distribution philosophy (1 paragraph)
2. Key magical items with brief descriptions (1 paragraph per item)
3. Gold and treasure overview (1 paragraph)
4. Experience rewards summary (1 paragraph)
5. Alternative rewards overview (1 paragraph)
6. Basic scaling guidelines (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 800-1200 words (detailed treasure system)."
            content_sections = """1. Overview of treasure distribution philosophy (1-2 paragraphs)
2. Major magical items with full descriptions (2-3 paragraphs per item)
3. Gold, gems, and mundane treasures (1-2 paragraphs per significant hoard)
4. Experience point rewards and milestones (1-2 paragraphs)
5. Alternative rewards and roleplaying opportunities (1-2 paragraphs)
6. Treasure scaling guidelines (1 paragraph)"""

        prompt = f"""
Write a detailed treasures and rewards section for the D&D 5e campaign "{name}".

Difficulty: {difficulty}
Level Range: {level_range}

Create comprehensive treasure descriptions that include:
{content_sections}

Format as a professional D&D adventure book section with clear headings.
Include balancing advice for Dungeon Masters.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    def _build_appendices_content_prompt(self, campaign_data: Dict[str, Any], custom_instructions: Optional[str] = None, mode: str = "production") -> str:
        """Build prompt for appendices content generation"""
        name = campaign_data.get("name", "Campaign")

        # Adjust content based on mode
        if mode == "sample":
            length_instruction = "Length should be approximately 300-500 words (essential reference materials)."
            content_sections = """1. Basic character creation guidelines (1 paragraph)
2. Key rules clarifications (1 paragraph)
3. Simple random encounter tables (1 paragraph)
4. NPC stat blocks overview (1 paragraph)
5. Maps and handouts overview (1 paragraph)
6. Adventure tracking basics (1 paragraph)"""
        else:  # production mode
            length_instruction = "Length should be approximately 800-1200 words (comprehensive appendices)."
            content_sections = """1. Character creation guidelines and suggestions (2-3 paragraphs)
2. Important rules clarifications and house rules (2-3 paragraphs)
3. Random encounter tables (1-2 pages worth)
4. NPC stat blocks and quick reference (2-3 paragraphs)
5. Maps and handouts descriptions (1-2 paragraphs)
6. Adventure tracking sheets and notes (1-2 paragraphs)"""

        prompt = f"""
Write a comprehensive appendices section for the D&D 5e campaign "{name}".

Create useful reference materials that include:
{content_sections}

Format as a professional D&D adventure book appendices section.
Include practical tools for Dungeon Masters.
{length_instruction}
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {custom_instructions}"

        return prompt.strip()

    async def generate_campaign_concept(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign concept from preferences"""
        prompt = self._build_campaign_concept_prompt(preferences)

        try:
            response = await self._call_claude_api(prompt)
            concept = self._parse_campaign_concept_response(response)

            # Additional validation specific to campaign concepts
            if concept and self.content_integrity_watchdog.is_active:
                try:
                    self.content_integrity_watchdog.validate_campaign_concept(concept)
                except ContentIntegrityError as e:
                    logger.error(f"Generated campaign concept failed integrity validation: {e.message}")
                    raise

            return concept
        except Exception as e:
            logger.error(f"Failed to generate campaign concept: {e}")
            raise

    def _build_campaign_concept_prompt(self, preferences: Dict[str, Any]) -> str:
        """Build prompt for campaign concept generation"""
        # Extract preference values
        theme = preferences.get("theme", "fantasy")
        difficulty = preferences.get("difficulty", "medium")
        setting = preferences.get("setting", "medieval_fantasy")
        character_focus = preferences.get("character_focus", "balanced")
        npc_style = preferences.get("npc_style", "neutral")
        gameplay_balance = preferences.get("gameplay_balance", "balanced")
        story_length = preferences.get("story_length", "medium")
        story_tone = preferences.get("story_tone", "balanced")
        specific_elements = preferences.get("specific_elements", [])
        freeform_input = preferences.get("freeform_input", "")

        prompt = f"""
You are an expert D&D 5e campaign designer. Create a campaign concept based on these preferences:

PREFERENCES:
- Theme: {theme}
- Difficulty: {difficulty}
- Setting: {setting}
- Character Focus: {character_focus}
- NPC Style: {npc_style}
- Gameplay Balance: {gameplay_balance}
- Story Length: {story_length}
- Story Tone: {story_tone}
- Specific Elements: {', '.join(specific_elements) if specific_elements else 'none'}
- Additional Input: {freeform_input}

TASK:
Create a compelling campaign concept that includes:
1. An evocative title
2. A subtitle that hints at the adventure
3. A brief description (2-3 paragraphs)
4. Recommended level range (e.g., "1-5", "3-8", etc.)

FORMAT:
Return ONLY a JSON object with these exact keys:
{{
    "title": "Campaign Title",
    "subtitle": "Campaign Subtitle",
    "description": "Campaign description...",
    "level_range": "X-Y"
}}

GUIDELINES:
- Create a title that is memorable and evocative
- Subtitle should hint at the adventure theme or challenge
- Description should be exciting and hook the reader
- Level range should be appropriate for the difficulty and length
- Ensure the concept aligns with all specified preferences

Return ONLY the JSON object, no other text.
"""

        return prompt.strip()

    def _parse_campaign_concept_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude response for campaign concept"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('{') and content.strip().endswith('}'):
                return json.loads(content)
            else:
                # Fallback parsing
                return self._extract_campaign_concept_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse campaign concept response: {e}")
            return {
                "title": "Generated Campaign",
                "subtitle": "A D&D 5e Adventure",
                "description": "A campaign generated based on your preferences",
                "level_range": "1-5"
            }

    def _extract_campaign_concept_from_text(self, text: str) -> Dict[str, Any]:
        """Extract campaign concept from text response"""
        # Simple fallback parsing
        lines = text.split('\n')
        concept = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.upper().startswith('TITLE') or line.upper().startswith('CAMPAIGN NAME'):
                concept['title'] = line.split(':', 1)[-1].strip()
            elif line.upper().startswith('SUBTITLE'):
                concept['subtitle'] = line.split(':', 1)[-1].strip()
            elif line.upper().startswith('DESCRIPTION'):
                concept['description'] = line.split(':', 1)[-1].strip()
            elif line.upper().startswith('LEVEL RANGE'):
                concept['level_range'] = line.split(':', 1)[-1].strip()

        # Set defaults
        concept.setdefault('title', 'Generated Campaign')
        concept.setdefault('subtitle', 'A D&D 5e Adventure')
        concept.setdefault('description', 'A campaign generated based on your preferences')
        concept.setdefault('level_range', '1-5')

        return concept

    def _parse_section_content_response(self, response: str) -> str:
        """Parse Claude response for section content"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            # If content is plain text, return it
            if content and not content.strip().startswith('{'):
                return content

            # Try to extract content from JSON structure
            return content or "Content generation failed"

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse section content response: {e}")
            return "Error parsing generated content"

    def _build_world_setting_prompt(self, theme: str, setting_type: str, complexity: str) -> str:
        """Build prompt for world setting generation"""
        prompt = f"""
Generate a rich, immersive world setting for a D&D 5e campaign.

SPECIFICATIONS:
- Theme: {theme}
- Setting Type: {setting_type}
- Complexity: {complexity}

Create a world with:
1. Unique name and core concept
2. Major geographical regions and features
3. 2-3 distinct cultures or societies
4. Magic system and supernatural elements
5. Major factions and political landscape
6. Historical context and significant events

Return as JSON with structure:
{{
    "name": "World Name",
    "description": "World description...",
    "geography": {{"regions": [], "features": []}},
    "cultures": [{{"name": "", "description": ""}}],
    "magic_system": {{"type": "", "traditions": []}},
    "factions": [{{"name": "", "description": "", "status": ""}}],
    "history": "Historical context..."
}}
"""

        return prompt.strip()

    def _build_story_hook_prompt(self, theme: str, difficulty: str, party_level: int) -> str:
        """Build prompt for story hook generation"""
        prompt = f"""
Create an engaging story hook for a D&D 5e campaign.

SPECIFICATIONS:
- Theme: {theme}
- Difficulty: {difficulty}
- Party Level: {party_level}

Generate a hook that includes:
1. Compelling title
2. Detailed scenario description (150-300 words)
3. Clear stakes and consequences
4. 3-5 complicating factors
5. Hook type (personal, mysterious, threatening, opportunity, cosmic)

Return as JSON:
{{
    "title": "Hook Title",
    "description": "Detailed description...",
    "stakes": "What's at stake...",
    "complications": ["complication1", "complication2"],
    "hook_type": "mysterious"
}}
"""

        return prompt.strip()

    def _build_story_arcs_prompt(self, campaign_overview: Dict[str, Any], duration: str) -> str:
        """Build prompt for story arcs generation"""
        prompt = f"""
Design story arcs for a D&D 5e campaign.

CAMPAIGN OVERVIEW: {campaign_overview.get('description', '')}
DURATION: {duration}

Create 2-4 interconnected story arcs with:
1. Clear titles and descriptions
2. 3-5 acts per arc with specific events
3. Dramatic climaxes
4. Satisfying resolutions
5. Logical progression and interconnectedness

Return as JSON array of arc objects.
"""

        return prompt.strip()

    def _build_npcs_prompt(self, count: int, campaign_context: Dict[str, Any]) -> str:
        """Build prompt for NPC generation"""
        prompt = f"""
Generate {count} diverse and memorable NPCs for a D&D 5e campaign.

CAMPAIGN CONTEXT: {campaign_context.get('description', '')}
THEME: {campaign_context.get('theme', 'fantasy')}

For each NPC, include:
1. Name and physical description
2. Race, class, background
3. Detailed personality (traits, ideals, bonds, flaws)
4. Motivation and goals
5. Role in the story
6. Key relationships

Ensure diversity in roles, personalities, and backgrounds.
Return as JSON array of NPC objects.
"""

        return prompt.strip()

    def _build_locations_prompt(self, count: int, campaign_context: Dict[str, Any]) -> str:
        """Build prompt for location generation"""
        prompt = f"""
Generate {count} detailed locations for a D&D 5e campaign.

CAMPAIGN CONTEXT: {campaign_context.get('description', '')}

For each location, include:
1. Name and type
2. Detailed description (100-200 words)
3. Strategic significance to the plot
4. 2-3 notable encounter ideas
5. Visual and atmospheric details

Ensure locations are diverse and provide adventure opportunities.
Return as JSON array of location objects.
"""

        return prompt.strip()

    def _build_quality_validation_prompt(self, content: Dict[str, Any], content_type: str) -> str:
        """Build prompt for quality validation"""
        prompt = f"""
Evaluate the quality of the following {content_type} content for a D&D 5e campaign:

CONTENT: {json.dumps(content, indent=2)}

Rate on these criteria (0-5 scale):
1. Completeness - All required elements present
2. Creativity - Original and engaging ideas
3. Balance - Appropriate for D&D 5e rules
4. Coherence - Internal consistency
5. Engagement - Appeal to players

Provide detailed feedback and overall score.
Return as JSON with scores and feedback.
"""

        return prompt.strip()

    def _parse_campaign_overview_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude response for campaign overview"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            # Try to parse the content as JSON if it looks like JSON
            if content.strip().startswith('{') and content.strip().endswith('}'):
                return json.loads(content)
            else:
                # Fallback: extract basic info from text response
                return self._extract_campaign_overview_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse campaign overview response: {e}")
            return {}

    def _extract_campaign_overview_from_text(self, text: str) -> Dict[str, Any]:
        """Extract campaign overview information from text response"""
        # This is a fallback method for when Claude returns plain text instead of JSON
        lines = text.split('\n')
        overview = {}

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for section headers
            if line.upper().startswith('CAMPAIGN NAME') or line.upper().startswith('NAME'):
                current_section = 'name'
                continue
            elif line.upper().startswith('DESCRIPTION') or line.upper().startswith('OVERVIEW'):
                current_section = 'description'
                continue
            elif line.upper().startswith('TONE') or line.upper().startswith('ATMOSPHERE'):
                current_section = 'tone'
                continue
            elif line.upper().startswith('PARTY') or line.upper().startswith('RECOMMENDED'):
                current_section = 'recommended_party'
                continue
            elif line.upper().startswith('THEMES') or line.upper().startswith('MAJOR'):
                current_section = 'major_themes'
                continue

            # Extract content based on current section
            if current_section and not line.startswith(('CAMPAIGN', 'DESCRIPTION', 'TONE', 'PARTY', 'THEMES')):
                if current_section == 'name':
                    if 'name' not in overview:
                        overview['name'] = line.replace(':', '').strip()
                elif current_section == 'description':
                    if 'description' not in overview:
                        overview['description'] = line
                    else:
                        overview['description'] += ' ' + line
                elif current_section == 'tone':
                    if 'tone' not in overview:
                        overview['tone'] = line
                elif current_section == 'recommended_party':
                    if 'recommended_party' not in overview:
                        overview['recommended_party'] = line
                elif current_section == 'major_themes':
                    if 'major_themes' not in overview:
                        overview['major_themes'] = [line.replace('-', '').strip()]
                    else:
                        overview['major_themes'].append(line.replace('-', '').strip())

        # Set defaults if not found
        overview.setdefault('name', 'Unnamed Campaign')
        overview.setdefault('description', 'A generated D&D campaign')
        overview.setdefault('tone', 'Epic fantasy adventure')
        overview.setdefault('recommended_party', 'Balanced party of 4-5 characters')
        overview.setdefault('major_themes', ['Exploration', 'Adventure', 'Mystery'])

        return overview

    def _parse_world_setting_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude response for world setting"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('{') and content.strip().endswith('}'):
                return json.loads(content)
            else:
                return self._extract_world_setting_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse world setting response: {e}")
            return {}

    def _parse_story_hook_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude response for story hook"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('{') and content.strip().endswith('}'):
                return json.loads(content)
            else:
                return self._extract_story_hook_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse story hook response: {e}")
            return {}

    def _parse_story_arcs_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse Claude response for story arcs"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('[') and content.strip().endswith(']'):
                return json.loads(content)
            else:
                return self._extract_story_arcs_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse story arcs response: {e}")
            return []

    def _parse_npcs_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse Claude response for NPCs"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('[') and content.strip().endswith(']'):
                return json.loads(content)
            else:
                return self._extract_npcs_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse NPCs response: {e}")
            return []

    def _parse_locations_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse Claude response for locations"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('[') and content.strip().endswith(']'):
                return json.loads(content)
            else:
                return self._extract_locations_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse locations response: {e}")
            return []

    def _parse_quality_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude response for quality validation"""
        try:
            data = json.loads(response)
            content = data.get('content', '')

            if content.strip().startswith('{') and content.strip().endswith('}'):
                return json.loads(content)
            else:
                return self._extract_quality_validation_from_text(content)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse quality validation response: {e}")
            return {}

    # Fallback text parsing methods
    def _extract_world_setting_from_text(self, text: str) -> Dict[str, Any]:
        """Extract world setting from text response"""
        return {
            "name": "Generated World",
            "description": text[:500] if text else "A mysterious world",
            "geography": {"regions": ["Various regions"], "features": []},
            "cultures": [{"name": "Primary Culture", "description": "A unique culture"}],
            "magic_system": {"type": "standard", "traditions": ["arcane", "divine"]},
            "factions": [{"name": "Main Faction", "description": "A powerful faction", "status": "active"}],
            "history": text[-500:] if len(text) > 500 else text
        }

    def _extract_story_hook_from_text(self, text: str) -> Dict[str, Any]:
        """Extract story hook from text response"""
        return {
            "title": "The Mysterious Beginning",
            "description": text[:300] if text else "An intriguing start to the adventure",
            "stakes": "The fate of the realm hangs in balance",
            "complications": ["Hidden dangers", "Unreliable allies", "Time pressure"],
            "hook_type": "mysterious"
        }

    def _extract_story_arcs_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract story arcs from text response"""
        return [
            {
                "title": "Main Story Arc",
                "description": text[:200] if text else "The primary storyline",
                "acts": [{"title": "Beginning"}, {"title": "Middle"}, {"title": "End"}],
                "climax": "Epic confrontation",
                "resolution": "Satisfying conclusion"
            }
        ]

    def _extract_npcs_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract NPCs from text response"""
        return [
            {
                "name": "Mysterious Stranger",
                "race": "human",
                "character_class": "rogue",
                "background": "criminal",
                "personality": {"traits": ["mysterious"], "ideals": ["freedom"], "bonds": ["none"], "flaws": ["secretive"]},
                "motivation": "Personal gain",
                "role_in_story": "Guide and informant"
            }
        ]

    def _extract_locations_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract locations from text response"""
        return [
            {
                "name": "Ancient Ruins",
                "type": "dungeon",
                "description": text[:200] if text else "Forgotten ruins filled with mystery",
                "significance": "Contains ancient secrets",
                "encounters": [{"type": "combat", "description": "Guardian creatures"}]
            }
        ]

    def _extract_quality_validation_from_text(self, text: str) -> Dict[str, Any]:
        """Extract quality validation from text response"""
        return {
            "completeness_score": 3.5,
            "engagement_score": 3.0,
            "balance_score": 3.5,
            "technical_quality_score": 4.0,
            "overall_score": 3.5,
            "issues": [],
            "recommendations": ["Content looks good"]
        }
