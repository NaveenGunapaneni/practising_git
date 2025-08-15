#!/bin/bash

# GeoPulse API Environment Setup Script
# This script sets up the Python environment and starts the API server

echo "🚀 Setting up GeoPulse API Environment..."

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "📦 Using conda environment..."
    
    # Create conda environment from environment.yaml
    if [ -f "environment.yaml" ]; then
        echo "Creating conda environment from environment.yaml..."
        conda env create -f environment.yaml
    else
        echo "environment.yaml not found, creating basic environment..."
        conda create -n geopulse_env python=3.11 -y
    fi
    
    # Activate environment
    echo "Activating conda environment..."
    source activate geopulse_env
    
    # Install additional dependencies if needed
    echo "Installing additional dependencies..."
    pip install -r requirements.txt
    
elif command -v python3 &> /dev/null; then
    echo "🐍 Using Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv geopulse_env
    
    # Activate environment
    echo "Activating virtual environment..."
    source geopulse_env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    
else
    echo "❌ Python not found. Please install Python 3.11 or later."
    exit 1
fi

echo "✅ Environment setup complete!"
echo ""
echo "To start the API server, run:"
echo "  source geopulse_env/bin/activate  # (if using venv)"
echo "  # OR"
echo "  conda activate geopulse_env       # (if using conda)"
echo "  python main.py"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
