"""
Main entry point for the Campaign Generator
"""
import asyncio
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.dirname(__file__))  # Go up from tools/ to project root
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from cli.app import main

if __name__ == "__main__":
    main()
