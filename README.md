# 🧘 Yoga Pose Tracker with Performance-Focused Voice Coaching

Your Personal AI Yoga Instructor with **Achievement-Based Feedback**

## 🎯 **What Makes This Special**

✅ **Performance-Focused Narrator** - Only speaks on achievements and improvements  
✅ **Real Data Tracking** - Saves your actual angle measurements and personal bests  
✅ **Historical Comparison** - Compares current form to your own progress  
✅ **Achievement Celebration** - *"New personal best! 178.3 degrees - that's 2.1 degrees better!"*  
✅ **Privacy First** - All data stored locally, never shared  

---

## 🚀 **Quick Start**

### **Option 1: Simple Version (Works Immediately)**
```bash
python yoga_coach_simple.py
```
- ✅ Real angle measurements and data saving
- 🎯 Achievement-focused narrator 
- 📊 Personal best tracking
- 🔊 Uses macOS `say` command

### **Option 2: Full Version (Advanced)**
```bash
./scripts/install_yaml.sh    # Install PyYAML first
./run_yoga_coach.sh          # Run full system
```
- 📈 Historical trend analysis (30-day averages)
- ⚙️ YAML configuration (fully customizable)
- 📊 Advanced performance statistics
- 🎯 Sophisticated achievement detection

---

## 📊 **What the Narrator Says**

### **🔊 Example Voice Feedback:**
```
🎙️ "Outstanding! New personal best standing leg in Tree Pose: 
     178.3 degrees! That's 1.4 degrees better than your 
     previous best of 176.9!"

🎙️ "Great improvement! Your front knee is 3.2 degrees better 
     than your average of 89.1. Current: 92.3 degrees!"

🎙️ "Excellent form! Standing leg in Tree Pose: 178.3 degrees - 
     very precise!"
```

### **📱 Console Output:**
```
📐 REAL ANGLE DATA SAVED:
   🎯 standing leg: 178.3°
   🏆 Personal best: 178.3°
   📊 Total tree_pose measurements: 7
   💾 Saved to: data/simple_history.json
```

---

## 🗂️ **Project Structure**

```
yoga_pose_tracker/
├── 🧘 MAIN APPLICATIONS
│   ├── yoga_coach_simple.py       # ⭐ Simple version (recommended start)
│   ├── yoga_coach_performance.py  # 📊 Full version with history
│   └── run_yoga_coach.sh          # 🚀 Auto-launcher script
│
├── 📊 CORE MODULES  
│   ├── pose_utils.py              # 👁️ Pose detection & comparison
│   ├── angle_analyzer.py          # 📐 Critical angle analysis
│   ├── pose_database.py           # 🗄️ Optimized pose matching
│   ├── performance_tracker.py     # 📈 Historical data tracking
│   └── performance_narrator.py    # 🎙️ Achievement-focused voice
│
├── ⚙️ CONFIGURATION
│   ├── config.yaml               # 🔧 YAML settings (full version)
│   ├── requirements.txt          # 📦 Python dependencies
│   └── .gitignore               # 🚫 Privacy protection
│
├── 📁 DIRECTORIES
│   ├── data/                    # 📊 Your performance data (PRIVATE)
│   ├── sessions/                # 💾 Session recordings (PRIVATE)  
│   ├── positions/               # 📸 Reference pose images (PRIVATE)
│   ├── pose_database/           # 🗄️ Processed pose data
│   ├── scripts/                 # 🛠️ Utility scripts
│   ├── tests/                   # 🧪 Debug tools
│   ├── archive/                 # 📁 Old versions
│   └── docs/                    # 📚 Documentation
│
└── 📚 DOCUMENTATION
    ├── README.md                # 📖 This file
    └── docs/DATA_STORAGE.md     # 📊 Data storage guide
```

---

## 💾 **Your Data is Saved Here**

All your practice data is stored **locally and privately**:

- **`data/simple_history.json`** - Every angle measurement
- **`data/simple_bests.json`** - Your personal best records  
- **`sessions/session_*.json`** - Complete session recordings
- **`positions/`** - Your reference pose images

**View your data:** `python scripts/check_my_data.py`

---

## 🛠️ **Setup & Installation**

### **Prerequisites:**
- Python 3.9+ 
- macOS (for voice synthesis)
- Webcam

### **Installation:**
```bash
# Clone or download this project
cd yoga_pose_tracker

# Option 1: Quick setup (simple version)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python yoga_coach_simple.py

# Option 2: Full setup (all features)  
./scripts/setup.sh
./scripts/install_yaml.sh
./run_yoga_coach.sh
```

---

## 🎯 **Narrator Behavior**

### **When the Narrator Speaks:**
- ✅ **High confidence poses** (85%+ similarity)
- ✅ **Personal best angles** achieved
- ✅ **Daily best** measurements
- ✅ **Significant improvements** vs your average
- ✅ **Excellent form** (within 5° of target)

### **When the Narrator is Silent:**
- 🔇 Low confidence pose detection
- 🔇 Normal/average measurements  
- 🔇 During cooldown periods (10s default)
- 🔇 Unknown poses

### **Configuration:**
Edit `config.yaml` to customize:
- Confidence thresholds
- Feedback frequency  
- Voice messages
- Tracked angles per pose

---

## 📸 **Setting Up Reference Poses**

1. **Add your pose images:**
   ```
   positions/
   ├── tree_pose/
   │   ├── tree1.jpg
   │   └── tree2.png  
   ├── warrior_2/
   └── downward_dog/
   ```

2. **Process images:**
   ```bash
   python scripts/process_images.py
   ```

3. **Start practicing:**
   ```bash
   python yoga_coach_simple.py
   ```

---

## 🎛️ **Scripts & Utilities**

- **`scripts/setup.sh`** - Complete project setup
- **`scripts/install_yaml.sh`** - Install PyYAML for full version
- **`scripts/process_images.py`** - Convert images to pose database  
- **`scripts/check_my_data.py`** - View your saved data
- **`scripts/view_my_data.py`** - Detailed data analysis

---

## 🔧 **Troubleshooting**

### **"No module named 'yaml'"**
```bash
./scripts/install_yaml.sh
# OR use simple version: python yoga_coach_simple.py
```

### **Voice not working**
- The narrator will show text output if voice fails
- Simple version uses macOS `say` command (very reliable)
- Full version requires PyYAML + proper config

### **Poses not recognized**
```bash
# Process your reference images first
python scripts/process_images.py

# Check pose database
ls pose_database/

# Debug pose detection
python tests/debug_poses.py
```

### **No data being saved**
```bash
# Check if data directory exists
python scripts/check_my_data.py

# Simple version auto-creates data/ directory
# Make sure you're holding poses for 3+ seconds with 85%+ confidence
```

---

## 🔒 **Privacy & Data**

- 🏠 **100% Local** - No cloud, no servers, no internet required
- 🔒 **Private by Default** - Your data never leaves your computer  
- 📊 **Git-Ignored** - Personal data excluded from version control
- 💾 **Backup Friendly** - Standard JSON files, easy to backup

**Read more:** [`docs/DATA_STORAGE.md`](docs/DATA_STORAGE.md)

---

## 🎯 **Performance Tracking Examples**

### **Personal Best Celebration:**
```
🎙️ "Outstanding! New personal best standing leg in Tree Pose: 
     178.3 degrees! That's 1.4 degrees better than your 
     previous best of 176.9!"
```

### **Improvement Recognition:**
```  
🎙️ "Excellent progress! Your front knee is 3.2 degrees better 
     than your 30-day average of 89.2 degrees. 
     Current measurement: 92.4 degrees!"
```

### **Daily Achievement:**
```
🎙️ "Great work! Best knee angle today: 92.4 degrees in Warrior Two!"
```

---

## 🧘 **Supported Poses**

Currently optimized for:
- **Tree Pose** - Standing leg stability, lifted leg position, spine alignment
- **Warrior II** - Front knee angle, back leg extension, hip alignment  
- **Downward Dog** - Shoulder angle, hip position, leg extension

**Adding new poses:** Place reference images in `positions/{pose_name}/` and run `scripts/process_images.py`

---

## 🏆 **Achievement System**

The narrator celebrates:
- **🥇 Personal Bests** - All-time best angles
- **🎯 Daily Bests** - Best today  
- **📈 Improvements** - Better than your average
- **✨ Excellent Form** - Near-perfect alignment
- **🎉 First Measurements** - Building your baseline

---

## 🔮 **Future Features**

- 📊 Progress visualization charts
- 📱 Mobile app integration  
- 🤝 Multiple pose sequences
- 🎯 Custom target angles
- 📈 Weekly/monthly progress reports

---

## 🤝 **Contributing**

This project is designed to be your personal yoga coach. Feel free to:
- Add new poses and reference images
- Customize the narrator messages  
- Adjust angle tracking for your needs
- Share improvements (without personal data)

---

## ✨ **Happy Practicing!**

Your AI yoga coach is ready to track your progress and celebrate your achievements! 

**Start simple:** `python yoga_coach_simple.py`  
**Go advanced:** `./run_yoga_coach.sh`  
**Check progress:** `python scripts/check_my_data.py`

🧘‍♀️ **Namaste!** 🏆
