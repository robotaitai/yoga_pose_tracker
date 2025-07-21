#!/usr/bin/env python3
"""
📊 View Your Yoga Data

Shows your current progress, personal bests, and recent sessions.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def main():
    print("=" * 60)
    print("📊 YOUR YOGA PRACTICE DATA")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('../data') and not os.path.exists('data'):
        print("❌ No data directory found!")
        print("💡 Run this from the yoga_pose_tracker directory")
        return
    
    data_dir = Path('data') if os.path.exists('data') else Path('../data')
    sessions_dir = Path('sessions') if os.path.exists('sessions') else Path('../sessions')
    
    # Check what data exists
    performance_file = data_dir / 'performance_history.json'
    personal_bests_file = data_dir / 'personal_bests.json'
    daily_stats_file = data_dir / 'daily_stats.json'
    
    print(f"📁 Data directory: {data_dir.absolute()}")
    print(f"💾 Sessions directory: {sessions_dir.absolute()}")
    print()
    
    # Performance History
    print("📈 PERFORMANCE HISTORY")
    print("-" * 30)
    
    if performance_file.exists():
        try:
            with open(performance_file, 'r') as f:
                history = json.load(f)
            
            print(f"✅ Total measurements recorded: {len(history)}")
            
            if history:
                # Recent measurements
                recent = history[-5:] if len(history) >= 5 else history
                print(f"🕐 Most recent measurements:")
                for measurement in recent:
                    timestamp = datetime.fromisoformat(measurement['timestamp'])
                    print(f"   • {measurement['pose'].replace('_', ' ').title()}: "
                          f"{measurement['angle_name'].replace('_', ' ')} = "
                          f"{measurement['value']:.1f}° "
                          f"({timestamp.strftime('%m/%d %H:%M')})")
                
                # Poses practiced
                poses = set([m['pose'] for m in history])
                print(f"🧘 Poses practiced: {', '.join([p.replace('_', ' ').title() for p in poses])}")
            
        except Exception as e:
            print(f"❌ Error reading performance history: {e}")
    else:
        print("📝 No performance history yet - start practicing to build your data!")
    
    print()
    
    # Personal Bests
    print("🏆 PERSONAL BESTS")
    print("-" * 20)
    
    if personal_bests_file.exists():
        try:
            with open(personal_bests_file, 'r') as f:
                bests = json.load(f)
            
            if bests:
                for key, record in bests.items():
                    pose, angle = key.split('_', 1)
                    pose_name = pose.replace('_', ' ').title()
                    angle_name = angle.replace('_', ' ')
                    date = record['date']
                    value = record['value']
                    print(f"   🎯 {pose_name} - {angle_name}: {value:.1f}° (set on {date})")
            else:
                print("   📈 No personal bests recorded yet!")
                
        except Exception as e:
            print(f"❌ Error reading personal bests: {e}")
    else:
        print("   🎯 No personal bests file yet - achieve some milestones!")
    
    print()
    
    # Daily Stats (Last 7 days)
    print("📅 RECENT DAILY BESTS (Last 7 days)")
    print("-" * 40)
    
    if daily_stats_file.exists():
        try:
            with open(daily_stats_file, 'r') as f:
                daily_stats = json.load(f)
            
            # Get last 7 days
            today = datetime.now().date()
            recent_days = [(today - timedelta(days=i)).isoformat() for i in range(7)]
            
            found_recent = False
            for day in recent_days:
                if day in daily_stats:
                    found_recent = True
                    print(f"   📅 {day}:")
                    for key, record in daily_stats[day].items():
                        pose, angle = key.split('_', 1)
                        pose_name = pose.replace('_', ' ').title()
                        angle_name = angle.replace('_', ' ')
                        value = record['value']
                        timestamp = datetime.fromisoformat(record['timestamp'])
                        print(f"      • {pose_name} - {angle_name}: {value:.1f}° "
                              f"({timestamp.strftime('%H:%M')})")
            
            if not found_recent:
                print("   📝 No recent daily bests - practice more to see progress!")
                
        except Exception as e:
            print(f"❌ Error reading daily stats: {e}")
    else:
        print("   📊 No daily stats file yet!")
    
    print()
    
    # Sessions
    print("💾 RECENT SESSIONS")
    print("-" * 20)
    
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob('session_*.json'))
        session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if session_files:
            print(f"✅ Total sessions recorded: {len(session_files)}")
            print(f"📋 Most recent sessions:")
            
            for i, session_file in enumerate(session_files[:5]):  # Show last 5
                try:
                    with open(session_file, 'r') as f:
                        session = json.load(f)
                    
                    duration = session.get('duration_seconds', 0)
                    duration_min = duration // 60
                    duration_sec = duration % 60
                    start_time = session.get('session_start', 'Unknown')
                    frames = len(session.get('frames', []))
                    
                    print(f"   {i+1}. {session_file.name}")
                    print(f"      ⏰ {start_time} ({duration_min}m {duration_sec}s)")
                    print(f"      🎞️ {frames} recorded frames")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {session_file.name}: {e}")
        else:
            print("   📝 No sessions recorded yet!")
    else:
        print("   📁 Sessions directory not found!")
    
    print()
    print("=" * 60)
    print("💡 TIPS:")
    print("   • Your data builds over time for better comparisons")
    print("   • All data is stored locally and privately")
    print("   • The narrator compares your current angles to this history")
    print("   • Back up your data/ and sessions/ folders to preserve progress")
    print("=" * 60)
    print("🧘 Keep practicing to build your performance history! 🏆")

if __name__ == "__main__":
    main() 