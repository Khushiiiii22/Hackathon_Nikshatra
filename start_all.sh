#!/bin/bash

# MIMIQ Complete Startup Script
# Starts both backend and frontend servers

echo "🏥 MIMIQ Medical AI Platform - Startup"
echo "========================================"
echo ""

# Check if backend is already running
if lsof -ti:5000 > /dev/null 2>&1; then
    echo "⚠️  Backend already running on port 5000"
else
    echo "🚀 Starting backend on port 5000..."
    cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
    source .venv/bin/activate
    python backend_simple.py &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
fi

echo ""

# Check if frontend is already running
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "⚠️  Frontend already running on port 5173"
else
    echo "🚀 Starting frontend on port 5173..."
    cd /Users/khushi22/Hackathon/Hackathon_Nikshatra/frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
fi

echo ""
echo "========================================"
echo "✅ MIMIQ is ready!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
