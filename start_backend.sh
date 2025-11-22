#!/bin/bash

# MIMIQ Backend Quick Start Script
# Run this script to start the backend server

cd /Users/khushi22/Hackathon/Hackathon_Nikshatra

echo "🏥 Starting MIMIQ Backend Server..."
echo "======================================"
echo ""
echo "✅ API Key: Loaded from .env"
echo "✅ Port: 5000"
echo "✅ Gemini Model: 2.5-flash"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

source .venv/bin/activate
python backend_simple.py
