#!/bin/bash

# Campaign Generator Setup Script
echo "🎲 Setting up D&D Campaign Generator"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created! Please edit it with your API keys."
    echo ""
    echo "Required:"
    echo "  - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/"
    echo "Optional:"
    echo "  - OPENAI_API_KEY: Get from https://platform.openai.com/"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Setup complete! You can now:"
    echo "  • Edit your .env file with API keys"
    echo "  • Run: python3 simple_generate.py (for quick campaigns)"
    echo "  • Run: python3 -m src.cli.app --mode sample (for interactive mode)"
    echo ""
    echo "🎉 Happy campaigning!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
