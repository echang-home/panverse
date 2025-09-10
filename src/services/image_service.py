"""
Image Generation Service using Claude AI and OpenAI's DALL-E API
Supports both Claude for high-quality fantasy art and DALL-E for general illustrations
"""
import os
import logging
import hashlib
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import aiohttp
import json
from PIL import Image

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for generating images using Claude AI and DALL-E API"""

    def __init__(self, openai_api_key: str = None, claude_api_key: str = None, output_dir: str = "images", model: str = "dall-e-3"):
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()

        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.claude_api_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.model = model

        # API URLs
        self.openai_url = "https://api.openai.com/v1/images/generations"
        self.claude_url = "https://api.anthropic.com/v1/messages"

        # Initialize HTTP session
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_image_hash(self, prompt: str, size: str = "1024x1024", resize_to: Optional[Tuple[int, int]] = None) -> str:
        """Generate a hash for the image based on prompt and parameters"""
        resize_str = f"_{resize_to[0]}x{resize_to[1]}" if resize_to else ""
        content = f"{prompt}_{size}_{self.model}{resize_str}"
        return hashlib.md5(content.encode()).hexdigest()

    async def generate_image(self, prompt: str, image_type: str = "general", filename: str = None, style: str = "fantasy", size: str = "1024x1024", quality: str = "standard", resize_to: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """Generate an image using Claude (for fantasy art) or DALL-E (for general images)"""

        # Ensure session is initialized

        # Determine which service to use based on image type and style
        use_claude = (
            image_type in ["cover", "chapter_opener", "portrait", "fantasy_art"] or
            style in ["dramatic_fantasy", "character_portrait", "fantasy_illustration"]
        )

        if use_claude and self.claude_api_key:
            return await self._generate_claude_image(prompt, filename or f"{image_type}_{hash(prompt) % 10000}.png")
        elif self.openai_api_key:
            return await self._generate_dalle_image(prompt, size, quality, resize_to, filename)
        else:
            logger.warning("No API keys available for image generation")
            return None

    async def _generate_claude_image(self, prompt: str, filename: str) -> Optional[str]:
        """Generate an image using Claude AI for high-quality fantasy art"""
        if not self.claude_api_key:
            logger.warning("Claude API key not provided")
            return None

        # Ensure session is initialized
        if not self.session:
            self.session = aiohttp.ClientSession()


        # Check cache first
        image_hash = self._get_image_hash(prompt, "claude")
        cached_path = self.output_dir / f"{image_hash}.png"

        if cached_path.exists():
            logger.info(f"Using cached Claude image: {cached_path}")
            return str(cached_path)

        try:
            # Enhanced Claude prompt for better fantasy art results
            enhanced_prompt = f"""Create a highly detailed fantasy illustration in the style of professional D&D campaign books. {prompt}

Style requirements:
- Professional fantasy art quality
- Rich, vibrant colors
- Dramatic lighting and shadows
- Detailed textures and intricate elements
- Suitable for publication in an RPG book
- High resolution, crisp details
- Authentic fantasy aesthetic"""

            # Claude API request for image generation
            headers = {
                "x-api-key": self.claude_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"Please generate a detailed description for creating this image, then provide guidance on how to create it as a professional fantasy illustration: {enhanced_prompt}"
                }]
            }

            async with self.session.post(self.claude_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    # For now, we'll use Claude to generate detailed prompts that can be used with DALL-E
                    # In a real implementation, you'd use Claude's vision capabilities or an image generation service
                    detailed_description = result["content"][0]["text"]

                    # Use DALL-E with the enhanced Claude description
                    return await self._generate_dalle_image(detailed_description, "1024x1024", "standard", None, filename)
                else:
                    logger.error(f"Claude API error: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error generating Claude image: {e}")
            return None

    async def _generate_dalle_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", resize_to: Optional[Tuple[int, int]] = None, filename: str = None) -> Optional[str]:
        """Generate an image using DALL-E"""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided, skipping image generation")
            return None

        # Ensure session is initialized
        if not self.session:
            self.session = aiohttp.ClientSession()


        # Check cache first
        image_hash = self._get_image_hash(prompt, size, resize_to)
        cached_path = self.output_dir / f"{image_hash}.png"

        if cached_path.exists():
            logger.info(f"Using cached image: {cached_path}")
            return str(cached_path)

        try:
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "prompt": prompt,
                "size": size,
                "quality": quality if quality in ['standard', 'hd'] else 'standard',
                "n": 1
            }

            logger.info(f"Generating image with prompt: {prompt[:100]}...")

            # Make API request
            async with self.session.post(self.openai_url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"DALL-E API error: {response.status} - {error_text}")
                    return None

                result = await response.json()

                # Download the generated image
                image_url = result["data"][0]["url"]

                # Download image
                image_path = await self._download_image(image_url, cached_path)

                # Resize if requested
                if resize_to:
                    image_path = await self._resize_image(image_path, resize_to)
                    logger.info(f"Image generated, resized, and saved: {image_path}")
                else:
                    logger.info(f"Image generated and saved: {image_path}")

                return str(image_path)

        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            return None

    async def _download_image(self, url: str, save_path: Path) -> str:
        """Download image from URL and save to file"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")

                # Save image to file
                with open(save_path, 'wb') as f:
                    f.write(await response.read())

                return str(save_path)

        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            raise

    async def _resize_image(self, image_path: str, size: Tuple[int, int]) -> str:
        """Resize image to specified dimensions"""
        try:
            # Open image with PIL
            with Image.open(image_path) as img:
                # Resize using high-quality resampling
                resized_img = img.resize(size, Image.Resampling.LANCZOS)

                # Save resized image
                resized_img.save(image_path, quality=95)

                logger.info(f"Image resized to {size[0]}x{size[1]}: {image_path}")
                return image_path

        except Exception as e:
            logger.error(f"Failed to resize image {image_path}: {e}")
            return image_path  # Return original path if resize fails

    async def generate_campaign_images(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate a set of images for a campaign"""
        images = {}

        # Generate cover art
        cover_prompt = self._create_cover_prompt(campaign_data)
        cover_image = await self.generate_image(cover_prompt, size="1792x1024")  # Wide format for cover
        if cover_image:
            images["cover"] = cover_image

        # Generate world map (if world data exists)
        if "world" in campaign_data and campaign_data["world"]:
            map_prompt = self._create_world_map_prompt(campaign_data["world"])
            map_image = await self.generate_image(map_prompt, size="1024x1024")
            if map_image:
                images["world_map"] = map_image

        # Generate NPC portraits
        if "npcs" in campaign_data and campaign_data["npcs"]:
            npc_images = await self.generate_npc_portraits(campaign_data["npcs"][:3])  # Limit to 3 NPCs
            images.update(npc_images)

        # Generate location images
        if "locations" in campaign_data and campaign_data["locations"]:
            location_images = await self.generate_location_images(campaign_data["locations"][:2])  # Limit to 2 locations
            images.update(location_images)

        return images

    def _create_cover_prompt(self, campaign_data: Dict[str, Any]) -> str:
        """Create a prompt for campaign cover art"""
        theme = campaign_data.get("theme", "fantasy")
        name = campaign_data.get("name", "D&D Campaign")

        base_prompt = f"""
        Create a stunning fantasy book cover for a Dungeons & Dragons campaign titled "{name}".
        Theme: {theme}. Style: Epic fantasy art, highly detailed, professional book cover.
        Include heroic fantasy elements, dramatic lighting, magical effects.
        """

        if "description" in campaign_data:
            base_prompt += f" Inspired by: {campaign_data['description'][:200]}"

        return base_prompt.strip()

    def _create_world_map_prompt(self, world_data: Dict[str, Any]) -> str:
        """Create a prompt for world map"""
        world_name = world_data.get("name", "Fantasy World")
        geography = world_data.get("geography", {})

        prompt = f"""
        Create a beautiful fantasy world map for "{world_name}".
        Style: Hand-drawn fantasy cartography, detailed terrain, borders, cities, mountains, forests, rivers.
        """

        if isinstance(geography, dict):
            if "terrain" in geography:
                prompt += f" Terrain features: {geography['terrain']}"
            if "features" in geography:
                prompt += f" Notable features: {geography['features']}"

        return prompt.strip()

    async def generate_npc_portraits(self, npcs: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate portraits for NPCs"""
        images = {}

        for i, npc in enumerate(npcs):
            prompt = self._create_npc_portrait_prompt(npc)
            # Generate at 1024x1024 (supported by DALL-E) then resize to 512x512
            portrait = await self.generate_image(prompt, size="1024x1024", resize_to=(512, 512))

            if portrait:
                npc_name = npc.get("name", f"NPC_{i+1}").replace(" ", "_")
                images[f"npc_{i+1}_{npc_name}"] = portrait

        return images

    def _create_npc_portrait_prompt(self, npc: Dict[str, Any]) -> str:
        """Create a prompt for NPC portrait"""
        name = npc.get("name", "Character")
        race = npc.get("race", "human")
        character_class = npc.get("character_class", "adventurer")
        personality = npc.get("personality", {})

        prompt = f"""
        Create a detailed character portrait of {name}, a {race} {character_class}.
        Fantasy art style, professional illustration, dramatic lighting, detailed facial features.
        """

        # Add personality traits to prompt
        if isinstance(personality, dict):
            traits = personality.get("traits", [])
            if traits:
                prompt += f" Character traits: {', '.join(traits[:3])}"

        return prompt.strip()

    async def generate_location_images(self, locations: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate images for locations"""
        images = {}

        for i, location in enumerate(locations):
            prompt = self._create_location_prompt(location)
            location_image = await self.generate_image(prompt, size="1024x1024")

            if location_image:
                location_name = location.get("name", f"Location_{i+1}").replace(" ", "_")
                images[f"location_{i+1}_{location_name}"] = location_image

        return images

    def _create_location_prompt(self, location: Dict[str, Any]) -> str:
        """Create a prompt for location image"""
        name = location.get("name", "Location")
        type_ = location.get("type", "place")
        description = location.get("description", "")

        prompt = f"""
        Create a beautiful fantasy illustration of {name}, a {type_} in a D&D campaign.
        Highly detailed, atmospheric fantasy art, dramatic lighting, immersive scene.
        """

        if description:
            prompt += f" Description: {description[:150]}"

        return prompt.strip()

    async def generate_batch_images(self, prompts: List[str], size: str = "1024x1024", resize_to: Optional[Tuple[int, int]] = None) -> List[Optional[str]]:
        """Generate multiple images in parallel"""
        tasks = [self.generate_image(prompt, size, resize_to=resize_to) for prompt in prompts]

        # Limit concurrency to avoid API rate limits
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

        async def limited_generate(prompt):
            async with semaphore:
                return await self.generate_image(prompt, size, resize_to=resize_to)

        limited_tasks = [limited_generate(prompt) for prompt in prompts]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate image {i+1}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)

        return processed_results

    async def generate_section_image(self, campaign_data: Dict[str, Any], section_id: str, size: str = "1024x1024", mode: str = "production") -> Optional[str]:
        """Generate an image for a specific campaign section"""
        prompt = self._create_section_image_prompt(campaign_data, section_id, mode)
        return await self.generate_image(prompt, size)

    async def generate_cover_image(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Generate cover image for campaign"""
        prompt = self._create_cover_image_prompt(campaign_data)
        return await self.generate_image(prompt, size="1792x1024")  # Wide format for cover

    async def generate_all_section_images(self, campaign_data: Dict[str, Any], mode: str = "production") -> Dict[str, Optional[str]]:
        """Generate images for all campaign sections based on mode"""
        # Adjust sections based on mode
        if mode == "test":
            # Test mode: Generate fewer images (7-15 total)
            sections = ["introduction", "setting", "locations", "npcs", "encounters"]
        else:
            # Production mode: Generate images for all sections (15-40 total)
            sections = [
                "introduction", "setting", "background", "structure",
                "locations", "npcs", "encounters", "treasures", "appendices"
            ]

        images = {}
        for section in sections:
            image_path = await self.generate_section_image(campaign_data, section, mode=mode)
            if image_path:
                images[f"{section}_image"] = image_path

        return images

    def _create_section_image_prompt(self, campaign_data: Dict[str, Any], section_id: str, mode: str = "production") -> str:
        """Create a prompt for section-specific image generation"""
        name = campaign_data.get("name", "Campaign")
        theme = campaign_data.get("theme", "fantasy")
        setting = campaign_data.get("setting", "medieval_fantasy")

        section_prompts = {
            "introduction": f"Create an evocative scene from the D&D campaign '{name}' that captures the overall mood and theme of the adventure. Setting: {setting}, Theme: {theme}",
            "setting": f"Create a panoramic view of the main setting for the D&D campaign '{name}'. Setting: {setting}, Theme: {theme}",
            "background": f"Create an illustration depicting a historical or legendary event from the D&D campaign '{name}'. Setting: {setting}, Theme: {theme}",
            "structure": f"Create an illustrated map or diagram showing the key locations and their relationships in the D&D campaign '{name}'. Setting: {setting}",
            "locations": f"Create an atmospheric illustration of one of the key locations from the D&D campaign '{name}'. Setting: {setting}",
            "npcs": f"Create a portrait of a major NPC from the D&D campaign '{name}'. Setting: {setting}, Theme: {theme}",
            "encounters": f"Create an illustration of an exciting encounter or monster from the D&D campaign '{name}'. Setting: {setting}, Theme: {theme}",
            "treasures": f"Create an illustration of a magical item or treasure from the D&D campaign '{name}'. Setting: {setting}",
            "appendices": f"Create a decorative illustration for the appendices of the D&D campaign '{name}'. Setting: {setting}",
        }

        base_prompt = section_prompts.get(section_id, f"Create an illustration for the D&D campaign '{name}'")

        # Adjust style guidelines based on mode
        if mode == "test":
            style_guidelines = """
        Style guidelines:
        - Clean, professional fantasy art suitable for a D&D campaign book
        - Good composition and readable details
        - Should match the style of official D&D artwork
        - No text or titles
        - Moderate detail level (suitable for quick validation)
        """
        else:  # production mode
            style_guidelines = """
        Style guidelines:
        - Professional fantasy art suitable for a D&D campaign book
        - Rich details and atmosphere
        - Should match the style of official D&D artwork
        - No text or titles
        - High detail level for publication quality
        """

        prompt = f"""
        {base_prompt}
        {style_guidelines}
        """

        return prompt.strip()

    def _create_cover_image_prompt(self, campaign_data: Dict[str, Any]) -> str:
        """Create prompt for cover image generation"""
        name = campaign_data.get("name", "Campaign")
        subtitle = campaign_data.get("subtitle", "")
        theme = campaign_data.get("theme", "fantasy")
        setting = campaign_data.get("setting", "medieval_fantasy")
        tone = campaign_data.get("story_tone", "balanced")

        prompt = f"""
        Create a dramatic, professional D&D campaign cover art for:

        Title: {name}
        Subtitle: {subtitle}
        Theme: {theme}
        Setting: {setting}
        Tone: {tone}

        Style guidelines:
        - Professional fantasy art suitable for a D&D campaign book
        - Dramatic lighting and composition
        - Rich colors and details
        - Should look like official D&D artwork
        - No text or titles (will be added later)
        - Landscape orientation
        """

        return prompt.strip()
