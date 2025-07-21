#!/bin/bash
# 🔧 Install PyYAML for Performance Yoga Coach

echo "🔧 Installing PyYAML for Performance Yoga Coach..."

# Ensure we're in the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📂 Working in: $PROJECT_ROOT"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run setup first: ./scripts/setup.sh"
    exit 1
fi

source venv/bin/activate

echo "📦 Installing PyYAML..."
pip install PyYAML

if [ $? -eq 0 ]; then
    echo "✅ PyYAML installed successfully!"
    echo ""
    echo "🧘 Now you can run the full performance coach:"
    echo "   ./run_yoga_coach.sh"
    echo ""
    echo "🎯 Testing the installation..."
    python -c "import yaml; print('✅ YAML import successful!')"
    if [ $? -eq 0 ]; then
        echo ""
        echo "🚀 Everything ready! Run: ./run_yoga_coach.sh"
    else
        echo "❌ YAML import failed"
    fi
else
    echo "❌ Failed to install PyYAML"
    echo "🔄 Trying alternative method..."
    pip install --upgrade pip
    pip install pyyaml
fi 