#!/bin/bash

# PPT Report Generator v6.0
# Cross-platform Startup Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "  PPT Report Generator v6.0"
echo "  Cross-platform Startup"
echo "========================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    echo "Detected OS: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    echo "Detected OS: macOS"
else
    OS="Unknown"
    echo "Detected OS: Unknown (may not be fully supported)"
fi

echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python not found!"
        echo ""
        echo "Please install Python 3.8+:"
        if [[ "$OS" == "Linux" ]]; then
            echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
            echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
        elif [[ "$OS" == "macOS" ]]; then
            echo "  macOS: brew install python3"
        else
            echo "  Download from: https://www.python.org/downloads/"
        fi
        echo ""
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "[OK] Python: $($PYTHON_CMD --version)"

# Check pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "[ERROR] pip not found!"
    echo ""
    echo "Please install pip:"
    if [[ "$OS" == "Linux" ]]; then
        echo "  Ubuntu/Debian: sudo apt-get install python3-pip"
        echo "  CentOS/RHEL: sudo yum install python3-pip"
    elif [[ "$OS" == "macOS" ]]; then
        echo "  macOS: brew install python3-pip"
    fi
    echo ""
    exit 1
fi

echo "[OK] pip: $($PYTHON_CMD -m pip --version)"
echo ""

# Check and install dependencies
if [ ! -f "requirements.txt" ]; then
    echo "[ERROR] requirements.txt not found!"
    echo ""
    exit 1
fi

echo "Checking dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt -q

echo ""
echo "[OK] All dependencies installed"
echo ""

# Start Streamlit
echo "Starting web interface..."
echo ""
echo "Access: http://localhost:8501/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_CMD -m streamlit run scripts/config_tool/app.py --server.port 8501 --server.address localhost
