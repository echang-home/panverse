#!/usr/bin/env python3
"""
Test script to check what's in domain.services
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import domain.services as ds
    print("domain.services attributes:")
    print(dir(ds))
    print("\nTrying to access CampaignGenerationService:")
    print(hasattr(ds, 'CampaignGenerationService'))
    if hasattr(ds, 'CampaignGenerationService'):
        print(ds.CampaignGenerationService)
    else:
        print("CampaignGenerationService not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
