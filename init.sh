#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Initializing AI Chat Application...${NC}\n"

# Add base directory tracking
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS type
detect_os() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    elif [[ -f "/etc/redhat-release" ]]; then
        echo "rhel"
    elif [[ -f "/etc/debian_version" ]]; then
        echo "debian"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)

# Handle package installation based on OS
if [[ "$OS_TYPE" == "windows" ]]; then
    echo -e "${RED}Windows detected. Please ensure you have the following installed:${NC}"
    echo -e "1. Python 3.8+ (from python.org)"
    echo -e "2. Node.js v20+ LTS (from nodejs.org)"
    echo -e "3. Git Bash or similar Unix-like environment"
    read -p "Press Enter to continue if you have these prerequisites..."
elif [[ "$OS_TYPE" == "rhel" ]]; then
    echo -e "${BLUE}RHEL-based system detected. Checking/installing dependencies...${NC}"
    if ! command_exists python3; then
        sudo dnf install -y python3
    fi
    if ! command_exists node; then
        echo -e "${BLUE}Installing Node.js 20 LTS...${NC}"
        # Remove any existing nodejs repositories
        sudo rm -f /etc/yum.repos.d/nodesource*
        # Install Node.js 20 LTS
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        # Install Node.js and npm
        sudo dnf install -y nodejs
        # Verify installation
        if ! command_exists node; then
            echo -e "${RED}Failed to install Node.js. Please install manually.${NC}"
            exit 1
        fi
    fi
elif [[ "$OS_TYPE" == "debian" ]]; then
    echo -e "${BLUE}Debian-based system detected. Checking/installing dependencies...${NC}"
    if ! command_exists python3; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    fi
    if ! command_exists node; then
        echo -e "${BLUE}Installing Node.js 20 LTS...${NC}"
        # Remove any existing nodejs repositories
        sudo rm -f /etc/apt/sources.list.d/nodesource.list
        # Install Node.js 20 LTS
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        # Verify installation
        if ! command_exists node; then
            echo -e "${RED}Failed to install Node.js. Please install manually.${NC}"
            exit 1
        fi
    fi
fi

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Add version checks
if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo -e "${GREEN}✓ Python 3.8+ detected${NC}"
else
    echo -e "${RED}❌ Python 3.8+ is required${NC}"
    exit 1
fi

# Add Ollama setup and model pulling
echo -e "\n${BLUE}Checking Ollama installation...${NC}"
if ! command_exists ollama; then
    echo -e "${BLUE}Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install Ollama${NC}"
        exit 1
    fi
fi

# Start Ollama service
echo -e "\n${BLUE}Starting Ollama service...${NC}"
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama service to start
echo -e "${BLUE}Waiting for Ollama service to initialize...${NC}"
sleep 5  # Give it some time to start up

echo -e "\n${BLUE}Pulling required Ollama models...${NC}"
models=("llama3.2" "llama3.2-vision" "codestral" "qwen2.5-coder")

for model in "${models[@]}"; do
    echo -e "${BLUE}Pulling $model...${NC}"
    ollama pull "$model"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to pull $model${NC}"
        kill $OLLAMA_PID
        exit 1
    fi
done

# Create and activate Python virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# Verify virtual environment activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Install backend dependencies
echo -e "\n${BLUE}Installing backend dependencies...${NC}"
cd "${BASE_DIR}/backend" || exit 1

# Update pip first
python3 -m pip install --upgrade pip

# Install requirements including ollama and requests
if ! pip install -r requirements.txt ollama requests; then
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f openai.env ]; then
    echo -e "${RED}⚠️  No openai.env file found in backend directory${NC}"
    echo -e "Creating openai.env file. Please edit it with your OpenAI API key"
    echo "OPENAI_API_KEY=your_api_key_here" > openai.env
fi

# Start backend server in background
echo -e "\n${BLUE}Starting backend server...${NC}"
uvicorn app:app --host 0.0.0.0 --port 5001 --reload &
BACKEND_PID=$!

# Install frontend dependencies
echo -e "\n${BLUE}Installing frontend dependencies...${NC}"
cd "${BASE_DIR}/frontend" || exit 1
if ! npm install; then
    echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
    kill $BACKEND_PID
    exit 1
fi

# Start frontend development server
echo -e "\n${BLUE}Starting frontend development server...${NC}"
npm run serve &
FRONTEND_PID=$!

# Trap SIGINT to properly close both servers
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' SIGINT

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}🌐 Frontend running at: http://localhost:8080${NC}"
echo -e "${GREEN}🚀 Backend API running at: http://localhost:5001${NC}"
echo -e "${GREEN}📚 API documentation available at: http://localhost:5001/docs${NC}"
echo -e "\n${BLUE}Press Ctrl+C to stop both servers${NC}"

# Wait for both processes
wait 