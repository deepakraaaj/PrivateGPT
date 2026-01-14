#!/bin/bash
echo "🚀 Starting FastQwenRunner Setup..."

# Check if python3.10 exists
if ! command -v python3.10 &> /dev/null; then
    echo "❌ Error: python3.10 could not be found. Please install it."
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.10 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "⬇️ Installing dependencies..."
pip install -r requirements.txt

# Run server
echo "🔥 Starting Server..."
echo "👉 API Docs: http://localhost:8001/docs"
python main.py
