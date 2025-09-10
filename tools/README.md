# Tools Directory

This directory contains utility tools and command-line interfaces for the Panverse campaign generator.

## Directory Structure

```
tools/
├── main.py            # Main CLI entry point
├── pdf/               # PDF generation utilities
└── README.md
```

## Available Tools

### Main CLI (`main.py`)
Primary command-line interface for campaign generation:
```bash
python tools/main.py generate --theme fantasy --difficulty medium
```

### PDF Tools (`pdf/`)
Specialized PDF generation and processing utilities:
- Enhanced PDF generation with celestial theming
- Template management
- Font embedding utilities

## Standards
- Tools must have clear, single responsibilities
- All tools must include help documentation
- Tools should follow CLI best practices
- Error handling must be comprehensive

## Development
When adding new tools:
1. Create clear, descriptive filenames
2. Include comprehensive documentation
3. Add usage examples
4. Follow established patterns
