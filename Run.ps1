# Auto Run Script - Enterprise Version
# Support both EXE bundled and direct PowerShell execution
# Auto-generate config.ini from template if not exists

Write-Host "========================================" -ForegroundColor Green
Write-Host "  FanRuan Auto Run - Enterprise Edition" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# ========== Check and Generate config.ini ==========
$scriptDir = if ($env:EXE_BASE_DIR) { $env:EXE_WORK_DIR } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$configFile = Join-Path $scriptDir "config.ini"
$configTemplate = Join-Path $scriptDir "config.ini.example"

if (-not (Test-Path $configFile)) {
    Write-Host "[INFO] config.ini not found, creating from template..." -ForegroundColor Yellow
    
    if (Test-Path $configTemplate) {
        Copy-Item $configTemplate $configFile
        Write-Host "[OK] config.ini created from template" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "  ACTION REQUIRED" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please edit config.ini and fill in:" -ForegroundColor White
        Write-Host "  1. [fanruan] password - Your FanRuan account password" -ForegroundColor Cyan
        Write-Host "  2. [api_keys] qwen_api_key - Your Qwen API key" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Then run again." -ForegroundColor White
        Write-Host ""
        Write-Host "Template location: $configTemplate" -ForegroundColor Gray
        Write-Host "Config location: $configFile" -ForegroundColor Gray
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    } else {
        Write-Host "[ERROR] config.ini.example template not found!" -ForegroundColor Red
        Write-Host "Please create config.ini manually" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Determine directories (support EXE bundled)
if ($env:EXE_BASE_DIR) {
    $scriptDir = $env:EXE_BASE_DIR
    $workDir = $env:EXE_WORK_DIR
    Write-Host "[INFO] Running from EXE" -ForegroundColor Cyan
    Write-Host "  Base: $scriptDir" -ForegroundColor Gray
    Write-Host "  Work: $workDir" -ForegroundColor Gray
} else {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $workDir = $scriptDir
}

$outputDir = Join-Path $workDir "output"
$scriptsDir = Join-Path $scriptDir "scripts"
$logsDir = Join-Path $workDir "logs"
$artifactsDir = Join-Path $workDir "artifacts"
$fanruanDir = Join-Path $scriptsDir "fanruan"

# Ensure directories exist
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Force -Path $logsDir | Out-Null }
if (-not (Test-Path $artifactsDir)) { New-Item -ItemType Directory -Force -Path $artifactsDir | Out-Null }

Set-Location $workDir

# Check for raw data file (帆软销售明细.xlsx)
Write-Host "Checking data files..." -ForegroundColor Cyan
$rawDataFile = Join-Path $outputDir "帆软销售明细.xlsx"
$skipScrape = $false

# 逻辑：如果文件存在且有效，直接跳过爬取
if (Test-Path $rawDataFile) {
    $fileSize = (Get-Item $rawDataFile).Length
    if ($fileSize -gt 10000) {  # 至少 10KB 才认为是有效文件
        Write-Host "[OK] Raw data file exists ($([math]::Round($fileSize/1KB, 1)) KB), skip scraping" -ForegroundColor Green
        Write-Host "      File: $rawDataFile" -ForegroundColor Gray
        $skipScrape = $true
    } else {
        Write-Host "[WARN] Raw data file is empty/small ($fileSize bytes), will re-scrape..." -ForegroundColor Yellow
        $skipScrape = $false
    }
} else {
    Write-Host "[INFO] Raw data file not found, starting scrape..." -ForegroundColor Yellow
    $skipScrape = $false
}

# Session Management
$sessionFile = Join-Path $artifactsDir "fanruan_session.json"
$sessionMaxAge = 7

function Test-SessionValid {
    param([string]$SessionFile, [int]$MaxAgeDays)
    if (-not (Test-Path $SessionFile)) { return $false }
    try {
        $session = Get-Content $SessionFile -Raw | ConvertFrom-Json
        $age = (Get-Date) - (Get-Item $SessionFile).LastWriteTime
        if ($age.TotalDays -gt $MaxAgeDays) {
            Write-Host "[INFO] Session expired (age: $($age.Days) days)" -ForegroundColor Yellow
            return $false
        }
        Write-Host "[OK] Session valid (age: $($age.Days) days)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[WARN] Session file invalid" -ForegroundColor Yellow
        return $false
    }
}

# Login & Scrape
if (-not $skipScrape) {
    $needLogin = -not (Test-SessionValid -SessionFile $sessionFile -MaxAgeDays $sessionMaxAge)
    if ($needLogin) {
        Write-Host "`nStep 1: Login to FanRuan..." -ForegroundColor Cyan
        $loginScript = Join-Path $fanruanDir "fanruan_login.py"
        if (Test-Path $loginScript) {
            python $loginScript
            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n[ERROR] Login failed!" -ForegroundColor Red
                Read-Host "Press Enter to exit"
                exit 1
            }
        } else {
            Write-Host "[ERROR] Login script not found: $loginScript" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    Write-Host "`nStep 2: Scrape data from FanRuan..." -ForegroundColor Cyan
    $scrapeScript = Join-Path $fanruanDir "fanruan_scrape.py"
    if (Test-Path $scrapeScript) {
        python $scrapeScript
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`n[ERROR] Scrape failed!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "[ERROR] Scrape script not found: $scrapeScript" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Analyze Data
Write-Host "`nStep 3: Analyze Data (with validation)..." -ForegroundColor Cyan
$analyzeScript = Join-Path $fanruanDir "fanruan_analyze.py"
if (Test-Path $analyzeScript) {
    python $analyzeScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[ERROR] Analysis failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[ERROR] Analysis script not found: $analyzeScript" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Generate Report
Write-Host "`nStep 4: Generate Report (Template + Charts + AI)..." -ForegroundColor Cyan
$reportScript = Join-Path $scriptsDir "generate_report.py"
if (Test-Path $reportScript) {
    python $reportScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[ERROR] Report generation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[ERROR] Report script not found: $reportScript" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
