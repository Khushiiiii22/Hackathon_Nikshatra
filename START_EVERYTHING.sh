#!/bin/bash

# MIMIQ Medical AI Platform - Complete Startup Script
# This script starts both backend and frontend servers

echo "=========================================="
echo "🏥 MIMIQ Medical AI Platform"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "backend_simple.py" ]; then
    echo -e "${RED}❌ Error: backend_simple.py not found${NC}"
    echo "Please run this script from the Hackathon_Nikshatra directory"
    exit 1
fi

echo -e "${BLUE}📋 Pre-flight checks...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 found${NC}"
else
    echo -e "${RED}❌ Python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js found${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check .venv
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env file with GEMINI_API_KEY"
    exit 1
fi

echo ""
echo -e "${BLUE}🚀 Starting servers...${NC}"
echo ""

# Kill any existing processes on ports 5000 and 5173
echo -e "${YELLOW}Cleaning up old processes...${NC}"
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend in background
echo -e "${GREEN}Starting backend server (port 5000)...${NC}"
source .venv/bin/activate
python backend_simple.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if lsof -ti:5000 > /dev/null; then
    echo -e "${GREEN}✅ Backend running on http://localhost:5000${NC}"
else
    echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
    exit 1
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend server (port 5173)...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 8

# Check if frontend is running
if lsof -ti:5173 > /dev/null; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:5173${NC}"
else
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 MIMIQ is ready!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📊 Server Information:${NC}"
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo ""
echo -e "${BLUE}📝 Process IDs:${NC}"
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo "Backend:  tail -f backend.log"
echo "Frontend: tail -f frontend.log"
echo ""
echo -e "${BLUE}🔍 Quick Tests:${NC}"
echo "Health Check: curl http://localhost:5000/health"
echo "Chat Test:    curl -X POST http://localhost:5000/api/chat -H 'Content-Type: application/json' -d '{\"patient_id\":\"test\",\"message\":\"Hello\"}'"
echo ""
echo -e "${YELLOW}⚠️  To stop servers:${NC}"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo "OR run: lsof -ti:5000,5173 | xargs kill -9"
echo ""
echo -e "${GREEN}🌐 Open your browser: http://localhost:5173${NC}"
echo ""
echo "Press Ctrl+C to stop (will kill background processes)"

# Keep script running and handle Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped'; exit" INT

# Wait indefinitely
wait
