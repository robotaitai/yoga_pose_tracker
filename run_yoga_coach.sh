#!/bin/bash
# 🧘 Yoga Coach - Voice-Enabled Pose Tracker
# Main runner script for the yoga coaching system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧘 YOGA COACH - VOICE-ENABLED POSE TRACKER"
echo "=" * 50
echo "🎙️ Your Personal AI Yoga Instructor"
echo "🔊 Real-time voice feedback and form analysis"
echo "=" * 50

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run setup first: ./scripts/setup.sh"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if pose database exists
if [ ! -f "pose_database/pose_database.json" ]; then
    echo "⚠️  Pose database not found!"
    echo "💡 Processing reference images..."
    echo "   This may take a moment..."
    python scripts/process_images.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create pose database"
        echo "💡 Make sure you have images in the 'positions' directory"
        echo "📁 Expected structure:"
        echo "   positions/"
        echo "   ├── tree_pose/"
        echo "   │   ├── tree1.jpg"
        echo "   │   └── tree2.png"
        echo "   ├── warrior_2/"
        echo "   └── downward_dog/"
        exit 1
    fi
fi

echo "✅ Environment ready!"
echo ""
echo "🚀 Starting Yoga Coach..."
echo "📹 Your camera will open shortly"
echo "🔊 Make sure your speakers are on"
echo "⌨️  Press 'q' in the camera window to end session"
echo ""

# Run the yoga coach
python yoga_coach.py

echo ""
echo "✨ Thank you for practicing with Yoga Coach!"
echo "🧘 Namaste!" 