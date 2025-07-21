#!/bin/bash
# Yoga Pose Tracker - Setup Script
# Sets up the virtual environment and installs all dependencies

echo "🧘 Yoga Pose Tracker - Setup"
echo "=" * 40

# Get the script directory and move to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📁 Project directory: $PROJECT_ROOT"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    if ! pip install -r requirements.txt; then
        echo "⚠️  Failed to install from requirements.txt, installing manually..."
        pip install opencv-python numpy pyttsx3
        pip install mediapipe --no-compile
    fi
else
    echo "Installing core packages..."
    pip install opencv-python numpy pyttsx3
    pip install mediapipe --no-compile
fi

# Test installation
echo "🧪 Testing installation..."
python -c "import cv2, mediapipe as mp, numpy as np; print('✅ All packages imported successfully')"

# Set up VS Code settings if .vscode doesn't exist
if [ ! -d ".vscode" ]; then
    echo "⚙️  Setting up VS Code configuration..."
    mkdir -p .vscode
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "*.py": "python"
    }
}
EOF
fi

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start using Yoga Coach:"
echo "   1. Activate the environment: source venv/bin/activate"
echo "   2. Run the yoga coach: python yoga_coach.py"
echo ""
echo "📖 Or use the convenience script: ./run_yoga_coach.sh" 