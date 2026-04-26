# Linear Webhook Receiver
# Location: [REPO_ROOT]/.sage/webhook/webhook_receiver.py
#
# Lightweight HTTP server that receives Linear webhook POST requests,
# validates HMAC-SHA256 signatures, filters for skill-update events,
# and writes trigger files to .skill-update-triggers/.
#
# Runs as a Windows Scheduled Task (starts on user login).
# Setup: run setup_webhook_receiver.ps1 once per developer machine.

import hashlib
import hmac
import http.server
import json
import logging
import os
import signal
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

PORT = int(os.environ.get("WEBHOOK_PORT", "7842"))
LOG_LEVEL = os.environ.get("WEBHOOK_LOG_LEVEL", "INFO")

# Linear webhook signing secret — set as environment variable
# Generate in Linear: Settings → API → Webhooks → [your webhook] → Signing secret
WEBHOOK_SECRET = os.environ.get("LINEAR_WEBHOOK_SECRET", "")

# Resolve repo root from this file's location
# This file lives at [REPO_ROOT]/.sage/webhook/webhook_receiver.py
SCRIPT_DIR = Path(__file__).parent.resolve()
HIVE_DIR = SCRIPT_DIR.parent
REPO_ROOT = HIVE_DIR.parent

TRIGGERS_DIR = REPO_ROOT / ".skill-update-triggers"
LOG_FILE = HIVE_DIR / "webhook" / "receiver.log"

# ─────────────────────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────────────────────

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("webhook_receiver")


# ─────────────────────────────────────────────────────────────────────────────
# Signature validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_signature(payload_bytes: bytes, signature_header: str) -> bool:
    """
    Validate Linear's HMAC-SHA256 webhook signature.
    Linear sends: Linear-Signature: <hex_digest>
    We compute:   HMAC-SHA256(secret, payload_bytes).hexdigest()
    """
    if not WEBHOOK_SECRET:
        log.warning(
            "LINEAR_WEBHOOK_SECRET not set — skipping signature validation. "
            "Set this environment variable before running in production."
        )
        return True

    if not signature_header:
        log.warning("Request missing Linear-Signature header — rejecting.")
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature_header.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Event filtering
# ─────────────────────────────────────────────────────────────────────────────

SKILL_UPDATE_LABEL = "skill-update"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"


def extract_event_type(payload: dict) -> str | None:
    """
    Determine if this webhook event is a skill-update approval or rejection.

    Linear webhook payload structure for issue status changes:
    {
      "type": "Issue",
      "action": "update",
      "data": {
        "id": "issue-uuid",
        "identifier": "LIN-4822",
        "title": "Skill update proposal — prd-completeness-check — ...",
        "state": { "name": "Approved", "type": "completed", ... },
        "labels": [{ "name": "skill-update", ... }],
        ...
      },
      "updatedFrom": {
        "stateId": "...",
        "state": { "name": "Pending Approval", ... }
      }
    }
    """
    if payload.get("type") != "Issue":
        return None

    if payload.get("action") != "update":
        return None

    data = payload.get("data", {})

    # Check for skill-update label
    labels = data.get("labels", [])
    label_names = [lbl.get("name", "").lower() for lbl in labels]
    if SKILL_UPDATE_LABEL not in label_names:
        return None

    # Check if state changed (updatedFrom must have a prior state)
    updated_from = payload.get("updatedFrom", {})
    if "stateId" not in updated_from:
        return None

    current_state = data.get("state", {}).get("name", "").lower()

    if current_state == APPROVED_STATUS:
        return "approved"
    elif REJECTED_STATUS in current_state:
        return "rejected"

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Trigger file writing
# ─────────────────────────────────────────────────────────────────────────────

def write_trigger_file(payload: dict, event_type: str) -> Path:
    """
    Write a trigger file to .skill-update-triggers/.
    The file name includes the Linear issue identifier for traceability.
    Returns the path of the written file.
    """
    TRIGGERS_DIR.mkdir(parents=True, exist_ok=True)

    data = payload.get("data", {})
    issue_identifier = data.get("identifier", "LIN-unknown")
    issue_id = data.get("id", "unknown")
    issue_title = data.get("title", "")

    # Extract skill name from the issue title
    # Expected format: "Skill update proposal — [skill-name] — ..."
    skill_name = "unknown"
    if "—" in issue_title:
        parts = issue_title.split("—")
        if len(parts) >= 2:
            skill_name = parts[1].strip()

    # Extract assignee
    assignee = data.get("assignee", {})
    approved_by = assignee.get("email", assignee.get("name", "unknown"))

    # Find the diff path from the issue description or custom fields
    # The diff path is stored as a custom field "diff_path" on the Linear issue
    diff_path = ""
    custom_fields = data.get("customFields", [])
    for field in custom_fields:
        if field.get("field", {}).get("name") == "diff_path":
            diff_path = field.get("value", "")
            break

    # If diff_path not in custom fields, construct expected path
    if not diff_path:
        diff_path = str(
            REPO_ROOT / ".skill-update-staging" / f"{issue_identifier}-diff.md"
        )

    trigger_data = {
        "linear_issue_id": issue_identifier,
        "linear_issue_uuid": issue_id,
        "skill_name": skill_name,
        "event_type": event_type,
        "approved_by": approved_by if event_type == "approved" else None,
        "rejected_by": approved_by if event_type == "rejected" else None,
        "actioned_at": datetime.now(timezone.utc).isoformat(),
        "diff_path": diff_path,
        "issue_title": issue_title,
    }

    # Include rejection comment if present
    if event_type == "rejected":
        # Linear includes comments in webhook payload for some event types
        # The rejection rationale comes from a separate comment webhook
        # We write what we have and the evaluator reads the full comment via MCP
        trigger_data["rejection_rationale_source"] = "read_from_linear_via_mcp"

    filename = f"{issue_identifier}-{event_type}.json"
    trigger_path = TRIGGERS_DIR / filename

    with open(trigger_path, "w", encoding="utf-8") as f:
        json.dump(trigger_data, f, indent=2)

    log.info(
        f"Trigger file written: {filename} "
        f"(skill: {skill_name}, event: {event_type})"
    )
    return trigger_path


# ─────────────────────────────────────────────────────────────────────────────
# HTTP request handler
# ─────────────────────────────────────────────────────────────────────────────

class WebhookHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):  # noqa: N802
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        # Always respond 200 immediately to prevent Linear retries
        # Processing happens after the response is sent
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

        # Process in background thread to avoid blocking the response
        thread = threading.Thread(
            target=self._process_payload,
            args=(body_bytes,),
            daemon=True,
        )
        thread.start()

    def _process_payload(self, body_bytes: bytes):
        # Validate signature
        signature = self.headers.get("Linear-Signature", "")
        if not validate_signature(body_bytes, signature):
            log.warning(
                "Webhook signature validation failed — payload discarded. "
                f"Path: {self.path}"
            )
            return

        # Parse JSON
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse webhook payload: {e}")
            return

        log.debug(
            f"Received webhook: type={payload.get('type')} "
            f"action={payload.get('action')}"
        )

        # Filter for skill-update events
        event_type = extract_event_type(payload)
        if not event_type:
            log.debug("Webhook event not relevant — ignored.")
            return

        issue_id = (
            payload.get("data", {}).get("identifier", "unknown")
        )
        log.info(
            f"Skill update event: {issue_id} → {event_type}"
        )

        # Write trigger file
        try:
            trigger_path = write_trigger_file(payload, event_type)
            log.info(f"Trigger file ready: {trigger_path.name}")
        except Exception as e:
            log.error(f"Failed to write trigger file: {e}", exc_info=True)

    def log_message(self, format, *args):  # noqa: A002
        # Suppress default HTTP server access log — we use our own logger
        log.debug(f"HTTP: {format % args}")


# ─────────────────────────────────────────────────────────────────────────────
# Startup checks
# ─────────────────────────────────────────────────────────────────────────────

def run_startup_checks() -> bool:
    """Run pre-start validation. Returns True if all checks pass."""
    passed = True

    if not WEBHOOK_SECRET:
        log.warning(
            "⚠  LINEAR_WEBHOOK_SECRET is not set. "
            "Signature validation is disabled. "
            "Set this environment variable before using in production."
        )

    if not TRIGGERS_DIR.parent.exists():
        log.error(
            f"❌  Repository root not found at expected path: {REPO_ROOT}\n"
            "   Ensure the receiver script is at "
            "[REPO_ROOT]/.sage/webhook/webhook_receiver.py"
        )
        passed = False

    log.info(f"📁  Repo root:     {REPO_ROOT}")
    log.info(f"📁  Triggers dir:  {TRIGGERS_DIR}")
    log.info(f"📋  Log file:      {LOG_FILE}")
    log.info(f"🔌  Port:          {PORT}")

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# Server startup and graceful shutdown
# ─────────────────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("Linear Webhook Receiver — starting up")
    log.info("=" * 60)

    if not run_startup_checks():
        log.error("Startup checks failed. Exiting.")
        sys.exit(1)

    server = http.server.HTTPServer(("localhost", PORT), WebhookHandler)

    def shutdown_handler(signum, frame):
        log.info("Shutdown signal received — stopping server.")
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    log.info(f"✅  Listening on http://localhost:{PORT}")
    log.info(
        "   Configure Linear webhook to POST to: "
        f"http://localhost:{PORT} (via ngrok or reverse proxy)"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Webhook receiver stopped.")


if __name__ == "__main__":
    main()
