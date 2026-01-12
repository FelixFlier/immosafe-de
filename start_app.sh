#!/bin/bash
echo "🚀 Starting ImmoSafe on Port 8001..."

# Kill anything currently running on 8001 or 5173 to clear conflicts
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend in Background
cd backend
source venv/bin/activate 2>/dev/null || (python3 -m venv venv && source venv/bin/activate)
pip install -r requirements.txt > /dev/null 2>&1
# Explicitly use port 8001
uvicorn main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Start Frontend
cd ../frontend
npm install > /dev/null 2>&1
echo "✅ Frontend starting..."
npm run dev &
FRONTEND_PID=$!

# Cleanup function to kill both when user presses Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

echo ""
echo "📍 Backend API:  http://localhost:8001"
echo "📍 Frontend:     http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

wait
