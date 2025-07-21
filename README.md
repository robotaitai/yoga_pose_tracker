# Yoga Pose Tracker

A real-time yoga pose detection and tracking system that uses your webcam to identify yoga poses and save session data locally. The system compares your current pose against reference poses using MediaPipe for pose detection.

## Features

- **Real-time pose detection** using MediaPipe
- **Command-line interface** - no GUI required
- **Local data storage** - all data stored locally, no cloud dependencies
- **Pose comparison** with customizable similarity thresholds
- **Session tracking** with automatic data saving
- **Reference pose capture** functionality
- **Cross-platform** compatibility (Windows, Mac, Linux)

## Project Structure

```
yoga_pose_tracker/
├── positions/          # Reference pose data
│   ├── warrior_2/
│   │   ├── ref1.json
│   │   └── ref2.json
│   ├── downward_dog/
│   │   └── ref1.json
│   ├── tree_pose/
│   │   └── ref1.json
│   └── [add more poses here]
├── sessions/           # Session data (auto-generated)
│   └── [session files with timestamps]
├── main.py            # Main application entry point
├── pose_utils.py      # Core pose detection and comparison logic
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Requirements

- Python 3.7 or higher
- Webcam/camera connected to your computer
- Operating System: Windows, macOS, or Linux

## Installation

### Option 1: Automated Setup (Recommended)

1. **Clone or download** this project to your local machine

2. **Navigate** to the project directory:
   ```bash
   cd yoga_pose_tracker
   ```

3. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

This will automatically:
- Create a virtual environment using Python 3.9
- Install all required dependencies with compatible versions
- Configure VS Code settings for automatic environment detection
- Set up scripts for easy activation

### Option 2: Manual Setup

1. **Create a virtual environment**:
   ```bash
   /usr/bin/python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install opencv-python numpy
   pip install mediapipe --no-compile
   ```

   *Note: The `--no-compile` flag is needed for MediaPipe compatibility with some Python versions.*

### Option 3: Quick Setup Check

If the environment is already set up, you can verify everything works:
```bash
./run.sh --help
```

## Usage

### Automatic Environment Activation

The project supports several ways to automatically activate the virtual environment:

#### Option 1: Use the run script (Simplest)
```bash
./run.sh                    # Start pose tracking
./run.sh --capture         # Capture new reference poses
```

#### Option 2: Use the activation script
```bash
source activate.sh         # Activates venv and starts a new shell
python main.py             # Run the tracker
```

#### Option 3: Use direnv (Auto-activation when entering directory)
```bash
# First time setup
brew install direnv        # or install via your package manager
direnv allow              # Allow direnv to activate the environment

# Now the environment activates automatically when you cd into the directory
cd yoga_pose_tracker      # Environment auto-activates
python main.py            # Ready to run!
```

#### Option 4: Manual activation
```bash
source venv/bin/activate   # Activate manually
python main.py            # Run the tracker
```

### Basic Pose Tracking

To start the yoga pose tracker:

```bash
./run.sh                   # Using run script (recommended)
# OR
python main.py            # If environment is already activated
```

**Instructions:**
1. Position yourself in front of your webcam
2. The camera window will open showing your live feed
3. Perform yoga poses - detected poses will be displayed on screen and in the terminal
4. Press 'q' in the camera window to stop and save your session

**Console Output Example:**
```
[00:00:05] Detected pose: warrior_2 (score: 0.082)
[00:00:12] Detected pose: downward_dog (score: 0.156)
[00:00:18] Detected pose: tree_pose (score: 0.093)
[00:00:25] Detected pose: unknown
```

### Capturing Reference Poses

To add new reference poses to your collection:

```bash
./run.sh --capture         # Using run script (recommended)
# OR
python main.py --capture   # If environment is already activated
```

This will start an interactive pose capture session where you can:
1. Enter the name of a new pose
2. Position yourself in that pose
3. Press SPACE to capture the pose
4. The pose will be automatically saved to the `positions/` directory

## Data Formats

### Reference Pose Format

Each reference pose is stored as a JSON file in `positions/[pose_name]/`:

```json
{
  "pose_name": "warrior_2",
  "keypoints": {
    "left_shoulder": [0.400, 0.280],
    "right_shoulder": [0.600, 0.280],
    "left_hip": [0.430, 0.520],
    "right_hip": [0.570, 0.520],
    ...
  }
}
```

Coordinates are normalized (0.0 to 1.0) relative to image dimensions.

### Session Data Format

Session data is automatically saved to `sessions/session_YYYY-MM-DD_HH-MM-SS.json`:

```json
{
  "session_start": "2024-01-15 14:30:25",
  "session_end": "2024-01-15 14:35:12",
  "duration_seconds": 287,
  "total_frames": 8610,
  "frames": [
    {
      "timestamp": "14:30:26.123",
      "frame_number": 10,
      "detected_pose": "warrior_2",
      "similarity_score": 0.082,
      "keypoints": {
        "left_shoulder": [0.398, 0.285],
        ...
      }
    }
  ]
}
```

## Adding New Poses

### Method 1: Using the Capture Tool (Recommended)

1. Run the capture tool:
   ```bash
   python main.py --capture
   ```

2. Enter the pose name when prompted
3. Position yourself in the pose
4. Press SPACE to capture

### Method 2: Manual Creation

1. Create a new folder in `positions/` with your pose name (use underscores instead of spaces)
2. Create reference JSON files following the format above
3. You can capture keypoints using any MediaPipe pose detection script

### Method 3: Using the Helper Function

You can also use the capture function programmatically:

```python
from pose_utils import PoseDataManager, capture_reference_pose

data_manager = PoseDataManager()
success = capture_reference_pose("my_new_pose", data_manager)
```

## Configuration

### Similarity Threshold

You can adjust the pose matching sensitivity by modifying the `similarity_threshold` parameter in `main.py`:

```python
comparator = PoseComparator(similarity_threshold=0.15)  # Lower = more strict
```

- **Lower values** (0.05-0.10): More strict matching, fewer false positives
- **Higher values** (0.20-0.30): More lenient matching, may catch variations better

### Camera Settings

Modify camera properties in `main.py`:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Height
cap.set(cv2.CAP_PROP_FPS, 30)            # Frame rate
```

## Troubleshooting

### Camera Issues

**Problem**: "Error: Could not open webcam!"
- **Solution**: Ensure your camera is connected and not being used by another application
- Try changing the camera index: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`

### Performance Issues

**Problem**: Slow performance or high CPU usage
- **Solution**: Reduce camera resolution or frame rate in the camera settings
- Close other applications using the camera

### Pose Detection Issues

**Problem**: "No pose detected" frequently appears
- **Solution**: Ensure good lighting and that your full body is visible in the camera
- Stand further back from the camera to capture your full body
- Ensure there's good contrast between you and the background

### Import Errors

**Problem**: `ImportError` for mediapipe, cv2, or numpy
- **Solution**: Reinstall dependencies: `pip install -r requirements.txt`
- Try using a virtual environment: `python -m venv venv && source venv/bin/activate`

## Technical Details

### Pose Comparison Algorithm

The system uses a normalized joint distance algorithm:

1. **Normalization**: Poses are normalized using hip center and torso length
2. **Key Joints**: Focuses on main body joints (shoulders, elbows, wrists, hips, knees, ankles)
3. **Distance Calculation**: Uses Euclidean distance between corresponding joints
4. **Similarity Score**: Mean squared error of joint distances (lower = more similar)

### MediaPipe Integration

- Uses MediaPipe Pose for real-time pose detection
- Extracts 33 body landmarks with normalized coordinates
- Optimized for real-time performance with tracking

## Project Scripts

The project includes several convenience scripts for easy setup and usage:

- **`setup.sh`** - Complete project setup (creates venv, installs dependencies, configures VS Code)
- **`run.sh`** - Quick run script with automatic environment activation
- **`activate.sh`** - Manual environment activation script  
- **`.envrc`** - direnv configuration for automatic activation when entering directory

## Contributing

To add new features or improve the system:

1. The core pose detection is in `PoseDetector` class
2. Pose comparison logic is in `PoseComparator` class  
3. Data management is handled by `PoseDataManager` class
4. Main application flow is in `main.py`

## Limitations

- Requires good lighting and clear view of the person
- Works best with full-body poses where major joints are visible
- Similarity scoring may need adjustment for different pose types
- Single-person detection only

## Future Enhancements

- Multiple pose variations per reference pose
- Better pose similarity algorithms (angle-based comparison)
- Pose sequence tracking
- Performance analytics and progress tracking
- Export to different data formats

## License

This project is open source. Feel free to modify and distribute as needed.

---

For questions or issues, please check the troubleshooting section above or refer to the code comments for implementation details. # yoga_pose_tracker
