#!/bin/bash

# BAMF ACTE Companion - Development Startup Script
# This script sets up and starts both frontend and backend services

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BAMF ACTE Companion - Startup Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check for Node.js
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/ or use nvm"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
echo -e "${GREEN}✓ Python3 found: $(python3 --version)${NC}\n"

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✓ node_modules already exists, skipping npm install${NC}"
fi

# Setup Python virtual environment
echo -e "\n${YELLOW}Setting up Python environment...${NC}"

# Check if venv exists AND is properly set up (has bin/activate)
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "Virtual environment missing or incomplete. Creating..."
    # Remove any incomplete venv folder
    rm -rf backend/venv
    python3 -m venv backend/venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
source backend/venv/bin/activate
backend/venv/bin/pip install -r backend/requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Check for .env file
echo -e "\n${YELLOW}Checking environment configuration...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}Warning: backend/.env file not found!${NC}"
    echo "Please create backend/.env with your GEMINI_API_KEY"
    echo "Example:"
    echo "  GEMINI_API_KEY=your_api_key_here"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Environment file found${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Starting Services${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Starting backend on http://localhost:8000${NC}"
source backend/venv/bin/activate
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${YELLOW}Starting frontend on http://localhost:5173${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Services Running${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for processes
wait
