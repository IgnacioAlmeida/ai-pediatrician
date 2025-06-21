#!/bin/bash

echo "Starting Pediatrician AI Assistant..."

# Start backend in background
echo "Starting backend API..."
cd /home/ignacio/projects
python pediatrician.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting React frontend..."
cd /home/ignacio/projects/pediatrician-frontend
npm start &
FRONTEND_PID=$!

echo "Application started!"
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait 