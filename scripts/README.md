# Scripts Directory

This directory contains all executable scripts and automation tools for the Panverse campaign generator.

## Directory Structure

```
scripts/
├── generation/          # Campaign generation scripts
│   ├── generate_full_campaign.py
│   ├── generate_campaign_pdf.py
│   ├── generate_enhanced_campaign_pdf.py
│   ├── generate_missing_npcs.py
│   ├── generate_npcs.py
│   └── generate_sample.py
├── testing/            # Test scripts and utilities
│   ├── test_ai_services.py
│   ├── test_cursor_rules.py
│   ├── test_enhanced_pdf.py
│   ├── test_env.py
│   ├── test_import.py
│   ├── test_imports.py
│   ├── test_watchdog_integration.py
│   └── watchdog_demo.py
└── README.md
```

## Usage

### Campaign Generation
```bash
cd scripts/generation
python generate_full_campaign.py
```

### Testing
```bash
cd scripts/testing
python test_enhanced_pdf.py
```

## Standards
- All scripts must have descriptive names matching their content
- Scripts must include proper error handling and logging
- No scripts should be placed in project root
- All scripts must be documented with usage examples
