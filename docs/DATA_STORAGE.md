# 📊 User Data Storage Guide

## 🗂️ Where Your Yoga Data is Saved

Your personal yoga practice data is stored **locally** and **privately** on your computer. Here's exactly where:

### 📁 **Main Data Directories:**

```
yoga_pose_tracker/
├── data/                           # 📊 Performance tracking data (PRIVATE)
│   ├── performance_history.json   # 📈 All your angle measurements over time
│   ├── daily_stats.json          # 🗓️ Daily best records
│   └── personal_bests.json       # 🏆 All-time personal bests
├── sessions/                      # 💾 Yoga session recordings (PRIVATE)
│   ├── session_20241223_143052.json
│   └── session_20241223_151234.json
└── positions/                     # 📸 Your reference pose images (PRIVATE)
    ├── tree_pose/
    ├── warrior_2/
    └── downward_dog/
```

---

## 📈 **Performance Data Details**

### 🎯 **`data/performance_history.json`**
**Complete record of every angle measurement:**
```json
[
  {
    "pose": "tree_pose",
    "angle_name": "standing_leg",
    "value": 178.3,
    "timestamp": "2024-12-23T14:30:52.123456",
    "session_id": "20241223_143052"
  },
  {
    "pose": "warrior_2", 
    "angle_name": "front_knee",
    "value": 92.4,
    "timestamp": "2024-12-23T14:31:15.987654",
    "session_id": "20241223_143052"
  }
]
```

### 🏆 **`data/personal_bests.json`**
**Your all-time best angles:**
```json
{
  "tree_pose_standing_leg": {
    "value": 178.3,
    "date": "2024-12-23",
    "session_id": "20241223_143052"
  },
  "warrior_2_front_knee": {
    "value": 94.8,
    "date": "2024-12-22", 
    "session_id": "20241222_090123"
  }
}
```

### 🗓️ **`data/daily_stats.json`**
**Best performance each day:**
```json
{
  "2024-12-23": {
    "tree_pose_standing_leg": {
      "value": 178.3,
      "timestamp": "2024-12-23T14:30:52.123456"
    },
    "warrior_2_front_knee": {
      "value": 92.4,
      "timestamp": "2024-12-23T14:31:15.987654"
    }
  }
}
```

---

## 💾 **Session Data**

### 📝 **`sessions/session_YYYYMMDD_HHMMSS.json`**
**Complete session recordings:**
```json
{
  "session_start": "2024-12-23 14:30:52",
  "session_end": "2024-12-23 14:45:30",
  "duration_seconds": 878,
  "total_frames": 8234,
  "frames": [
    {
      "timestamp": "14:30:52.123",
      "frame_number": 100,
      "detected_pose": "tree_pose",
      "similarity_score": 0.15,
      "confidence": 0.85,
      "keypoints": { ... }
    }
  ]
}
```

---

## 🔒 **Privacy & Security**

### ✅ **What's Private (NOT in Git):**
- ✅ `data/` - All your performance measurements
- ✅ `sessions/` - Your practice session recordings  
- ✅ `positions/` - Your personal reference pose images

### 📂 **What's Shared (In Git):**
- ✅ Source code and scripts
- ✅ Configuration files
- ✅ Documentation
- ✅ Empty directory structure (`.gitkeep` files)

---

## 🔍 **Viewing Your Data**

### 📊 **Quick Data Summary:**
```bash
# View your personal bests
cat data/personal_bests.json | python -m json.tool

# View recent session
ls -la sessions/ | tail -5

# Count total measurements
cat data/performance_history.json | python -c "import json, sys; data=json.load(sys.stdin); print(f'Total measurements: {len(data)}')"
```

### 📈 **Data Analysis Scripts** (Coming Soon):
- `scripts/view_progress.py` - Weekly/monthly progress charts
- `scripts/export_data.py` - Export to CSV for analysis
- `scripts/backup_data.py` - Backup your practice data

---

## 💡 **What the Narrator Sees & Says**

When the narrator speaks, he's comparing your **current angle measurement** to:

### 🎯 **Real-Time Analysis:**
- **Current angle:** *"Your knee angle is 92.4 degrees"*
- **vs Personal Best:** *"That's 2.1 degrees better than your best of 90.3!"*  
- **vs Daily Best:** *"Best knee angle today - 92.4 degrees!"*
- **vs 30-Day Average:** *"3.2 degrees better than your average of 89.2!"*

### 📊 **Example Narrator Messages:**
```
🎙️ "Outstanding! New personal best standing leg in Tree Pose: 
     178.3 degrees! That's 1.4 degrees better than your 
     previous best of 176.9!"

🎙️ "Excellent progress! Your front knee is 3.2 degrees better 
     than your 30-day average of 89.2 degrees. 
     Current measurement: 92.4 degrees!"
```

---

## 🛡️ **Data Backup Recommendations**

Your yoga data is **valuable progress tracking** - consider backing it up:

```bash
# Backup all your yoga data
cp -r data/ ~/Documents/yoga_backup_$(date +%Y%m%d)/
cp -r sessions/ ~/Documents/yoga_backup_$(date +%Y%m%d)/

# Or create a zip backup
zip -r yoga_data_backup_$(date +%Y%m%d).zip data/ sessions/
```

---

## 🧘 **Your Data, Your Privacy**

- 🏠 **Stored locally** - Never sent to cloud or servers
- 🔒 **Private by default** - Excluded from Git sharing
- 📈 **Builds over time** - More data = better comparisons
- 🎯 **Achievement focused** - Celebrates your real progress

**Happy practicing! Your progress is being tracked and celebrated! 🏆** 