#!/bin/bash
# 🧘 Yoga Coach - Performance-Focused Pose Tracker
# Main runner script for the performance-tracking yoga coaching system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧘 PERFORMANCE-FOCUSED YOGA COACH"
echo "=" * 50
echo "🎯 Data-driven feedback based on your progress"
echo "📊 Only speaks on achievements and improvements"
echo "🏆 Tracks personal bests vs your history"
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

# Check if config file exists, create if needed
if [ ! -f "config.yaml" ]; then
    echo "⚙️  Creating default configuration file..."
    cat > config.yaml << 'EOF'
# 🧘 Yoga Coach - Configuration File

# Pose Detection Settings
pose_detection:
  similarity_threshold: 0.20        # How similar pose must be to reference (lower = stricter)
  confidence_threshold: 0.85        # Minimum confidence to trigger narrator (0-1)
  min_hold_time: 3.0               # Seconds to hold pose before analysis
  
# Narrator Behavior  
narrator:
  enabled: true
  speech_rate: 180                 # Words per minute
  
  # When to speak
  speak_on_performance: true       # Speak about performance only
  speak_on_improvement: true       # Celebrate improvements
  speak_on_personal_best: true     # Celebrate new personal bests
  
  # Feedback frequency
  feedback_cooldown: 10.0          # Seconds between feedback for same pose
  
# Performance Tracking
performance:
  track_angles: true               # Track angle measurements
  compare_to_history: true         # Compare current to historical performance
  history_days: 30                 # Days of history to consider
  improvement_threshold: 2.0       # Degrees improvement to celebrate
  
  # Angles to track per pose
  tracked_angles:
    tree_pose:
      - standing_leg
      - lifted_leg
      - spine_vertical
    warrior_2:
      - front_knee
      - back_leg  
      - hip_alignment
    downward_dog:
      - shoulder_angle
      - hip_angle
      - leg_extension

# Voice Messages (templates)
voice_messages:
  personal_best: "Excellent! New personal best for {pose} {angle}: {current_angle:.1f} degrees!"
  improvement: "Great progress! Your {angle} is {improvement:.1f} degrees better than your average."
  daily_best: "That's your best {angle} today - {current_angle:.1f} degrees!"
  session_summary: "Session complete! You achieved {num_improvements} improvements today."
EOF
    echo "✅ Created config.yaml"
fi

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
echo "🚀 Starting Performance Yoga Coach..."
echo "📹 Your camera will open shortly"
echo "🔊 Narrator will ONLY speak on achievements:"
echo "   🏆 Personal bests"
echo "   🎯 Daily bests" 
echo "   📈 Significant improvements"
echo "⌨️  Press 'q' in the camera window to end session"
echo ""

# Run the performance-focused yoga coach
python yoga_coach_performance.py

echo ""
echo "✨ Thank you for using Performance Yoga Coach!"
echo "📈 Your progress data has been saved!"
echo "🧘 Namaste!" 