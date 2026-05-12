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
# Also supports reading from a secret file at .sage/webhook/.webhook_secret for environments
# where env var inheritance is unreliable (e.g., Windows Scheduled Tasks).
def _load_webhook_secret() -> str:
    val = os.environ.get("LINEAR_WEBHOOK_SECRET", "").strip()
    if val:
        return val
    secret_file = SCRIPT_DIR / ".webhook_secret"
    if secret_file.exists():
        return secret_file.read_text(encoding="ascii").strip()
    return ""

WEBHOOK_SECRET = _load_webhook_secret()

# Resolve repo root from this file's location
# This file lives at [REPO_ROOT]/.sage/webhook/webhook_receiver.py
SCRIPT_DIR = Path(__file__).parent.resolve()
SAGE_DIR = SCRIPT_DIR.parent
REPO_ROOT = SAGE_DIR.parent

TRIGGERS_DIR = REPO_ROOT / ".skill-update-triggers"
LOG_FILE = SAGE_DIR / "webhook" / "receiver.log"

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
    Linear sends: Linear-Signature: <hex-digest>
    We compute: HMAC-SHA256(secret, payload_bytes).hexdigest()
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

    sig_clean = signature_header.strip()
    if not hmac.compare_digest(expected, sig_clean):
        log.warning(
            f"Signature mismatch — expected={expected[:16]}... got={sig_clean[:16]}... "
            f"secret_len={len(WEBHOOK_SECRET)} body_len={len(payload_bytes)}"
        )
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Event filtering
# ─────────────────────────────────────────────────────────────────────────────

SKILL_UPDATE_LABEL = "skill-update"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"


def extract_event_type(payload: dict) -> str | None:
    """
    Determine if this webhook event is a skill-update approval or rejection.
    Returns "approved", "rejected", or None if the event is not relevant.
    """
    if payload.get("type") != "Issue":
        return None

    if payload.get("action") != "update":
        return None

    data = payload.get("data", {})

    labels = data.get("labels", [])
    label_names = [lbl.get("name", "").lower() for lbl in labels]
    if SKILL_UPDATE_LABEL not in label_names:
        return None

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
    Returns the path of the written file.
    """
    TRIGGERS_DIR.mkdir(parents=True, exist_ok=True)

    data = payload.get("data", {})
    issue_identifier = data.get("identifier", "LIN-unknown")
    issue_id = data.get("id", "unknown")
    issue_title = data.get("title", "")

    # Extract skill name from issue title
    # Expected format: "Skill update proposal — [skill-name] — ..."
    skill_name = "unknown"
    if "\u2014" in issue_title:
        parts = issue_title.split("\u2014")
        if len(parts) >= 2:
            skill_name = parts[1].strip()

    assignee = data.get("assignee", {})
    approved_by = assignee.get("email", assignee.get("name", "unknown"))

    # Find diff path from issue description custom fields
    diff_path = ""
    custom_fields = data.get("customFields", [])
    for field in custom_fields:
        if field.get("field", {}).get("name") == "diff_path":
            diff_path = field.get("value", "")
            break

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

    if event_type == "rejected":
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
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        # Capture header before responding — self.headers may not survive thread boundary
        signature = self.headers.get("Linear-Signature", "")

        # Always respond 200 immediately to prevent Linear retries
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

        # Process in background thread
        thread = threading.Thread(
            target=self._process_payload,
            args=(body_bytes, signature),
            daemon=True,
        )
        thread.start()

    def _process_payload(self, body_bytes: bytes, signature: str):
        # signature captured in do_POST before thread spawn
        try:
            self._process_payload_inner(body_bytes, signature)
        except Exception:
            log.exception("Unhandled error in _process_payload")

    def _process_payload_inner(self, body_bytes: bytes, signature: str):
        log.info(f"Processing payload: body_len={len(body_bytes)} sig_len={len(signature)}")
        if not validate_signature(body_bytes, signature):
            log.warning("Webhook signature validation failed — payload discarded.")
            return

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse webhook payload: {e}")
            return

        log.debug(
            f"Received webhook: type={payload.get('type')} "
            f"action={payload.get('action')}"
        )

        event_type = extract_event_type(payload)
        if not event_type:
            log.debug("Webhook event not relevant — ignored.")
            return

        issue_id = payload.get("data", {}).get("identifier", "unknown")
        log.info(f"Skill update event: {issue_id} -> {event_type}")

        try:
            trigger_path = write_trigger_file(payload, event_type)
            log.info(f"Trigger file ready: {trigger_path.name}")
        except Exception as e:
            log.error(f"Failed to write trigger file: {e}", exc_info=True)

    def log_message(self, format, *args):  # noqa: A002
        log.debug(f"HTTP: {format % args}")


# ─────────────────────────────────────────────────────────────────────────────
# Startup checks
# ─────────────────────────────────────────────────────────────────────────────

def run_startup_checks() -> bool:
    passed = True

    if not WEBHOOK_SECRET:
        log.warning(
            "LINEAR_WEBHOOK_SECRET is not set. "
            "Signature validation is disabled. "
            "Set this environment variable before using in production."
        )

    if not TRIGGERS_DIR.parent.exists():
        log.error(
            f"Repository root not found at expected path: {REPO_ROOT}\n"
            "  Ensure this file is at [REPO_ROOT]/.sage/webhook/webhook_receiver.py"
        )
        passed = False

    log.info(f"Repo root:    {REPO_ROOT}")
    log.info(f"Triggers dir: {TRIGGERS_DIR}")
    log.info(f"Log file:     {LOG_FILE}")
    log.info(f"Port:         {PORT}")

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

    log.info(f"Listening on http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Webhook receiver stopped.")


if __name__ == "__main__":
    main()
