#!/bin/bash

# Script để chạy FastAPI server

echo "Starting Financial Management API..."

# Kiểm tra virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    python3.12 -m venv venv || python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Kiểm tra và cài đặt dependencies
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Kiểm tra file .env
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create .env file with your configuration."
    exit 1
fi

# Chạy server
echo "Starting server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

