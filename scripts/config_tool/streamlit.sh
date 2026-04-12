#!/bin/bash

# PPT Report Generator v6.0
# Streamlit Web Interface Launcher

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "  PPT Report Generator v6.0"
echo "  Streamlit Web Interface"
echo "========================================"
echo ""
echo "Starting web interface..."
echo ""
echo "Access: http://localhost:8501/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python not found!"
        echo ""
        echo "Please install Python 3.8+:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "  macOS: brew install python3"
        echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
        echo ""
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Check if Streamlit is installed
if ! $PYTHON_CMD -m streamlit --version &> /dev/null; then
    echo "[ERROR] Streamlit not found!"
    echo ""
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r ../../requirements.txt
fi

# Start Streamlit
$PYTHON_CMD -m streamlit run app.py --server.port 8501 --server.address localhost
