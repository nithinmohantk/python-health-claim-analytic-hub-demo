#!/bin/bash
# Quick start script for HealthClaim Analytics Hub

set -e

echo "🏥 HealthClaim Analytics Hub - Quick Start"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${BLUE}[Step 1] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Step 2: Create virtual environment
echo -e "${BLUE}[Step 2] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Step 3: Activate virtual environment
echo -e "${BLUE}[Step 3] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 4: Install dependencies
echo -e "${BLUE}[Step 4] Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 5: Configure secrets
echo -e "${BLUE}[Step 5] Checking Streamlit secrets...${NC}"
if [ ! -f ".streamlit/secrets.toml" ]; then
    if [ -f ".streamlit/secrets.toml.example" ]; then
        cp .streamlit/secrets.toml.example .streamlit/secrets.toml
        echo -e "${YELLOW}⚠ Created .streamlit/secrets.toml from template${NC}"
        echo -e "${YELLOW}⚠ Please edit .streamlit/secrets.toml and add your OpenAI API key${NC}"
        echo ""
        echo "To get your OpenAI API key:"
        echo "  1. Visit https://platform.openai.com/api-keys"
        echo "  2. Create a new API key"
        echo "  3. Copy the key to .streamlit/secrets.toml"
        echo ""
        read -p "Press Enter after updating secrets, or Ctrl+C to exit: "
    fi
fi

# Step 6: Test OpenAI connection
echo -e "${BLUE}[Step 6] Testing OpenAI API connection...${NC}"
python3 << EOF 2>/dev/null
import os
import sys
sys.path.insert(0, 'utils')

# Check if API key exists
api_key = os.getenv('OPENAI_API_KEY') or open('.streamlit/secrets.toml', 'r').read().split('=')[1].strip().strip('"\'')
if api_key and api_key.startswith('sk-'):
    print("✓ OpenAI API key configured")
else:
    print("⚠ OpenAI API key not properly configured")
EOF

# Step 7: Start application
echo -e "${BLUE}[Step 7] Starting HealthClaim Analytics Hub...${NC}"
echo -e "${GREEN}✓ Application starting at http://localhost:8501${NC}"
echo -e "${YELLOW}⚠ Press Ctrl+C to stop${NC}"
echo ""

streamlit run app.py --logger.level=warning
