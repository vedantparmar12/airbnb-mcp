# VoicePlan Startup Script
# Starts backend, frontend, and LiveKit agent in separate windows

Write-Host "Starting VoicePlan Services..." -ForegroundColor Green

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "Error: .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

# Check if frontend .env.local exists
if (-Not (Test-Path "landing-page\.env.local")) {
    Write-Host "Error: landing-page\.env.local not found. Please copy .env.local.example and configure it." -ForegroundColor Red
    exit 1
}

# Get current directory
$projectRoot = Get-Location

Write-Host "`n1. Starting Backend API Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python backend_server.py"

Start-Sleep -Seconds 3

Write-Host "`n2. Starting Frontend Dev Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\landing-page'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "`n3. Starting LiveKit Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python livekit_mcp_agent.py start"

Write-Host "`n✅ All services started!" -ForegroundColor Green
Write-Host "`nServices running:" -ForegroundColor Yellow
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  - LiveKit Agent: Connected to LiveKit server" -ForegroundColor White
Write-Host "`nPress any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
