#!/usr/bin/env python3
"""
🔍 Quick Data Checker

Shows if your yoga data is being saved and what's in it.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

def main():
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🔍 CHECKING YOUR YOGA DATA...")
    print("=" * 50)
    
    # Check for data directory
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("❌ No 'data' directory found!")
        print("💡 Run a yoga session first to create data")
        return
    
    print(f"✅ Data directory exists: {data_dir.absolute()}")
    print()
    
    # Check for simple data files
    simple_history = data_dir / "simple_history.json"
    simple_bests = data_dir / "simple_bests.json"
    
    print("📊 SIMPLE VERSION DATA:")
    print("-" * 30)
    
    if simple_history.exists():
        try:
            with open(simple_history, 'r') as f:
                history = json.load(f)
            print(f"✅ Angle measurements: {len(history)} recorded")
            
            if history:
                print("🕐 Most recent measurements:")
                for measurement in history[-3:]:  # Show last 3
                    timestamp = datetime.fromisoformat(measurement['timestamp'])
                    print(f"   • {measurement['pose'].replace('_', ' ').title()}: "
                          f"{measurement['angle_name'].replace('_', ' ')} = "
                          f"{measurement['value']:.1f}° "
                          f"({timestamp.strftime('%H:%M:%S')})")
        except Exception as e:
            print(f"❌ Error reading history: {e}")
    else:
        print("📝 No angle measurements yet")
    
    if simple_bests.exists():
        try:
            with open(simple_bests, 'r') as f:
                bests = json.load(f)
            print(f"🏆 Personal bests: {len(bests)} recorded")
            
            if bests:
                print("🎯 Your current personal bests:")
                for key, record in bests.items():
                    pose, angle = key.split('_', 1)
                    pose_name = pose.replace('_', ' ').title()
                    angle_name = angle.replace('_', ' ')
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    print(f"   • {pose_name} - {angle_name}: {record['value']:.1f}° "
                          f"(set {timestamp.strftime('%m/%d %H:%M')})")
        except Exception as e:
            print(f"❌ Error reading bests: {e}")
    else:
        print("🎯 No personal bests yet")
    
    print()
    
    # Check for full version data
    print("📈 FULL VERSION DATA:")
    print("-" * 25)
    
    performance_history = data_dir / "performance_history.json"
    personal_bests = data_dir / "personal_bests.json"
    daily_stats = data_dir / "daily_stats.json"
    
    files_found = []
    if performance_history.exists():
        files_found.append("performance_history.json")
    if personal_bests.exists():
        files_found.append("personal_bests.json")
    if daily_stats.exists():
        files_found.append("daily_stats.json")
    
    if files_found:
        print(f"✅ Full version files found: {', '.join(files_found)}")
    else:
        print("📝 No full version data yet (install PyYAML to use)")
    
    print()
    
    # Check sessions
    sessions_dir = Path("sessions")
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("session_*.json"))
        print(f"💾 Session files: {len(session_files)} found")
        
        if session_files:
            latest_session = max(session_files, key=lambda x: x.stat().st_mtime)
            print(f"📅 Latest session: {latest_session.name}")
    else:
        print("💾 No sessions directory yet")
    
    print()
    print("=" * 50)
    print("💡 TO VIEW MORE DETAILED DATA:")
    print("   python scripts/view_my_data.py")
    print()
    print("🧘 TO START TRACKING DATA:")
    print("   python yoga_coach_simple.py")
    print("=" * 50)

if __name__ == "__main__":
    main() 