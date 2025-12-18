

````md
# Proxmox Telegram Bot

A Telegram bot for managing Proxmox VE environments via chat, focused on **safe operations** and **real-world administration workflows**.

The bot allows controlling QEMU virtual machines and LXC containers while enforcing confirmations, state tracking, and safety checks.

---

## ✨ Features

- 📋 List virtual machines (QEMU) and LXC containers
- ▶️ Start virtual machines
- ⏹ Stop virtual machines
- ℹ️ Get VM status
- 🟢 Show all running resources (VMs + LXC)
- 🔐 Confirmation flow for destructive actions
- ⚠️ Safety checks before host shutdown
- ⏻ Safe Proxmox host shutdown (admin only)
- 📝 Centralized logging with rotation

---

## 🧠 Design Principles

- Clear separation between **API layer** and **Telegram handlers**
- Explicit state machine for user interaction flow
- No silent destructive operations
- Human-readable output for operational clarity
- Built with homelab and small production environments in mind

---

## 📦 Requirements

- Python **3.10+**
- Proxmox VE with API access enabled
- Telegram Bot Token
- Network access to the Proxmox API endpoint

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/lior3333/telbot-proxmox.git
cd telbot-proxmox
````

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration

Create environment configuration:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token
PROXMOX_HOST=https://proxmox.example:8006
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=bot
PROXMOX_TOKEN_SECRET=xxxxxxxx
PROXMOX_NODE=pve
```


---

## ▶️ Running the Bot

```bash
python3 main.py
```

---

## 🛡 Safety Notes

* All destructive actions require explicit confirmation
* Host shutdown is blocked if running VMs or containers are detected
* Designed to prevent accidental service disruption
* Recommended to restrict admin actions to trusted users only

---

## 📂 Project Structure

```
.
├── main.py                # Telegram bot entrypoint
├── proxmox_client.py      # Proxmox API abstraction
├── handler_shutdown.py    # Host-level operations
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚧 Roadmap

* Inline keyboard confirmations
* VM and LXC restart actions
* Role-based access control
* Resource metrics (CPU / RAM / uptime)
* Audit log export

---

## 📄 License

MIT License

---

## 👤 Author

Built by a SysAdmin with a homelab-first mindset, focusing on reliability, safety, and operational clarity.

