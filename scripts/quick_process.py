#!/usr/bin/env python3
"""
Quick Process Script

Convenience script to quickly process pose images and rebuild the database.
This runs the main image processing pipeline with sensible defaults.

Usage:
    python scripts/quick_process.py
"""

import os
import sys

# Add parent directory to path to import yoga modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)
os.chdir(project_root)

# Import and run the main processing function
from scripts.process_images import main

if __name__ == "__main__":
    print("🚀 Quick Process - Building Pose Database")
    print("=" * 50)
    main() 