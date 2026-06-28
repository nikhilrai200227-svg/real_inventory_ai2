#!/bin/bash

# InventoryPilot AI - Setup & Run Script
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      InventoryPilot AI - Setup & Run Script               ║"
echo "║   AI-Powered Inventory Intelligence Platform             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${BLUE}⚠ Please edit .env and add your GOOGLE_API_KEY${NC}"
fi

# Create necessary directories
mkdir -p data models reports

# Generate sample data
echo -e "${YELLOW}Generating sample inventory data...${NC}"
python3 generate_sample_data.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Sample data generated${NC}"
else
    echo -e "${RED}✗ Failed to generate sample data${NC}"
fi

# Display startup options
echo -e "${BLUE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup Complete! Choose how to run the application:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

echo -e "${YELLOW}Option 1: Run Dashboard only${NC}"
echo "  Command: streamlit run dashboard.py"
echo "  Access: http://localhost:8501"

echo -e "${YELLOW}Option 2: Run Backend API only${NC}"
echo "  Command: python -m uvicorn backend:app --reload"
echo "  Access: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"

echo -e "${YELLOW}Option 3: Run Both (Dashboard + Backend)${NC}"
echo "  Terminal 1: python -m uvicorn backend:app --reload"
echo "  Terminal 2: streamlit run dashboard.py"

echo -e "${YELLOW}Option 4: Run with Docker${NC}"
echo "  Command: docker-compose up --build"
echo "  Backend: http://localhost:8000"
echo "  Dashboard: http://localhost:8501"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Ask user what to run
read -p "Which option would you like to run? (1/2/3/4/q to quit): " choice

case $choice in
    1)
        echo -e "${GREEN}Starting Dashboard...${NC}"
        echo -e "${BLUE}Dashboard: http://localhost:8501${NC}"
        streamlit run dashboard.py
        ;;
    2)
        echo -e "${GREEN}Starting Backend API...${NC}"
        echo -e "${BLUE}API: http://localhost:8000${NC}"
        echo -e "${BLUE}Docs: http://localhost:8000/docs${NC}"
        python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo -e "${GREEN}Starting both services...${NC}"
        echo -e "${YELLOW}This requires two terminal windows.${NC}"
        echo -e "${BLUE}Dashboard: http://localhost:8501${NC}"
        echo -e "${BLUE}API: http://localhost:8000${NC}"
        echo ""
        echo -e "${YELLOW}Starting Backend API first...${NC}"
        python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        sleep 2
        
        echo -e "${YELLOW}Starting Dashboard...${NC}"
        streamlit run dashboard.py &
        DASH_PID=$!
        
        echo -e "${GREEN}Both services running!${NC}"
        echo "Press Ctrl+C to stop all services..."
        
        wait
        ;;
    4)
        echo -e "${GREEN}Starting with Docker Compose...${NC}"
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}✗ Docker Compose is not installed${NC}"
            echo "Install Docker Desktop or Docker Compose to proceed"
            exit 1
        fi
        docker-compose up --build
        ;;
    q)
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac
