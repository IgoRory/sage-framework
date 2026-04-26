# setup_webhook_receiver.ps1
# Location: [REPO_ROOT]/.sage/webhook/setup_webhook_receiver.ps1
#
# Registers the Linear webhook receiver as a Windows Scheduled Task
# that starts automatically on user login.
#
# Run once per developer machine. Requires no admin privileges —
# the task runs as the current user.
#
# Usage:
#   cd [REPO_ROOT]\.mob\webhook
#   .\setup_webhook_receiver.ps1
#
# To uninstall:
#   Unregister-ScheduledTask -TaskName "LinearWebhookReceiver" -Confirm:$false

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

$TaskName        = "LinearWebhookReceiver"
$TaskDescription = "Linear webhook receiver for Profitability AI workflow. Receives skill-update approval events from Linear and writes trigger files for Cursor hook processing."
$ScriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReceiverScript  = Join-Path $ScriptDir "webhook_receiver.py"
$LogFile         = Join-Path $ScriptDir "receiver.log"
$PidFile         = Join-Path $ScriptDir "receiver.pid"

# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "`nLinear Webhook Receiver — Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅  Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "❌  Python not found in PATH. Install Python 3.12+ and retry."
    exit 1
}

# Check receiver script exists
if (-not (Test-Path $ReceiverScript)) {
    Write-Error "❌  Receiver script not found at: $ReceiverScript"
    exit 1
}
Write-Host "✅  Receiver script: $ReceiverScript" -ForegroundColor Green

# Check environment variables
$missingVars = @()
if (-not $env:LINEAR_WEBHOOK_SECRET) { $missingVars += "LINEAR_WEBHOOK_SECRET" }
if (-not $env:LINEAR_API_KEY)         { $missingVars += "LINEAR_API_KEY" }

if ($missingVars.Count -gt 0) {
    Write-Host "`n⚠  The following environment variables are not set:" -ForegroundColor Yellow
    $missingVars | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
    Write-Host "   The receiver will start but signature validation will be disabled." -ForegroundColor Yellow
    Write-Host "   Set these variables (User scope) and re-run setup to enable validation.`n" -ForegroundColor Yellow
} else {
    Write-Host "✅  Environment variables confirmed." -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────────────────────
# Check for existing task
# ─────────────────────────────────────────────────────────────────────────────

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "`nScheduled task '$TaskName' already exists." -ForegroundColor Yellow
    $response = Read-Host "Replace it? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Setup cancelled." -ForegroundColor Gray
        exit 0
    }
    Write-Host "Removing existing task..." -ForegroundColor Gray
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# ─────────────────────────────────────────────────────────────────────────────
# Resolve python executable path
# ─────────────────────────────────────────────────────────────────────────────

$PythonExe = (Get-Command python).Source
Write-Host "   Python executable: $PythonExe" -ForegroundColor Gray

# ─────────────────────────────────────────────────────────────────────────────
# Create the scheduled task
# ─────────────────────────────────────────────────────────────────────────────

# Action: run python webhook_receiver.py
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $ReceiverScript `
    -WorkingDirectory $ScriptDir

# Trigger: on user logon
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Settings
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `  # No time limit
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# Principal: run as current user, only when logged in
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

# Register the task
$Task = Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal

Write-Host "`n✅  Scheduled task registered: '$TaskName'" -ForegroundColor Green
Write-Host "   Runs at: User login (you)" -ForegroundColor Gray
Write-Host "   Restarts: Up to 3 times on failure (1 min interval)" -ForegroundColor Gray

# ─────────────────────────────────────────────────────────────────────────────
# Start the task now (don't wait for next login)
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "`nStarting receiver now..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2

# Verify it's running
$TaskState = (Get-ScheduledTask -TaskName $TaskName).State
if ($TaskState -eq "Running") {
    Write-Host "✅  Receiver is running." -ForegroundColor Green
} else {
    Write-Host "⚠  Receiver state: $TaskState — check log for errors:" -ForegroundColor Yellow
    Write-Host "   $LogFile" -ForegroundColor Gray
}

# ─────────────────────────────────────────────────────────────────────────────
# ngrok setup reminder
# ─────────────────────────────────────────────────────────────────────────────

$Port = if ($env:WEBHOOK_PORT) { $env:WEBHOOK_PORT } else { "7842" }

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "NEXT STEP — Configure Linear webhook endpoint" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "The receiver listens on: http://localhost:$Port" -ForegroundColor White
Write-Host ""
Write-Host "Linear requires a publicly reachable HTTPS URL." -ForegroundColor White
Write-Host "Use ngrok to expose the local port:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Install ngrok: https://ngrok.com/download" -ForegroundColor Gray
Write-Host "  2. Run: ngrok http $Port" -ForegroundColor Gray
Write-Host "  3. Copy the https://xxxx.ngrok.io URL" -ForegroundColor Gray
Write-Host "  4. In Linear: Settings → API → Webhooks → New webhook" -ForegroundColor Gray
Write-Host "     URL:    https://xxxx.ngrok.io" -ForegroundColor Gray
Write-Host "     Events: Issue (update)" -ForegroundColor Gray
Write-Host "     Copy the Signing Secret → set as LINEAR_WEBHOOK_SECRET env var" -ForegroundColor Gray
Write-Host ""
Write-Host "  Note: ngrok free tier generates a new URL each time it starts." -ForegroundColor Yellow
Write-Host "  For a stable URL, use ngrok's paid static domain feature" -ForegroundColor Yellow
Write-Host "  or configure a static reverse proxy on a shared machine." -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Setup complete. Log: $LogFile" -ForegroundColor Green
Write-Host ""
