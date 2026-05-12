# setup_webhook_receiver.ps1
# Location: [REPO_ROOT]/.sage/webhook/setup_webhook_receiver.ps1
#
# Registers the Linear webhook receiver as a Windows Scheduled Task
# that starts automatically on user login.
#
# Run once per developer machine. Requires no admin privileges.
#
# Usage:
#   cd [REPO_ROOT]\.sage\webhook
#   .\setup_webhook_receiver.ps1
#
# To uninstall:
#   Unregister-ScheduledTask -TaskName "LinearWebhookReceiver" -Confirm:$false

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskName        = "LinearWebhookReceiver"
$TaskDescription = "Linear webhook receiver for Profitability AI workflow. Receives skill-update approval events from Linear and writes trigger files for Cursor hook processing."
$ScriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReceiverScript  = Join-Path $ScriptDir "webhook_receiver.py"
$LogFile         = Join-Path $ScriptDir "receiver.log"

Write-Host ""
Write-Host "Linear Webhook Receiver - Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found in PATH. Install Python 3.12+ and retry."
    exit 1
}

# Check receiver script exists
if (-not (Test-Path $ReceiverScript)) {
    Write-Error "Receiver script not found at: $ReceiverScript"
    exit 1
}
Write-Host "OK Receiver script: $ReceiverScript" -ForegroundColor Green

# Check environment variables
$missingVars = @()
if (-not [System.Environment]::GetEnvironmentVariable("LINEAR_WEBHOOK_SECRET", "User")) { $missingVars += "LINEAR_WEBHOOK_SECRET" }
if (-not [System.Environment]::GetEnvironmentVariable("LINEAR_API_KEY", "User"))         { $missingVars += "LINEAR_API_KEY" }

if ($missingVars.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: The following environment variables are not set:" -ForegroundColor Yellow
    $missingVars | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    Write-Host "  The receiver will start but signature validation will be disabled." -ForegroundColor Yellow
    Write-Host "  Set these variables and re-run setup to enable validation." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "OK Environment variables confirmed." -ForegroundColor Green
}

# Remove existing task if present
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host ""
    Write-Host "Scheduled task '$TaskName' already exists." -ForegroundColor Yellow
    $response = Read-Host "Replace it? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Setup cancelled." -ForegroundColor Gray
        exit 0
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Resolve python executable
$PythonExe = (Get-Command python).Source
Write-Host "  Python executable: $PythonExe" -ForegroundColor Gray

# Create scheduled task
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $ReceiverScript `
    -WorkingDirectory $ScriptDir

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal | Out-Null

Write-Host ""
Write-Host "OK Scheduled task registered: '$TaskName'" -ForegroundColor Green
Write-Host "   Runs at: User login" -ForegroundColor Gray
Write-Host "   Restarts: Up to 3 times on failure (1 min interval)" -ForegroundColor Gray

# Start immediately
Write-Host ""
Write-Host "Starting receiver now..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2

$TaskState = (Get-ScheduledTask -TaskName $TaskName).State
if ($TaskState -eq "Running") {
    Write-Host "OK Receiver is running." -ForegroundColor Green
} else {
    Write-Host "WARNING Receiver state: $TaskState - check log for errors:" -ForegroundColor Yellow
    Write-Host "  $LogFile" -ForegroundColor Gray
}

# ngrok setup instructions
$Port = if ([System.Environment]::GetEnvironmentVariable("WEBHOOK_PORT", "User")) {
    [System.Environment]::GetEnvironmentVariable("WEBHOOK_PORT", "User")
} else { "7842" }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "NEXT STEP: Configure Linear webhook endpoint" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The receiver listens on: http://localhost:$Port" -ForegroundColor White
Write-Host ""
Write-Host "Linear requires a publicly reachable HTTPS URL." -ForegroundColor White
Write-Host "Expose the local port using ngrok:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Run: ngrok http $Port" -ForegroundColor Gray
Write-Host "  2. Copy the https://xxxx.ngrok.io URL" -ForegroundColor Gray
Write-Host "  3. Linear: Settings -> API -> Webhooks -> New webhook" -ForegroundColor Gray
Write-Host "     URL: https://xxxx.ngrok.io" -ForegroundColor Gray
Write-Host "     Events: Issue (update)" -ForegroundColor Gray
Write-Host "  4. Copy the Signing Secret shown by Linear" -ForegroundColor Gray
Write-Host "  5. Run:" -ForegroundColor Gray
Write-Host "     [System.Environment]::SetEnvironmentVariable('LINEAR_WEBHOOK_SECRET', '<secret>', 'User')" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Setup complete. Log: $LogFile" -ForegroundColor Green
Write-Host ""
