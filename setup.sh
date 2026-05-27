#!/bin/bash
set -e

echo "=== AICodePR Setup ==="

# Check Python
python3 --version || { echo "Python 3 required"; exit 1; }

# Create venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi

source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -q
echo "Dependencies installed"

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "============================================"
    echo "  ACTION REQUIRED: Edit .env with your keys"
    echo "============================================"
    echo ""
    echo "  You need:"
    echo "    1. GitHub App credentials (see SETUP.md)"
    echo "    2. DeepSeek API key"
    echo ""
    echo "  Then run: ./start.sh"
    echo ""
    exit 0
fi

# Run
echo "Starting server on http://0.0.0.0:8000"
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
