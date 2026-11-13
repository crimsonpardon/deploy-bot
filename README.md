<div align="center">

```
██████╗ ██████╗ ██╗███╗   ███╗███████╗ ██████╗ ███╗   ██╗
██╔════╝██╔══██╗██║████╗ ████║██╔════╝██╔═══██╗████╗  ██║
██║     ██████╔╝██║██╔████╔██║███████╗██║   ██║██╔██╗ ██║
██║     ██╔══██╗██║██║╚██╔╝██║╚════██║██║   ██║██║╚██╗██║
╚██████╗██║  ██║██║██║ ╚═╝ ██║███████║╚██████╔╝██║ ╚████║
 ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
```

### 🤖 **deploy-bot** — Fully Automated LXC/LXD VPS Discord Bot Installer

![Version](https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/platform-Ubuntu%20%7C%20Debian-orange?style=for-the-badge&logo=linux)
![Discord](https://img.shields.io/badge/discord.gg-crimson-5865F2?style=for-the-badge&logo=discord)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

> *Made with ❤️ by [crimsonpardon](https://github.com/crimsonpardon)*

</div>

---

## 🌈 What is this?

**deploy-bot** is a one-command installer that sets up a fully automated **LXC/LXD VPS Discord bot** environment on Ubuntu or Debian. No manual setup. Just run, answer two questions, and your bot is live.

---

## ⚡ Quick Install

```bash
# Clone the repo
git clone https://github.com/crimsonpardon/deploy-bot.git

# Enter the directory
cd deploy-bot

# Give execute permission
chmod +x install.sh

# Run as root
sudo ./install.sh
```

---

## 🚀 One-Liner

```bash
git clone https://github.com/crimsonpardon/deploy-bot.git && cd deploy-bot && chmod +x install.sh && sudo ./install.sh
```

---

## 📋 Requirements

| Requirement | Details |
|-------------|---------|
| 🖥️ OS | Ubuntu 20.04+ or Debian 11+ |
| 👤 Permissions | Root / sudo |
| 🐍 Python | 3.x (auto-installed) |
| 🌐 Network | Active internet connection |
| 🤖 Discord | Bot token + Admin user ID |

---

## 🛠️ What the Installer Does

```
[+] Updates system packages
[+] Installs LXC / LXD via snap
[+] Configures LXD (auto/minimal)
[+] Installs Python 3 + pip
[+] Installs discord.py + requests
[+] Deploys bot.py to /root
[+] Configures environment (token, admin ID)
[+] Creates & starts systemd service
[+] Enables bot on system boot
```

---

## 🔧 Bot Management

```bash
# Check bot status
systemctl status bot

# View live logs
journalctl -u bot -f

# Restart the bot
systemctl restart bot

# Stop the bot
systemctl stop bot

# Enable on boot
systemctl enable bot
```

---

## 📁 File Structure

```
deploy-bot/
├── install.sh   ← Run this first
└── bot.py       ← Your Discord bot (place here before install)
```

> ⚠️ **Important:** Make sure `bot.py` is in the **same folder** as `install.sh` before running the installer.

---

## 🌐 Support

<div align="center">

[![Discord](https://img.shields.io/badge/Join%20Discord-discord.gg%2Fcrimson-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/crimson)
[![GitHub](https://img.shields.io/badge/GitHub-crimsonpardon-181717?style=for-the-badge&logo=github)](https://github.com/crimsonpardon)

</div>

---

<div align="center">

```
[crimson] deploy-bot → online ✓
```

*© 2024 crimsonpardon — All rights reserved*

</div>
