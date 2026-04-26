# Linear Webhook Receiver

## What this is

A lightweight Python HTTP server that receives Linear webhook events
and writes trigger files for the Cursor hook layer to process.

Used specifically for skill-update approval events:
- When a `skill-update` Linear issue moves to `Approved` → writes
  an approved trigger file → skill-effectiveness-evaluator applies
  the SKILL.md diff
- When a `skill-update` Linear issue moves to `Rejected` → writes
  a rejected trigger file → change is suppressed for 2 evaluation cycles

## Files in this directory

```
.sage/webhook/
├── webhook_receiver.py          ← The receiver service
├── setup_webhook_receiver.ps1   ← One-time Windows setup script
├── receiver.log                 ← Runtime log (auto-created)
└── README.md                    ← This file
```

---

## Setup (one-time, per developer machine)

### Step 1 — Set the webhook signing secret

After configuring the Linear webhook (Step 4 below), set the
signing secret as a User environment variable:

```powershell
[System.Environment]::SetEnvironmentVariable(
  "LINEAR_WEBHOOK_SECRET", "your-secret-here", "User")
```

### Step 2 — Run the setup script

```powershell
cd [REPO_ROOT]\.mob\webhook
.\setup_webhook_receiver.ps1
```

The script:
- Registers `LinearWebhookReceiver` as a Windows Scheduled Task
- Starts at user login automatically
- Restarts up to 3 times on failure
- Starts the receiver immediately (no need to log out and back in)

### Step 3 — Install and configure ngrok

Linear requires a publicly reachable HTTPS URL for webhook delivery.
Since the receiver runs on a local machine, ngrok exposes it.

1. Download ngrok: https://ngrok.com/download
2. Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
3. Start tunnel: `ngrok http 7842`
4. Copy the `https://xxxx.ngrok.io` URL

**ngrok free tier caveat:** The URL changes every time ngrok starts.
You must update the Linear webhook URL after each restart.

**Recommended for stability:** Use ngrok's paid static domain feature
(`ngrok http --domain=your-domain.ngrok.dev 7842`). This gives a
fixed URL that never changes. Configure this on **one machine only**
(the Lead Dev's machine or a dedicated server) — the webhook does not need
to run on every developer machine, only the machine that processes
skill updates.

### Step 4 — Configure the Linear webhook

In Linear: Settings → API → Webhooks → New webhook

| Field | Value |
|---|---|
| URL | `https://[your-ngrok-url]` |
| Events | Issue → Update |
| Label filter | `skill-update` (optional but reduces noise) |

After saving, copy the **Signing Secret** shown by Linear.
Set it as `LINEAR_WEBHOOK_SECRET` (Step 1 above).

### Step 5 — Verify

Test by approving a skill-update issue in Linear (or creating a
test issue with the `skill-update` label and moving it to Approved).

Check the log:
```powershell
Get-Content [REPO_ROOT]\.mob\webhook\receiver.log -Tail 20
```

You should see:
```
[INFO] Skill update event: LIN-XXXX → approved
[INFO] Trigger file ready: LIN-XXXX-approved.json
```

---

## Runtime management

### Check if running
```powershell
Get-ScheduledTask -TaskName "LinearWebhookReceiver" | Select-Object State
```

### Start manually
```powershell
Start-ScheduledTask -TaskName "LinearWebhookReceiver"
```

### Stop
```powershell
Stop-ScheduledTask -TaskName "LinearWebhookReceiver"
```

### View live log
```powershell
Get-Content [REPO_ROOT]\.mob\webhook\receiver.log -Wait -Tail 50
```

### Uninstall
```powershell
Stop-ScheduledTask -TaskName "LinearWebhookReceiver"
Unregister-ScheduledTask -TaskName "LinearWebhookReceiver" -Confirm:$false
```

---

## Configuration

The receiver reads configuration from environment variables:

| Variable | Default | Description |
|---|---|---|
| `LINEAR_WEBHOOK_SECRET` | (none) | HMAC signing secret from Linear. Required for signature validation. If not set, all requests are accepted (insecure). |
| `WEBHOOK_PORT` | `7842` | Port to listen on. Must match your ngrok tunnel port. |
| `WEBHOOK_LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |

All variables are set at User scope so they persist across restarts
without admin privileges.

---

## Which machine should run this?

The receiver does not need to run on every developer machine.
It only needs to run on **one machine** — the one that processes
skill update approvals. the Lead Dev's machine is the natural choice since
the Lead Dev approves phase-splitter updates and is the technical lead.

the Product Manager's machine should also run it if it needs to process
prd-completeness-check and prd-interviewer skill updates
(since the Product Manager is the approver for those).

If only one machine runs the receiver, configure ngrok's static
domain on that machine and use that URL for the Linear webhook.

---

## How the trigger chain works

```
Linear issue → "Approved" status
        ↓
Linear fires POST to https://[ngrok-url]
        ↓
webhook_receiver.py receives POST
        ↓
Validates HMAC-SHA256 signature
        ↓
Filters: type=Issue, action=update,
         label=skill-update, state=Approved
        ↓
Writes: .skill-update-triggers/LIN-[id]-approved.json
        ↓
skill_update_trigger_watcher.py detects new file
(Cursor afterFileEdit hook fires)
        ↓
Launches skill-effectiveness-evaluator apply step
        ↓
SKILL.md updated + committed + Linear status = Applied
```

---

## Troubleshooting

**Receiver not starting:**
Check the log for Python errors. Confirm Python 3.12 is in PATH.
Confirm the script path in the scheduled task matches the actual
file location.

**Webhook events not received:**
Confirm ngrok is running and the URL in Linear matches.
Check Linear webhook delivery logs (Settings → API → Webhooks →
your webhook → Recent deliveries).

**Signature validation failures:**
Confirm `LINEAR_WEBHOOK_SECRET` matches the secret shown in
Linear's webhook settings. Note: the secret is shown only once
when the webhook is created — if you didn't capture it, regenerate
it in Linear and update the environment variable.

**Trigger file written but Cursor not detecting it:**
Confirm Cursor is open and the `skill_update_trigger_watcher.py`
hook is registered in `hooks.json`. The hook fires on `afterFileEdit`
events — Cursor must be running for it to fire.

**Duplicate trigger files:**
If Linear retries a webhook (it retries on non-2xx responses), the
receiver may write duplicate trigger files. The receiver always
responds 200, but if it crashes mid-response Linear may retry.
The apply step handles duplicates gracefully — it checks whether
the diff has already been applied before re-applying.
