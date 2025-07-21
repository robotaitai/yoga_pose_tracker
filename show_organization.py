#!/usr/bin/env python3
"""
🗂️ Project Organization Overview

Shows the clean, well-organized structure of the yoga pose tracker.
"""

def main():
    print("🗂️ YOGA POSE TRACKER - CLEAN ORGANIZATION")
    print("=" * 60)
    print()
    
    structure = """
🧘 MAIN APPLICATIONS (Choose Your Version)
├── yoga_coach_simple.py       ⭐ Recommended start - works immediately
├── yoga_coach_performance.py  📊 Full version with historical tracking  
└── run_yoga_coach.sh          🚀 Auto-launcher (detects PyYAML)

📊 CORE MODULES (The Brain)
├── pose_utils.py              👁️ Pose detection & comparison
├── angle_analyzer.py          📐 Critical angle analysis
├── pose_database.py           🗄️ Optimized pose matching
├── performance_tracker.py     📈 Historical data tracking
└── performance_narrator.py    🎙️ Achievement-focused voice

⚙️ CONFIGURATION
├── config.yaml               🔧 YAML settings (full version)
├── requirements.txt          📦 Python dependencies
└── .gitignore               🚫 Privacy protection

📁 DATA DIRECTORIES (Your Private Data)
├── data/                    📊 Performance history (gitignored)
│   ├── simple_history.json  📈 Angle measurements
│   └── simple_bests.json    🏆 Personal bests
├── sessions/                💾 Session recordings (gitignored)
├── positions/               📸 Reference images (gitignored)
└── pose_database/           🗄️ Processed pose data

🛠️ UTILITIES & TOOLS  
├── scripts/                 🔧 Organized utility scripts
│   ├── setup.sh            🚀 Complete project setup
│   ├── install_yaml.sh     📦 PyYAML installer
│   ├── process_images.py   🖼️ Image processor
│   ├── check_my_data.py    📊 Quick data viewer
│   └── view_my_data.py     📈 Detailed data analysis
├── tests/                  🧪 Debug and testing tools
└── docs/                   📚 Documentation
    └── DATA_STORAGE.md     📊 Data storage guide

📁 ARCHIVE (Old Versions)
├── yoga_coach_old.py       🗄️ Original coach (reference)
└── yoga_narrator_old.py   🗄️ Original narrator (reference)
"""
    
    print(structure)
    print()
    print("🎯 QUICK START GUIDE:")
    print("-" * 30)
    print("1. 🚀 python yoga_coach_simple.py        # Start immediately")
    print("2. 📊 python scripts/check_my_data.py    # View your data")
    print("3. 🔧 ./scripts/install_yaml.sh          # For full version")
    print("4. 🏃 ./run_yoga_coach.sh                # Run full system")
    print()
    print("🔊 WHAT YOU'LL HEAR:")
    print("-" * 25)
    print('🎙️ "New personal best standing leg: 178.3 degrees!"')
    print('🎙️ "Great improvement! 3.2 degrees better than average."')
    print('🎙️ "Excellent form! Very precise alignment."')
    print()
    print("💾 YOUR DATA IS SAFE:")
    print("-" * 25)
    print("✅ 100% Local - Never leaves your computer")
    print("✅ Git-ignored - Private data not shared")
    print("✅ JSON format - Easy to backup and read")
    print("✅ Achievement-focused - Celebrates real progress")
    print()
    print("🧘 Ready to start your personal yoga coaching journey! 🏆")

if __name__ == "__main__":
    main() 