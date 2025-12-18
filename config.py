import os

# =========================
# TELEGRAM
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

# =========================
# SECURITY
# =========================

ALLOWED_USERS = {
    int(uid) for uid in os.getenv("ALLOWED_USERS", "").split(",") if uid
}

# =========================
# FSM STATES
# =========================

MAIN_MENU = "MAIN_MENU"
WAIT_VM_ID = "WAIT_VM_ID"
CONFIRM_ACTION = "CONFIRM_ACTION"

# =========================
# PROXMOX
# =========================

PROXMOX_NODE = os.getenv("PROXMOX_NODE", "pve")

import os

PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_TOKEN_NAME = os.getenv("PROXMOX_TOKEN_NAME")
PROXMOX_TOKEN_VALUE = os.getenv("PROXMOX_TOKEN_VALUE")

VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"
