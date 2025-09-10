# 🎲 Campaign Generator MVP

AI-powered D&D 5e campaign generation service that creates unique, high-quality adventure books with text and images.

## ✨ Overview

This project implements a complete MVP for generating Dungeons & Dragons 5th Edition campaigns using Claude AI and DALL-E. The system provides:

- **🎲 Interactive CLI**: User-friendly command-line interface for campaign generation
- **📖 Professional PDFs**: Complete adventure booklets with text content and custom artwork
- **🎨 AI Image Generation**: Custom illustrations using DALL-E API
- **✅ D&D 5e Validation**: Built-in CursorRules service for rule compliance
- **👁️ Quality Monitoring**: Watchdog service prevents AI drift and monitors performance
- **💾 Smart Caching**: Image and content caching to optimize API usage
- **🏗️ Clean Architecture**: Domain-driven design with clear separation of concerns

## 🎯 MVP Features

### 🎲 Campaign Generation
- **Complete Adventure Books**: 30-100 page campaigns with full content
- **10 Campaign Themes**: Fantasy, Horror, Mystery, Exploration, Political Intrigue, War, Supernatural, Custom
- **4 Difficulty Levels**: Easy, Medium, Hard, Deadly
- **Flexible Party Sizes**: Solo, Duo, Small (3-4), Medium (5-6), Large (7+)
- **5 Duration Options**: One-shot to Epic campaigns
- **Custom Instructions**: User-defined preferences and specific elements

### 📖 Content Structure
- **Cover Page**: Custom artwork with campaign branding
- **Campaign Overview**: Description, themes, recommended party composition
- **World Setting**: Geography, cultures, magic systems, factions
- **Story Elements**: Hooks, plot arcs, climaxes, resolutions
- **Key NPCs**: 3-5 characters with detailed backgrounds and portraits
- **Important Locations**: 3-5 adventure locations with encounter ideas
- **Appendices**: Reference materials and random encounter tables

### 🎨 Visual Elements
- **Cover Art**: Professional fantasy artwork (1792x1024)
- **Character Portraits**: Individual NPC illustrations (512x512, generated at 1024x1024 and resized)
- **Location Images**: Adventure location artwork (1024x1024)
- **World Maps**: Campaign setting overview maps
- **PDF Integration**: All images embedded in professional layout

### ✅ Quality Assurance
- **D&D 5e Validation**: CursorRules service checks rule compliance
- **Quality Scoring**: Content quality assessment (0-5 scale)
- **Balance Analysis**: Encounter difficulty validation
- **Watchdog Monitoring**: AI drift detection and performance tracking
- **Fallback Systems**: Graceful degradation when APIs fail

### 🛠️ Technical Features
- **Interactive CLI**: Rich interface with questionary prompts
- **Dependency Injection**: Clean service architecture
- **Image Caching**: Prevents redundant DALL-E API calls
- **Content Caching**: Redis-based caching for generated content
- **Error Handling**: Comprehensive error recovery and logging
- **Docker Support**: Containerized deployment with docker-compose
- **Enhanced PDF Generation**: Professional campaign booklets with celestial theming
- **Standardized Project Structure**: Organized according to domain-driven design principles

## 📋 Project Standards Compliance

This project follows strict organizational standards:

### ✅ **Folder Structure Standards**
- **No files in project root** - All content properly organized in subdirectories
- **Descriptive filenames** - All files match their content and purpose
- **Domain-Driven Design** - Clear separation between domain, application, and infrastructure layers
- **Organized output** - Generated content separated by type (campaigns, PDFs, temp)

### ✅ **Development Standards**
- **Single responsibility** - Each module has one clear purpose
- **Clean architecture** - Domain-driven design with dependency injection
- **Comprehensive testing** - Unit, integration, and end-to-end test coverage
- **Documentation** - Detailed README files in each major directory
- **Type hints** - Full type annotation throughout the codebase

### ✅ **Content Standards**
- **AI integrity** - No mock responses or fallback content
- **D&D compliance** - Built-in validation ensures rule adherence
- **Quality assurance** - Multiple validation layers prevent AI drift
- **Professional output** - Enhanced PDFs look like published campaign books

## 📁 Standardized Project Structure

```
panverse/
├── 📁 assets/                      # Static assets and templates
│   ├── fonts/                      # Custom fonts for PDF generation
│   └── templates/                  # Document templates
├── 📁 cache/                       # Runtime cache directories
│   ├── content/                    # Generated content cache
│   └── images/                     # Image cache
├── 📁 data/                        # Static data files
│   └── dnd5e_rules/                # D&D 5e validation rules
├── 📁 docs/                        # Documentation
│   ├── guides/                     # Usage guides and examples
│   └── TECHNICAL_SPECIFICATION.md  # Technical documentation
├── 📁 docker/                      # Docker configuration
├── 📁 output/                      # Generated content (organized)
│   ├── campaigns/                  # Campaign text files
│   ├── pdfs/                       # Generated PDF files
│   └── temp/                       # Temporary files
├── 📁 scripts/                     # Executable scripts
│   ├── generation/                 # Campaign generation scripts
│   └── testing/                    # Test and utility scripts
├── 📁 src/                         # Source code (Domain-Driven Design)
│   ├── api/                        # API layer (FastAPI)
│   ├── cli/                        # Command-line interface
│   ├── domain/                     # Domain layer (entities, services)
│   ├── infrastructure/             # Infrastructure layer (DB, external APIs)
│   └── services/                   # Application services
├── 📁 tests/                       # Test suite (unit, integration, e2e)
├── 📁 tools/                       # Utility tools and CLI entry points
├── 📄 requirements.txt             # Python dependencies
└── 📄 README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Anthropic Claude API key (required for campaign generation)
- OpenAI API key (optional, for image generation)

### Local Development Setup

#### Option 1: Quick Setup (Recommended)

1. **Clone and setup automatically**
   ```bash
   git clone <repository-url>
   cd panverse
   ./setup.sh
   ```

2. **Configure your API keys**
   ```bash
   # Edit the .env file with your keys
   nano .env  # or use any text editor

   # Required: Anthropic API key
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxx

   # Optional: OpenAI API key for images
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
   ```

3. **Generate your first campaign!**
   ```bash
   python3 simple_generate.py
   ```

#### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd panverse
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the template and edit with your keys
   cp .env.example .env
   nano .env  # Edit with your API keys

   # Required variables:
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. **Generate a sample campaign**
   ```bash
   python3 simple_generate.py
   ```

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for text generation | ✅ Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for image generation | ❌ No | Disabled |
| `DATABASE_URL` | PostgreSQL connection URL | ❌ No | Local SQLite |
| `REDIS_URL` | Redis connection URL for caching | ❌ No | Local Redis |
| `JWT_SECRET_KEY` | JWT signing key for API auth | ❌ No | Auto-generated |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ❌ No | INFO |

**Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore` for your protection.

### Advanced Usage

#### Interactive CLI Mode
```bash
python3 -m src.cli.app
```
This provides an interactive experience with prompts for all campaign preferences.

#### Script-Based Generation
```bash
# Quick sample campaign (20-30 pages)
python3 simple_generate.py

# Interactive mode with full options
python3 -m src.cli.app --interactive

# Non-interactive with specific parameters
python3 -m src.cli.app --no-interactive --theme fantasy --difficulty medium

# Production mode (60+ pages)
python3 -m src.cli.app --mode production --theme epic --difficulty hard
```

#### Docker Setup (Optional)
```bash
# Start supporting services
cd docker
docker-compose up -d

# Run the application
python3 simple_generate.py
```

### 🎲 Usage Examples

#### Interactive Campaign Generation
```bash
python tools/main.py
```

#### Script-Based Generation
```bash
# Generate complete campaign with images and PDF
python scripts/generation/generate_full_campaign.py

# Generate enhanced professional PDF from existing content
python scripts/generation/generate_enhanced_campaign_pdf.py

# Generate sample content for testing
python scripts/generation/generate_sample.py
```
Follow the interactive prompts to:
- Choose campaign theme (Fantasy, Horror, Mystery, etc.)
- Set difficulty level (Easy, Medium, Hard, Deadly)
- Configure party size and starting level
- Select campaign duration
- Add custom instructions

#### Generated Output
- **Campaign PDF**: Complete adventure booklet saved locally
- **Summary Display**: Campaign details shown in terminal
- **Quality Metrics**: Generation statistics and validation results

### API Access (Optional)
```bash
# Start API server
cd src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   cd docker
   docker-compose up --build
   ```

2. **Access services**
   - API: http://localhost:8000
   - pgAdmin: http://localhost:5050 (admin@campaign-generator.com / admin123)

## API Usage Examples

### Generate a Campaign

```bash
curl -X POST "http://localhost:8000/campaigns" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "fantasy",
    "difficulty": "medium",
    "party_size": "small",
    "starting_level": 3,
    "duration": "medium",
    "custom_instructions": "Include elements of ancient magic"
  }'
```

Response:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "estimated_completion_time": 180,
  "message": "Campaign generation started. Check status at /status/550e8400-e29b-41d4-a716-446655440000"
}
```

### Check Generation Status

```bash
curl "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

### Get Generated Campaign

```bash
curl "http://localhost:8000/campaigns/550e8400-e29b-41d4-a716-446655440001"
```

## Architecture

### Domain-Driven Design

The application follows Domain-Driven Design principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and service orchestration
- **Infrastructure Layer**: External concerns (database, APIs, etc.)
- **API Layer**: REST endpoints and HTTP handling

### Key Components

1. **Campaign Entity**: Central domain entity representing a generated campaign
2. **AI Service**: Integration with Claude for content generation
3. **Validation Service**: Ensures D&D 5e compliance and quality
4. **Repository Pattern**: Abstract data access layer
5. **Service Layer**: Business logic orchestration

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests
pytest
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "migration description"

# Run migrations
alembic upgrade head
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `LOG_LEVEL` | Logging level | No (default: INFO) |

## Deployment

### Production Considerations

1. **Security**
   - Use strong JWT secrets
   - Configure CORS properly
   - Enable HTTPS/TLS
   - Implement rate limiting

2. **Scalability**
   - Horizontal scaling with load balancer
   - Redis clustering for cache
   - PostgreSQL read replicas
   - Async task queuing (Celery, etc.)

3. **Monitoring**
   - Application performance monitoring
   - Error tracking and alerting
   - Database performance monitoring
   - AI usage and cost tracking

### Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: campaign-generator:latest
    environment:
      - ENVIRONMENT=production
    secrets:
      - anthropic_key
      - jwt_secret
      - db_password
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

### Development Guidelines

- Follow the existing code structure and patterns
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all linting and type checking passes
- Follow commit message conventions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Roadmap

### MVP (Current)
- Basic campaign generation
- Core API endpoints
- Quality validation
- Docker deployment

### Future Enhancements
- Advanced customization options
- Campaign continuation
- Multi-language support
- Mobile SDK
- Third-party integrations

---

For detailed technical specifications, see `docs/TECHNICAL_SPECIFICATION.md`.
