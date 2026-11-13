#!/bin/bash
# ============================================================
#  Evil Vps V1 — Installer
#  Sets up LXD/LXC, Python deps, systemd service for bot.py
# ============================================================

set -e

# ---------- Colors ----------
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'
MAG='\033[0;35m'; CYN='\033[0;36m'; WHT='\033[1;37m'; NC='\033[0m'

# RGB palette
C1='\033[38;5;196m' # red
C2='\033[38;5;208m' # orange
C3='\033[38;5;226m' # yellow
C4='\033[38;5;46m'  # green
C5='\033[38;5;39m'  # blue
C6='\033[38;5;135m' # purple
DIM='\033[38;5;238m'
PURPLE='\033[38;5;135m'

ascii_banner() {
    echo -e "${C1} ██████${C2}╗ ${C3}██████${C4}╗ ${C5}██╗${C6}███╗   ███${C1}╗███████${C2}╗ ██████${C3}╗ ███${C4}╗   ██${C5}╗${NC}"
    echo -e "${C1}██╔════${C2}╝ ${C3}██╔══██${C4}╗██${C5}║${C6}████╗ ████${C1}║██╔════${C2}╝██╔═══${C3}██╗████${C4}╗  ██${C5}║${NC}"
    echo -e "${C2}██${C3}║${C4}  ███${C5}╗██████${C6}╔╝██${C1}║██╔████╔${C2}██║███████${C3}╗██║   ${C4}██║██╔██${C5}╗ ██║${NC}"
    echo -e "${C3}██${C4}║${C5}   ██${C6}║██╔══██${C1}╗██${C2}║██║╚██╔╝${C3}██║╚════${C4}██║██║   ${C5}██║██║╚██${C6}╗██║${NC}"
    echo -e "${C4}╚${C5}██████${C6}╔╝██${C1}║  ██${C2}║██║${C3}██║ ╚═╝ ${C4}██║███████${C5}║╚██████${C6}╔╝██║ ╚████║${NC}"
    echo -e "${C5} ${C6}╚═════${C1}╝ ╚═${C2}╝  ╚═${C3}╝╚═╝╚═╝     ${C4}╚═╝╚══════${C5}╝ ╚═════${C6}╝ ╚═╝  ╚═══╝${NC}"
    echo ""
    echo -e "  ${PURPLE}[Version]${DIM} >> ${WHT}1.0.0${DIM}  •  ${PURPLE}crimson${DIM}  •  ${CYN}discord.gg/crimson${NC}"
    echo ""
}

banner() {
    clear
    ascii_banner
    echo -e "${DIM}  ┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "  ${DIM}│  ${CYN}Fully Automated LXC/LXD VPS Discord Bot Installer${DIM}           │${NC}"
    echo -e "  ${DIM}│  ${CYN}Ubuntu & Debian supported  |  Fast setup${DIM}                    │${NC}"
    echo -e "  ${DIM}│  ${PURPLE}Made by EvilSaad${DIM}  |  ${C5}github.com/evilsaad0-hash/vps-deploy-bot-v1${DIM}  │${NC}"
    echo -e "${DIM}  └─────────────────────────────────────────────────────────────┘${NC}\n"
}

step()  { echo -e "  ${C4}›${NC} ${WHT}$1${NC}"; }
warn()  { echo -e "  ${C3}⚠${NC}  $1"; }
err()   { echo -e "  ${C1}✗${NC}  $1"; }

need_root() {
    if [ "$EUID" -ne 0 ]; then
        err "Please run this script as root (sudo ./install.sh)"
        exit 1
    fi
}

# ---------- OS selection ----------
choose_os() {
    echo -e "${WHT}Select your OS:${NC}"
    echo -e "  ${YEL}1)${NC} Ubuntu"
    echo -e "  ${YEL}2)${NC} Debian"
    read -rp "$(echo -e "${CYN}Enter choice [1-2]: ${NC}")" OS_CHOICE
}

install_lxd_ubuntu() {
    step "Updating system (Ubuntu)..."
    apt update && apt upgrade -y

    step "Installing LXC utilities..."
    apt install lxc lxc-utils -y

    step "Installing snapd..."
    apt install snapd -y
    systemctl enable --now snapd.socket

    step "Installing LXD via snap..."
    snap install lxd

    step "Adding $SUDO_USER to lxd group..."
    usermod -aG lxd "${SUDO_USER:-$USER}" || true

    step "Initializing LXD (auto/minimal config)..."
    lxd init --auto

    step "Installing bridge/uidmap utilities..."
    apt update
    apt install lxc lxc-utils bridge-utils uidmap -y
}

install_lxd_debian() {
    step "Updating system (Debian)..."
    apt update && apt upgrade -y

    step "Installing snapd..."
    apt install snapd -y
    systemctl enable --now snapd.socket

    step "Linking snap directory..."
    ln -sf /var/lib/snapd/snap /snap

    step "Installing LXD via snap..."
    snap install lxd

    step "Adding $SUDO_USER to lxd group..."
    usermod -aG lxd "${SUDO_USER:-$USER}" || true

    step "Initializing LXD (auto/minimal config)..."
    lxd init --auto
}

install_python_stack() {
    step "Installing Python 3 / pip..."
    apt install python3-pip -y

    step "Allowing pip to break system packages (PEP 668 override)..."
    mkdir -p ~/.config/pip
    echo -e "[global]\nbreak-system-packages = true" > ~/.config/pip/pip.conf

    step "Installing Python dependencies (discord.py, requests)..."
    pip3 install -U discord.py requests
}

deploy_bot() {
    step "Deploying bot.py to /root ..."
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/bot.py" ]; then
        cp "$SCRIPT_DIR/bot.py" /root/bot.py
    else
        err "bot.py not found next to install.sh. Place it in the same folder and re-run."
        exit 1
    fi
}

configure_env() {
    echo -e "\n${WHT}────────── Bot Configuration ──────────${NC}"
    read -rp "$(echo -e "${CYN}Enter your Discord Bot Token: ${NC}")" DISCORD_TOKEN
    read -rp "$(echo -e "${CYN}Enter your Main Admin Discord ID: ${NC}")" MAIN_ADMIN_ID

    if [ -z "$DISCORD_TOKEN" ] || [ -z "$MAIN_ADMIN_ID" ]; then
        err "Token and Admin ID cannot be empty."
        exit 1
    fi
}

create_service() {
    step "Creating systemd service..."
    cat > /etc/systemd/system/bot.service <<EOF
[Unit]
Description=IPMI SUPERMICRO BOT
After=network.target

[Service]
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=DISCORD_TOKEN=${DISCORD_TOKEN}
Environment=MAIN_ADMIN_ID=${MAIN_ADMIN_ID}
Environment=BOT_NAME=Svm-v9

[Install]
WantedBy=multi-user.target
EOF

    step "Reloading systemd daemon..."
    systemctl daemon-reload

    step "Starting bot service..."
    systemctl restart bot

    step "Enabling bot service on boot..."
    systemctl enable bot
}

final_message() {
    echo ""
    echo -e "${DIM}  ┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "  ${DIM}│  ${C4}✓  Installation complete!${DIM}                                     │${NC}"
    echo -e "  ${DIM}├─────────────────────────────────────────────────────────────┤${NC}"
    echo -e "  ${DIM}│  ${PURPLE}Service name${DIM} :${NC} bot.service${DIM}                                   │${NC}"
    echo -e "  ${DIM}│  ${PURPLE}Status${DIM}       :${NC} systemctl status bot${DIM}                          │${NC}"
    echo -e "  ${DIM}│  ${PURPLE}Logs${DIM}         :${NC} journalctl -u bot -f${DIM}                          │${NC}"
    echo -e "  ${DIM}│  ${PURPLE}Restart${DIM}      :${NC} systemctl restart bot${DIM}                         │${NC}"
    echo -e "${DIM}  └─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "  ${PURPLE}[crimson]${DIM} install → ${NC}"
    echo ""
}

main() {
    banner
    need_root
    choose_os

    case "$OS_CHOICE" in
        1) install_lxd_ubuntu ;;
        2) install_lxd_debian ;;
        *) err "Invalid choice. Exiting."; exit 1 ;;
    esac

    install_python_stack
    deploy_bot
    configure_env
    create_service
    final_message
}

main "$@"
