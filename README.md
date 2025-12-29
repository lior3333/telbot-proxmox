<p align="center">
  <img src="https://img.shields.io/github/license/lior3333/telbot-proxmox?style=for-the-badge&color=blue" alt="License" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Proxmox-VE-E57000?style=for-the-badge&logo=proxmox&logoColor=white" alt="Proxmox" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram" />
</p>

# 🤖 Proxmox Telegram Bot

> **Manage your Proxmox VE infrastructure safely and securely directly from Telegram.**

This bot provides a robust interface for administrators to monitor and control their Proxmox environment on the go. Designed with **safety first** principles, it ensures critical operations require explicit confirmation and prevents accidental downtime.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#-architecture)
- [📦 Requirements](#-requirements)
- [🚀 Getting Started](#-getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Bot](#running-the-bot)
- [🎮 Usage](#-usage)
- [🛡️ Safety Mechanisms](#-safety-mechanisms)
- [🗺️ Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **VM & LXC Management** | List, Start, Stop, and Get Status for all your QEMU VMs and LXC containers. |
| **Real-time Status** | 🟢 Identify all running resources instantly with a single command. |
| **Safety First** | 🔐 Strict confirmation flows for all destructive actions (Stop, Shutdown). |
| **Smart Shutdown** | 🛡️ Prevents host shutdown if any VMs or containers are still running. |
| **Access Control** | 👤 Whitelist-based access control to ensure only authorized admins can issue commands. |
| **Audit Logging** | 📝 Comprehensive logging of all actions and errors for troubleshooting. |

---

## 🏗️ Architecture

The solution is built on a clean, modular architecture:

1.  **Telegram Layer (`main.py`)**: Handles user interaction, input validation, and state management using `pyTelegramBotAPI`.
2.  **API Abstraction (`proxmox_client.py`)**: Wraps the `proxmoxer` library to provide a simplified, high-level API for bot operations.
3.  **Core Logic**: Implements business rules (e.g., "don't shutdown if VMs are running") and error handling.

---

## 📦 Requirements

- **Python**: 3.10 or higher
- **Proxmox VE**: Verified on 7.x and 8.x
- **Network**: The bot must have network access to your Proxmox server's API port (default `8006`).

---

## 🚀 Getting Started

Follow these steps to get your bot up and running in minutes.

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/lior3333/telbot-proxmox.git
    cd telbot-proxmox
    ```

2.  **Set up Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Configure the `.env` file with your credentials:

| Variable | Description | Required | Example |
| :--- | :--- | :---: | :--- |
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token (from @BotFather) | ✅ | `123456:ABC...` |
| `PROXMOX_HOST` | URL of your Proxmox API | ✅ | `https://192.168.1.100:8006` |
| `PROXMOX_USER` | Proxmox user (include realm) | ✅ | `root@pam` |
| `PROXMOX_TOKEN_NAME` | Name of the API Token | ✅ | `telbot` |
| `PROXMOX_TOKEN_VALUE` | The secret API Token | ✅ | `xxxxxxxx-xxxx...` |
| `PROXMOX_NODE` | Name of the target node | ✅ | `pve1` |
| `ALLOWED_USERS` | Comma-separated Telegram User IDs | ✅ | `12345678, 87654321` |

### Running the Bot

```bash
python3 main.py
```

*Tip: For production, consider running this as a systemd service or in a Docker container.*

---

## 🎮 Usage

Once the bot is running, send `/start` to see the main menu.

**Common Commands:**
- **Show VMs**: Displays a list of all VMs with their status (Running/Stopped).
- **Show Running**: Lists ONLY the resources that are currently active.
- **Start/Stop VM**: Initiates a state change (requires confirmation).
- **Shutdown Host**: Initiates a host shutdown (blocked if resources are active).

---

## 🛡️ Safety Mechanisms

We take safety seriously. This tool is designed to prevent "fat-finger" mistakes:

*   **Confirmation Dialogs**: No destructive action happens without a "Yes/No" confirmation click.
*   **State Awareness**: The bot checks the actual status of a VM before attempting to start or stop it.
*   **Host Protection**: The `Shutdown Host` command performs a pre-flight check and aborts if any VM or LXC container is currently running.

---

## 🗺️ Roadmap

- [ ] 🔄 Restart VM/LXC command
- [ ] � Resource Usage Stats (CPU/RAM graphs)
- [ ] 🐳 Docker container support
- [ ] 🌐 Webhook support for alerts
- [ ] 🌍 Multi-language support (currently English)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/lior3333">Lior Rez</a>
</p>
