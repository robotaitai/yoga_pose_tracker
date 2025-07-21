# 🧘 Yoga Coach - Voice-Enabled Pose Tracker

Your Personal AI Yoga Instructor with Real-time Voice Feedback

## ✨ Features

- **🎙️ Voice Coaching**: Real-time spoken feedback using macOS text-to-speech
- **📐 Critical Angle Analysis**: Measures joint angles and provides form corrections
- **🧘 Smart Pose Recognition**: Detects Tree Pose, Warrior 2, Downward Dog, and more
- **📊 Performance Tracking**: Session statistics and improvement tracking
- **🔊 Intelligent Feedback**: Priority-based coaching with breathing reminders
- **💾 Session Recording**: Saves detailed session data for progress tracking

## 🚀 Quick Start

### 1. Setup (First Time Only)
```bash
# Run the setup script
./scripts/setup.sh

# This will:
# - Create virtual environment
# - Install all dependencies
# - Configure VS Code settings
```

### 2. Add Reference Poses
Create your pose reference images:
```
positions/
├── tree_pose/
│   ├── tree1.jpg
│   └── tree2.png
├── warrior_2/
│   ├── warrior1.jpg
│   └── warrior2.png
└── downward_dog/
    ├── dog1.jpg
    └── dog2.png
```

### 3. Start Yoga Coaching
```bash
# Run the main application
./run_yoga_coach.sh

# Or manually:
source venv/bin/activate
python yoga_coach.py
```

## 🎯 How It Works

1. **Camera opens** - Position yourself in front of the camera
2. **Voice coaching begins** - Your computer will speak guidance
3. **Pose detection** - AI recognizes your yoga poses in real-time
4. **Form analysis** - Critical angles are measured (knee bends, spine alignment, etc.)
5. **Voice feedback** - Immediate spoken corrections and encouragement
6. **Session tracking** - Performance data is saved automatically

## 🔊 Voice Coaching Examples

- *"Entering Tree Pose. Focus on your alignment."*
- *"Critical adjustment: Straighten your standing leg more."*
- *"Excellent form! Beautiful pose."*
- *"Remember to breathe deeply. Inhale strength, exhale tension."*
- *"Session complete! You practiced 3 poses with an average score of 82 percent."*

## 📁 Project Structure

```
yoga_pose_tracker/
├── 🧘 yoga_coach.py          # Main voice-enabled application
├── 🛠️ pose_utils.py           # Core pose detection and comparison
├── 📐 angle_analyzer.py       # Critical angle analysis and feedback
├── 💾 pose_database.py        # Optimized pose database system
├── ⚙️ requirements.txt        # Python dependencies
├── 🚀 run_yoga_coach.sh       # Main run script
│
├── 📁 scripts/               # Utility scripts
│   ├── setup.sh             # Environment setup
│   └── process_images.py    # Image processing for pose database
│
├── 📁 tests/                # Debug and testing tools
│   └── debug_poses.py       # Pose recognition troubleshooting
│
├── 📁 positions/            # Reference pose images (you add these)
├── 📁 sessions/             # Saved session data
├── 📁 pose_database/        # Processed pose database
└── 📁 venv/                 # Python virtual environment
```

## 🎮 Usage Instructions

### During Your Session

- **Position yourself** fully in the camera frame
- **Listen for voice guidance** as you practice poses
- **Hold poses** for 5-10 seconds to get detailed feedback
- **Follow voice corrections** for better form
- **Press 'q'** in the camera window to end session

### Pose Requirements

For best recognition:
- **Full body visible** in camera frame
- **Good lighting** and uncluttered background
- **Hold poses steadily** for at least 5 seconds
- **Face the camera** for frontal poses

## 🔧 Advanced Usage

### Adding New Poses

1. Create a new directory in `positions/` (e.g., `positions/new_pose/`)
2. Add reference images of the pose
3. Run: `python scripts/process_images.py`
4. Restart yoga coach

### Troubleshooting

```bash
# Debug pose recognition issues
python tests/debug_poses.py

# Check system status
python -c "import cv2, mediapipe as mp; print('✅ All systems ready')"

# Re-process images if poses not recognized
python scripts/process_images.py
```

### Voice Settings

Edit `yoga_coach.py` to customize:
- Speech rate: `YogaVoiceCoach(speech_rate=180)`
- Feedback frequency: Adjust `feedback_cooldown` value
- Breathing reminders: Modify reminder interval

## 📊 Performance Metrics

The system tracks:
- **Form scores** (0-100%) for each pose
- **Critical angle measurements** (degrees)
- **Session duration** and poses practiced
- **Improvement trends** over time
- **Best poses** and personal records

## 🔍 Troubleshooting

### Common Issues

**❌ "No pose detected"**
- Ensure full body is visible in camera
- Check lighting and background
- Run `python tests/debug_poses.py`

**❌ "Voice not working"**
- macOS only - uses built-in `say` command
- Check system audio settings
- Voice will fallback to text display

**❌ "No reference poses found"**
- Add images to `positions/` directory
- Run `python scripts/process_images.py`
- Check image formats (jpg, png supported)

**❌ "Virtual environment not found"**
- Run `./scripts/setup.sh` first
- Ensure you're in the project directory

## 🎯 Tips for Best Results

### Pose Performance
- Start with basic poses (Tree, Warrior 2)
- Hold poses steadily for detailed analysis
- Focus on one improvement at a time
- Practice regularly for progress tracking

### Camera Setup
- Position camera at chest height
- Ensure stable lighting
- Clear background behind you
- Stay within camera frame boundaries

### Voice Coaching
- Keep speakers/headphones on
- Follow voice guidance patiently
- Don't rush between pose corrections
- Listen for breathing reminders

## 🛠️ Technical Requirements

- **macOS** (for voice synthesis)
- **Python 3.8+**
- **Webcam**
- **Speakers or headphones**
- **Good lighting** for pose detection

### Dependencies
- OpenCV (computer vision)
- MediaPipe (pose detection)
- NumPy (numerical processing)
- Built-in macOS text-to-speech

## 📈 Session Data

Sessions are automatically saved to `sessions/` with:
- Timestamp and duration
- Detected poses and form scores
- Critical angle measurements
- Performance statistics
- Keypoint data for analysis

## 🧘 Getting Started with Yoga

New to yoga? The system includes beginner-friendly feedback:
- **Tree Pose**: Focus on balance and alignment
- **Warrior 2**: Work on leg strength and hip opening
- **Downward Dog**: Build upper body and core strength

Listen to the voice coaching for proper form guidance!

## 🎉 Enjoy Your Practice!

Your personal AI yoga instructor is ready to help you improve your practice with real-time voice coaching and intelligent form analysis. 

**Namaste!** 🙏

---

*For technical support or feature requests, check the troubleshooting section or run the debug tools.*
