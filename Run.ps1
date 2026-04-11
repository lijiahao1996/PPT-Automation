# PPT Report Generator - Web Interface Launcher v5.0
# Simplified version - Web interface only

Write-Host "========================================" -ForegroundColor Green
Write-Host "  PPT Report Generator v5.0" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Streamlit
try {
    $streamlitVersion = streamlit --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Streamlit: $streamlitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Streamlit not found! Install with: pip install streamlit" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting web interface..." -ForegroundColor Cyan
Write-Host "Access: http://localhost:8501/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start Streamlit
python -m streamlit run scripts\config_tool\app.py --server.port 8501 --server.address localhost
