# 🤖 GCW Discord CTF Bot Realtime - Firstblook Notifier

Bot Discord sederhana untuk integrasi dengan CTFd.

---

## Features

- 🩸 First Blood notification
- ✅ Solve notification
- 🎯 Self-role participant button
- 📜 Rules panel
- 💬 CLI sender
- 🤖 Discord commands

---

## Installation

```bash
git clone https://github.com/FavianRP/gcw_discordbot.git
cd gcw_discordbot

pip install -r requirements.txt
```

---

## Configuration

Buat file `.env`:

```env
CTFD_API_URL=https://ctfd.example.com
CTFD_API_KEY=your_ctfd_api_key

DISCORD_CHANNEL_ID=1234567890
DISCORD_BOT_TOKEN=your_discord_bot_token
```

---

## Run

```bash
python main.py
```

---

## Commands

| Command | Description |
|---|---|
| `!ping` | Check bot latency |
| `!status` | Show bot status |
| `!sendrules` | Send rules panel |

---

## CLI Sender

Kirim pesan langsung dari terminal:

```bash
say hello
embed Welcome to GCW CTF!
```

---

## Requirements

```txt
discord.py
aiohttp
python-dotenv
```

---

## Preview

- First blood announcement
- Auto solve notification
- Participant role button
- Rules embed panel

---

## Kontribusi

Pull request sangat diperbolehkan! Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan apa yang ingin kamu ubah.

---

## Lisensi

MIT License - bebas digunakan dan dimodifikasi untuk event CTF sendiri.

---

> Made with ❤️ by dre4mer | CCUG — GCW 2026
