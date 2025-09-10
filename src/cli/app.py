"""
Command Line Interface for Campaign Generator
"""
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

import click
import questionary
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from domain.value_objects import (
    CampaignTheme, DifficultyLevel, PartySize, Duration,
    SettingType, CharacterFocus, NPCStyle, GameplayBalance,
    StoryTone, PlayerPreferences
)
from domain.errors import DomainError, ValidationError
from api.middleware import ErrorHandler
from infrastructure.container import get_container

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()


class CampaignGeneratorCLI:
    """CLI application for generating D&D campaigns"""

    def __init__(self):
        self.container = None
        self.user_id = "cli-user-12345"  # Mock user ID for CLI

    async def initialize_services(self):
        """Initialize all required services through dependency injection"""
        try:
            self.container = await get_container()
            console.print("[green]Services initialized successfully![/green]")
            return self.container

        except Exception as e:
            console.print(f"[red]Failed to initialize services: {e}[/red]")
            logger.exception("Service initialization failed")
            sys.exit(1)

    async def collect_user_preferences(self) -> PlayerPreferences:
        """Collect comprehensive user preferences through interactive prompts"""
        console.print(Panel.fit(
            "[bold blue]🎲 D&D Campaign Generator[/bold blue]\n"
            "Create your custom Dungeons & Dragons 5th Edition campaign!",
            title="Welcome"
        ))

        preferences = PlayerPreferences()

        # Welcome message with instructions
        console.print("\n🎯 [bold cyan]CAMPAIGN PREFERENCE COLLECTION[/bold cyan]")
        console.print("==================================================")
        console.print("Let's create a campaign tailored just for you!")
        console.print("You can skip any section by pressing Enter for 'no preference'")
        console.print("Type 'quit' at any time to exit\n")

        try:
            # Theme selection
            console.print("\n🎭 [bold cyan]CAMPAIGN THEME[/bold cyan]")
            console.print("What type of story interests you most?")
            theme_choices = [
                {"name": "🔍 Mystery - Solve puzzles and uncover secrets", "value": CampaignTheme.MYSTERY},
                {"name": "⚔️ Combat - Fight challenging enemies and tactical battles", "value": CampaignTheme.COMBAT},
                {"name": "🗺️ Exploration - Discover new lands and hidden treasures", "value": CampaignTheme.EXPLORATION},
                {"name": "👑 Political Intrigue - Navigate complex social dynamics", "value": CampaignTheme.POLITICAL_INTRIGUE},
                {"name": "🌿 Survival - Overcome environmental challenges", "value": CampaignTheme.SURVIVAL},
                {"name": "✨ Magical - Experience wonder and arcane mysteries", "value": CampaignTheme.MAGICAL},
                {"name": "👻 Horror - Face terrifying threats", "value": CampaignTheme.HORROR},
                {"name": "😄 Comedy - Enjoy lighthearted adventures", "value": CampaignTheme.COMEDY},
                {"name": "🌟 Epic - Embark on grand quests", "value": CampaignTheme.EPIC},
                {"name": "💝 Personal - Focus on character development", "value": CampaignTheme.PERSONAL},
            ]

            theme_response = await questionary.select(
                "Choose theme (1-10) or Enter for no preference:",
                choices=theme_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if theme_response is not None:
                preferences.theme = theme_response

            # Difficulty selection
            console.print("\n⚔️ [bold cyan]CAMPAIGN DIFFICULTY[/bold cyan]")
            console.print("How challenging do you want the adventure to be?")
            difficulty_choices = [
                {"name": "🌱 Beginner - Easy challenges, forgiving gameplay", "value": DifficultyLevel.EASY},
                {"name": "⚖️ Standard - Balanced challenges and rewards", "value": DifficultyLevel.MEDIUM},
                {"name": "🔥 Challenging - Tough decisions and difficult encounters", "value": DifficultyLevel.HARD},
                {"name": "👑 Expert - Requires strategic thinking", "value": DifficultyLevel.DEADLY},
            ]

            difficulty_response = await questionary.select(
                "Choose difficulty or Enter for no preference:",
                choices=difficulty_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if difficulty_response is not None:
                preferences.difficulty = difficulty_response

            # Setting selection
            console.print("\n🌍 [bold cyan]WORLD SETTING[/bold cyan]")
            console.print("What type of world do you want to explore?")
            setting_choices = [
                {"name": "🏰 Medieval Fantasy - Classic knights, dragons, and magic", "value": SettingType.MEDIEVAL_FANTASY},
                {"name": "🌃 Urban Fantasy - Modern cities with hidden magical elements", "value": SettingType.URBAN_FANTASY},
                {"name": "☢️ Post-Apocalyptic - Surviving in a ruined world", "value": SettingType.POST_APOCALYPTIC},
                {"name": "🚀 Sci-Fi - Advanced technology and space exploration", "value": SettingType.CYBERPUNK},
                {"name": "📚 Historical - Real-world historical settings with fantasy", "value": SettingType.MEDIEVAL_FANTASY},
                {"name": "🏛️ Mythological - Ancient myths and legendary creatures", "value": SettingType.MEDIEVAL_FANTASY},
                {"name": "⚙️ Steampunk - Victorian-era technology and steam power", "value": SettingType.STEAMPUNK},
                {"name": "🌌 Cosmic - Space, time, and reality-bending adventures", "value": SettingType.MEDIEVAL_FANTASY},
            ]

            setting_response = await questionary.select(
                "Choose setting or Enter for no preference:",
                choices=setting_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if setting_response is not None:
                preferences.setting = setting_response

            # Character Focus
            console.print("\n👤 [bold cyan]CHARACTER FOCUS[/bold cyan]")
            console.print("What type of character abilities interest you most?")
            focus_choices = [
                {"name": "⚔️ Combat - Fighting and tactical combat", "value": CharacterFocus.COMBAT},
                {"name": "💬 Social - Dialogue, persuasion, and relationships", "value": CharacterFocus.SOCIAL},
                {"name": "🔮 Magic - Spellcasting and magical abilities", "value": CharacterFocus.MAGIC},
                {"name": "🥷 Stealth - Sneaking, infiltration, and subtlety", "value": CharacterFocus.STEALTH},
                {"name": "⚖️ Balanced - Mix of all approaches", "value": CharacterFocus.BALANCED},
            ]

            focus_response = await questionary.select(
                "Choose focus or Enter for no preference:",
                choices=focus_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if focus_response is not None:
                preferences.character_focus = focus_response

            # NPC Style
            console.print("\n🤝 [bold cyan]NPC RELATIONSHIP STYLE[/bold cyan]")
            console.print("How do you want NPCs to interact with you?")
            npc_choices = [
                {"name": "😊 Friendly - Helpful and cooperative NPCs", "value": NPCStyle.FRIENDLY},
                {"name": "😠 Hostile - Antagonistic and challenging NPCs", "value": NPCStyle.HOSTILE},
                {"name": "🤔 Complex - Multi-dimensional NPCs with mixed motives", "value": NPCStyle.COMPLEX},
                {"name": "😐 Neutral - NPCs that can be swayed either way", "value": NPCStyle.NEUTRAL},
            ]

            npc_response = await questionary.select(
                "Choose NPC style or Enter for no preference:",
                choices=npc_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if npc_response is not None:
                preferences.npc_style = npc_response

            # Gameplay Balance
            console.print("\n⚖️ [bold cyan]GAMEPLAY BALANCE[/bold cyan]")
            console.print("How do you want to balance combat and social interactions?")
            balance_choices = [
                {"name": "⚔️ Combat Heavy - More fighting, less talking", "value": GameplayBalance.COMBAT_HEAVY},
                {"name": "💬 Social Heavy - More talking, less fighting", "value": GameplayBalance.SOCIAL_HEAVY},
                {"name": "⚖️ Balanced - Equal mix of combat and social", "value": GameplayBalance.BALANCED},
            ]

            balance_response = await questionary.select(
                "Choose balance or Enter for no preference:",
                choices=balance_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if balance_response is not None:
                preferences.gameplay_balance = balance_response

            # Story Length (Duration)
            console.print("\n📏 [bold cyan]STORY LENGTH[/bold cyan]")
            console.print("How long do you want the adventure to be?")
            length_choices = [
                {"name": "⏱️ Short - 1-2 sessions, focused story", "value": Duration.ONE_SHOT},
                {"name": "⏰ Medium - 3-5 sessions", "value": Duration.SHORT},
                {"name": "⏳ Long - 6-10 sessions", "value": Duration.MEDIUM},
                {"name": "♾️ Epic - 10+ sessions", "value": Duration.EPIC},
            ]

            length_response = await questionary.select(
                "Choose length or Enter for no preference:",
                choices=length_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if length_response is not None:
                preferences.story_length = length_response

            # Story Tone
            console.print("\n🎨 [bold cyan]STORY TONE[/bold cyan]")
            console.print("What emotional tone do you want for the story?")
            tone_choices = [
                {"name": "🌑 Dark - Grim, serious, and challenging", "value": StoryTone.DARK},
                {"name": "☀️ Light - Uplifting, positive, and hopeful", "value": StoryTone.LIGHT},
                {"name": "💀 Gritty - Realistic, harsh, and unforgiving", "value": StoryTone.GRITTY},
                {"name": "🌈 Whimsical - Playful, imaginative, and fun", "value": StoryTone.WHIMSICAL},
            ]

            tone_response = await questionary.select(
                "Choose tone or Enter for no preference:",
                choices=tone_choices + [{"name": "Enter - No preference (AI will choose)", "value": None}]
            ).unsafe_ask_async()

            if tone_response is not None:
                preferences.story_tone = tone_response

            # Specific Elements
            console.print("\n🎭 [bold cyan]SPECIFIC STORY ELEMENTS[/bold cyan]")
            console.print("Are there any specific elements you'd like to see in your adventure?")
            console.print("Examples: dragons, politics, exploration, magic, technology, etc.")

            elements_input = await questionary.text(
                "Enter specific elements (comma-separated) or Enter for none:",
                multiline=False
            ).unsafe_ask_async()

            if elements_input and elements_input.strip():
                preferences.specific_elements = [elem.strip() for elem in elements_input.split(",")]

            # Freeform Input
            console.print("\n💭 [bold cyan]FREE-FORM INPUT[/bold cyan]")
            console.print("Is there anything else you'd like to tell the AI about your dream campaign?")
            console.print("This could be specific ideas, themes, or anything else on your mind.")

            freeform_input = await questionary.text(
                "Type your thoughts or just hit Enter to start:",
                multiline=True
            ).unsafe_ask_async()

            if freeform_input and freeform_input.strip():
                preferences.freeform_input = freeform_input.strip()

            # Display preferences summary
            self.display_preferences_summary(preferences)

            return preferences

        except KeyboardInterrupt:
            console.print("\n[yellow]Preference collection cancelled by user.[/yellow]")
            raise
        except Exception as e:
            error_message = ErrorHandler.handle_cli_error(e)
            console.print(error_message)
            ErrorHandler.log_error(e, "preference_collection")
            raise

    def display_preferences_summary(self, preferences: PlayerPreferences) -> None:
        """Display a summary of collected preferences"""
        console.print("\n📋 [bold cyan]PREFERENCES SUMMARY[/bold cyan]")
        console.print("==================================================")

        if preferences.theme:
            console.print(f"🎭 Theme: {preferences.theme.value}")
        if preferences.difficulty:
            console.print(f"⚔️ Difficulty: {preferences.difficulty.value}")
        if preferences.setting:
            console.print(f"🌍 Setting: {preferences.setting.value}")
        if preferences.character_focus:
            console.print(f"👤 Character Focus: {preferences.character_focus.value}")
        if preferences.npc_style:
            console.print(f"🤝 NPC Style: {preferences.npc_style.value}")
        if preferences.gameplay_balance:
            console.print(f"⚖️ Balance: {preferences.gameplay_balance.value}")
        if preferences.story_length:
            console.print(f"📏 Length: {preferences.story_length.value}")
        if preferences.story_tone:
            console.print(f"🎨 Tone: {preferences.story_tone.value}")
        if preferences.specific_elements:
            console.print(f"🎭 Elements: {', '.join(preferences.specific_elements)}")
        if preferences.freeform_input:
            console.print(f"💭 Additional: {preferences.freeform_input}")

        console.print("\n🚀 Ready to generate your unique campaign!")

    async def generate_campaign_non_interactive(self, preferences: PlayerPreferences, mode: str = "sample") -> str:
        """Generate a campaign in non-interactive mode with specified mode"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating your {mode} campaign...", total=None)

            try:
                generation_service = self.container.campaign_generation_service
                watchdog_service = self.container.watchdog_service

                # Start timing
                start_time = time.time()

                # Convert PlayerPreferences to parameters for the service
                generation_params = {
                    "theme": preferences.theme.value if preferences.theme else "fantasy",
                    "difficulty": preferences.difficulty.value if preferences.difficulty else "medium",
                    "party_size": "small",
                    "starting_level": 3,
                    "duration": preferences.story_length.value if preferences.story_length else "medium",
                    "setting": preferences.setting.value if preferences.setting else "medieval_fantasy",
                    "character_focus": preferences.character_focus.value if preferences.character_focus else None,
                    "npc_style": preferences.npc_style.value if preferences.npc_style else None,
                    "gameplay_balance": preferences.gameplay_balance.value if preferences.gameplay_balance else None,
                    "story_tone": preferences.story_tone.value if preferences.story_tone else None,
                    "specific_elements": preferences.specific_elements,
                    "freeform_input": preferences.freeform_input
                }

                # Build custom instructions from preferences
                custom_instructions = []
                if preferences.specific_elements:
                    custom_instructions.append(f"Specific elements requested: {', '.join(preferences.specific_elements)}")
                if preferences.character_focus:
                    custom_instructions.append(f"Character focus: {preferences.character_focus.value}")
                if preferences.npc_style:
                    custom_instructions.append(f"NPC style: {preferences.npc_style.value}")
                if preferences.gameplay_balance:
                    custom_instructions.append(f"Gameplay balance: {preferences.gameplay_balance.value}")
                if preferences.story_tone:
                    custom_instructions.append(f"Story tone: {preferences.story_tone.value}")
                if preferences.freeform_input:
                    custom_instructions.append(f"Additional instructions: {preferences.freeform_input}")

                custom_instructions_str = " | ".join(custom_instructions) if custom_instructions else None

                # Start campaign generation with specified mode
                request_id = await generation_service.generate_campaign(
                    theme=generation_params["theme"],
                    difficulty=generation_params["difficulty"],
                    party_size=generation_params["party_size"],
                    starting_level=generation_params["starting_level"],
                    duration=generation_params["duration"],
                    user_id=self.user_id,
                    custom_instructions=custom_instructions_str,
                    mode=mode  # Pass the mode to the service
                )

                progress.update(task, description="Campaign generation started...")

                # Wait for completion
                await asyncio.sleep(2)

                # Get final status
                status = await generation_service.get_generation_status(request_id)

                # Record generation metrics
                generation_time = time.time() - start_time
                success = status["status"] == "completed"

                # Import MetricType for proper enum usage
                from services.watchdog_service import MetricType

                # Track generation metrics
                watchdog_service.track_metric(
                    metric_type=MetricType.GENERATION_TIME,
                    value=generation_time,
                    component="campaign",
                    details={"campaign_id": status.get("campaign_id"), "mode": mode}
                )

                watchdog_service.track_quality_score(
                    component="campaign",
                    score=4.0,
                    details={"campaign_id": status.get("campaign_id"), "mode": mode}
                )

                if success:
                    progress.update(task, description=f"[green]{mode.title()} campaign generated successfully![/green]")
                    return status["campaign_id"]
                else:
                    progress.update(task, description=f"[yellow]Generation status: {status['status']}[/yellow]")
                    return status.get("campaign_id")

            except Exception as e:
                progress.update(task, description=f"[red]Generation failed: {e}[/red]")
                logger.exception("Campaign generation failed")
                raise

    async def generate_campaign(self, preferences: PlayerPreferences) -> str:
        """Generate a campaign based on user preferences"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating your D&D campaign...", total=None)

            try:
                generation_service = self.container.campaign_generation_service
                watchdog_service = self.container.watchdog_service

                # Start timing
                start_time = time.time()

                # Convert PlayerPreferences to parameters for the service
                generation_params = {
                    "theme": preferences.theme.value if preferences.theme else "fantasy",
                    "difficulty": preferences.difficulty.value if preferences.difficulty else "medium",
                    "party_size": "small",  # Default for now
                    "starting_level": 3,  # Default for now
                    "duration": preferences.story_length.value if preferences.story_length else "medium",
                    "setting": preferences.setting.value if preferences.setting else "medieval_fantasy",
                    "character_focus": preferences.character_focus.value if preferences.character_focus else None,
                    "npc_style": preferences.npc_style.value if preferences.npc_style else None,
                    "gameplay_balance": preferences.gameplay_balance.value if preferences.gameplay_balance else None,
                    "story_tone": preferences.story_tone.value if preferences.story_tone else None,
                    "specific_elements": preferences.specific_elements,
                    "freeform_input": preferences.freeform_input
                }

                # Build custom instructions from preferences
                custom_instructions = []
                if preferences.specific_elements:
                    custom_instructions.append(f"Specific elements requested: {', '.join(preferences.specific_elements)}")
                if preferences.character_focus:
                    custom_instructions.append(f"Character focus: {preferences.character_focus.value}")
                if preferences.npc_style:
                    custom_instructions.append(f"NPC style: {preferences.npc_style.value}")
                if preferences.gameplay_balance:
                    custom_instructions.append(f"Gameplay balance: {preferences.gameplay_balance.value}")
                if preferences.story_tone:
                    custom_instructions.append(f"Story tone: {preferences.story_tone.value}")
                if preferences.freeform_input:
                    custom_instructions.append(f"Additional instructions: {preferences.freeform_input}")

                custom_instructions_str = " | ".join(custom_instructions) if custom_instructions else None

                # Start campaign generation
                request_id = await generation_service.generate_campaign(
                    theme=generation_params["theme"],
                    difficulty=generation_params["difficulty"],
                    party_size=generation_params["party_size"],
                    starting_level=generation_params["starting_level"],
                    duration=generation_params["duration"],
                    user_id=self.user_id,
                    custom_instructions=custom_instructions_str
                )

                progress.update(task, description="Campaign generation started...")

                # Wait for completion (in a real implementation, you'd poll the status)
                await asyncio.sleep(2)  # Simulate processing time

                # Get final status
                status = await generation_service.get_generation_status(request_id)

                # Record generation metrics
                generation_time = time.time() - start_time
                success = status["status"] == "completed"

                # Track generation metrics (update to match watchdog interface)
                await watchdog_service.track_metric(
                    metric_type="generation_time",
                    value=generation_time,
                    component="campaign",
                    details={"campaign_id": status.get("campaign_id")}
                )

                await watchdog_service.track_quality_score(
                    component="campaign",
                    score=4.0,
                    details={"campaign_id": status.get("campaign_id")}
                )

                if success:
                    progress.update(task, description="[green]Campaign generated successfully![/green]")

                    # Try to generate PDF
                    if status["campaign_id"]:
                        await self.generate_campaign_pdf(status["campaign_id"])

                    return status["campaign_id"]
                else:
                    progress.update(task, description=f"[yellow]Generation status: {status['status']}[/yellow]")
                    return status.get("campaign_id")

            except Exception as e:
                progress.update(task, description=f"[red]Generation failed: {e}[/red]")
                logger.exception("Campaign generation failed")
                raise

    async def generate_campaign_pdf(self, campaign_id: str) -> Optional[str]:
        """Generate PDF for the campaign"""
        try:
            # Get campaign data
            campaign = await self.container.campaign_retrieval_service.get_campaign(campaign_id, self.user_id)

            # Generate PDF
            pdf_service = self.container.pdf_service
            pdf_path = await pdf_service.generate_campaign_pdf(campaign)

            console.print(f"[green]PDF generated: {pdf_path}[/green]")
            return pdf_path

        except Exception as e:
            console.print(f"[yellow]PDF generation failed: {e}[/yellow]")
            return None

    async def display_campaign_summary(self, campaign_id: str):
        """Display a summary of the generated campaign"""
        try:
            retrieval_service = self.container.campaign_retrieval_service
            campaign = await retrieval_service.get_campaign(campaign_id, self.user_id)

            if not campaign:
                console.print("[red]Campaign not found![/red]")
                return

            # Create a nice summary display
            summary = f"""
[bold cyan]📖 {campaign.name}[/bold cyan]

[bold white]Description:[/bold white]
{campaign.description}

[bold white]Campaign Details:[/bold white]
• Theme: {campaign.theme.value}
• Difficulty: {campaign.difficulty.value}
• Party Size: {campaign.party_size.value}
• Starting Level: {campaign.starting_level}
• Duration: {campaign.expected_duration.value}
• Quality Score: {campaign.quality_score.value}/5.0

[bold white]World:[/bold white] {campaign.world.name if campaign.world else 'Not generated'}

[bold white]Story Elements:[/bold white]
• NPCs: {len(campaign.key_npcs)}
• Locations: {len(campaign.key_locations)}
• Story Arcs: {len(campaign.story_arcs)}
"""

            # Add sections information if available
            if campaign.sections:
                summary += f"""
[bold white]Campaign Sections:[/bold white]
• Total Sections: {len(campaign.sections)}
• Total Content Length: {campaign.get_total_content_length()} characters
• Total Images: {campaign.get_total_image_count()}
"""

                # List section titles
                section_titles = [f"  - {section.title}" for section in campaign.sections[:5]]
                if len(campaign.sections) > 5:
                    section_titles.append(f"  ... and {len(campaign.sections) - 5} more")
                summary += "\n" + "\n".join(section_titles)

            # Add player preferences if available
            if campaign.player_preferences and campaign.player_preferences.has_preferences():
                summary += f"""

[bold white]Player Preferences Used:[/bold white]"""
                prefs = campaign.player_preferences.get_preference_summary()
                for key, value in prefs.items():
                    summary += f"\n• {key.replace('_', ' ').title()}: {value}"

            console.print(Panel(summary, title="🎲 Campaign Summary"))

        except Exception as e:
            console.print(f"[red]Error displaying campaign: {e}[/red]")
            logger.exception("Error displaying campaign summary")

    async def run(self):
        """Main CLI application flow"""
        try:
            # Initialize services
            session = await self.initialize_services()

            # Collect user preferences
            preferences = await self.collect_user_preferences()

            # Generate campaign
            campaign_id = await self.generate_campaign(preferences)

            if campaign_id:
                # Display summary
                await self.display_campaign_summary(campaign_id)

                # Ask about next steps
                next_action = await questionary.select(
                    "What would you like to do next?",
                    choices=[
                        {"name": "Generate PDF (enhanced)", "value": "pdf"},
                        {"name": "View detailed campaign info", "value": "details"},
                        {"name": "Generate another campaign", "value": "another"},
                        {"name": "Exit", "value": "exit"}
                    ]
                ).unsafe_ask_async()

                if next_action == "another":
                    await self.run()  # Recursive call for another campaign
                elif next_action == "details":
                    console.print("[yellow]Detailed view coming soon![/yellow]")
                elif next_action == "pdf":
                    console.print("[yellow]PDF generation coming soon![/yellow]")

            console.print("[green]Thank you for using the Campaign Generator![/green]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Generation cancelled by user.[/yellow]")
        except Exception as e:
            error_message = ErrorHandler.handle_cli_error(e)
            console.print(error_message)
            ErrorHandler.log_error(e, "cli_application")


@click.command()
@click.option('--theme', type=click.Choice(['fantasy', 'horror', 'mystery', 'exploration', 'political_intrigue', 'war', 'supernatural', 'combat', 'survival', 'magical', 'comedy', 'epic', 'personal']),
              help='Campaign theme')
@click.option('--difficulty', type=click.Choice(['easy', 'medium', 'hard', 'deadly']),
              help='Difficulty level')
@click.option('--party-size', type=click.Choice(['solo', 'duo', 'small', 'medium', 'large']),
              help='Party size')
@click.option('--starting-level', type=int, default=3, help='Starting character level')
@click.option('--duration', type=click.Choice(['one_shot', 'short', 'medium', 'long', 'epic']),
              help='Campaign duration')
@click.option('--setting', type=click.Choice(['medieval_fantasy', 'dark_fantasy', 'high_fantasy', 'urban_fantasy', 'post_apocalyptic', 'steampunk', 'cyberpunk']),
              help='Campaign setting')
@click.option('--character-focus', type=click.Choice(['combat', 'social', 'magic', 'stealth', 'balanced']),
              help='Character focus')
@click.option('--npc-style', type=click.Choice(['friendly', 'hostile', 'complex', 'neutral']),
              help='NPC relationship style')
@click.option('--gameplay-balance', type=click.Choice(['combat_heavy', 'social_heavy', 'balanced']),
              help='Gameplay balance')
@click.option('--story-tone', type=click.Choice(['dark', 'light', 'gritty', 'whimsical']),
              help='Story tone')
@click.option('--specific-elements', help='Comma-separated specific elements')
@click.option('--freeform-input', help='Freeform additional instructions')
@click.option('--interactive/--no-interactive', default=True, help='Use interactive mode')
@click.option('--mode', type=click.Choice(['sample', 'production']), default='sample',
              help='Generation mode: sample (20-30 pages) or production (60+ pages)')
def main(theme, difficulty, party_size, starting_level, duration, setting, character_focus, npc_style, gameplay_balance, story_tone, specific_elements, freeform_input, interactive, mode):
    """D&D Campaign Generator CLI"""

    async def async_main():
        cli = CampaignGeneratorCLI()

        if interactive:
            await cli.run()
        else:
            # Non-interactive mode with provided parameters
            console.print(f"[blue]🎲 Campaign Generator - {mode.title()} Mode[/blue]")

            # Initialize services first
            await cli.initialize_services()

            # Set defaults for missing parameters
            theme_param = theme or "fantasy"
            difficulty_param = difficulty or "medium"
            party_size_param = party_size or "small"
            duration_param = duration or "medium"

            # Create preferences
            preferences = PlayerPreferences()
            if theme_param:
                preferences.theme = CampaignTheme(theme_param)
            if difficulty_param:
                preferences.difficulty = DifficultyLevel(difficulty_param)
            if setting:
                preferences.setting = SettingType(setting)
            if character_focus:
                preferences.character_focus = CharacterFocus(character_focus)
            if npc_style:
                preferences.npc_style = NPCStyle(npc_style)
            if gameplay_balance:
                preferences.gameplay_balance = GameplayBalance(gameplay_balance)
            if story_tone:
                preferences.story_tone = StoryTone(story_tone)
            if duration_param:
                preferences.story_length = Duration(duration_param)
            if specific_elements:
                preferences.specific_elements = [elem.strip() for elem in specific_elements.split(",")]
            if freeform_input:
                preferences.freeform_input = freeform_input

            # Generate campaign
            campaign_id = await cli.generate_campaign_non_interactive(preferences, mode)

            if campaign_id:
                # Display summary
                await cli.display_campaign_summary(campaign_id)

    asyncio.run(async_main())


if __name__ == "__main__":
    main()
