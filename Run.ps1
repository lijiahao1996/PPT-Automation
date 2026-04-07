# Auto Run Script - Enterprise Version
# Support both EXE bundled and direct PowerShell execution

Write-Host "========================================" -ForegroundColor Green
Write-Host "  FanRuan Auto Run - Enterprise Edition" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

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

# Check for Excel files
Write-Host "Checking data files..." -ForegroundColor Cyan
$excelFiles = Get-ChildItem -Path $outputDir -Filter "*.xlsx" -ErrorAction SilentlyContinue

if ($excelFiles.Count -gt 0) {
    Write-Host "[OK] Found $($excelFiles.Count) Excel files, skip scraping" -ForegroundColor Green
    $skipScrape = $true
} else {
    Write-Host "[INFO] No data files, starting scrape..." -ForegroundColor Yellow
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
