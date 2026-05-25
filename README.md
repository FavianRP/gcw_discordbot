# 🤖 CTF Discord Bot — Real-Time Webhook Notifier

Bot Discord untuk kompetisi CTF (Capture The Flag) yang terintegrasi dengan **CTFd** melalui webhook. Bot ini mengirimkan notifikasi real-time ke server Discord. Mulai dari pengumuman first blood, solve challenge, rilis challenge baru, hingga role peserta.

---

## ✨ Fitur

- 🩸 **First Blood** — Mengumumkan peserta pertama yang berhasil solve setiap challenge
- ✅ **Notifikasi Solve** — Memberitahu channel setiap kali ada challenge yang berhasil di-solve
- 🚀 **Rilis Challenge Baru** — Notifikasi otomatis saat challenge baru tersedia
- 📜 **Panel Rules** — Mengirim embed peraturan CTF lengkap dengan tombol self-role
- 🎯 **Tombol Role Peserta** — Peserta bisa ambil role sendiri hanya dengan satu klik
- 🌐 **Webhook Server (FastAPI)** — Menerima event dari CTFd secara real-time
- 💬 **CLI Sender** — Kirim pesan atau embed langsung dari terminal
- 🤖 **Perintah Bot** — `!status`, `!sendrules`

---

## 📋 Persyaratan

- Python **3.10** atau lebih baru
- Instance **CTFd** dengan dukungan webhook
- **Token Bot Discord**
- Server Discord yang kamu miliki akses admin-nya

---

## 🚀 Cara Penggunaan

### 1. Clone Repository

```bash
git clone https://github.com/FavianRP/gcw_discordbot.git
cd gcw_discordbot
```

### 2. Install Dependensi

```bash
pip install -r requirements.txt
```

> **requirements.txt** berisi:
> ```
> discord.py>=2.3.0
> fastapi>=0.110.0
> uvicorn>=0.29.0
> python-dotenv>=1.0.0
> ```

### 3. Konfigurasi Environment Variables

Salin file contoh dan isi dengan nilai yang sesuai:

```bash
cp .env.example .env
```

Edit file `.env`:

```env
# URL CTFd (contoh: https://ctf.example.com)
CTFD_API_URL=https://your-ctfd-instance.com

# ID channel Discord tempat notifikasi dikirim
DISCORD_CHANNEL_ID=123456789012345678

# Token bot Discord
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Port untuk webhook server
WEBHOOK_PORT=5000

# Secret untuk validasi webhook
WEBHOOK_SECRET=changeme
```

### 4. Jalankan Bot

```bash
python main.py
```

---

## ⚙️ Referensi Environment Variables

| Variabel | Wajib | Default | Keterangan |
|---|---|---|---|
| `CTFD_API_URL` | Tidak | _(kosong)_ | URL dasar instance CTFd kamu |
| `DISCORD_CHANNEL_ID` | **Ya** | `0` | ID channel Discord untuk notifikasi |
| `DISCORD_BOT_TOKEN` | **Ya** | _(kosong)_ | Token bot Discord |
| `WEBHOOK_PORT` | Tidak | `5000` | Port yang digunakan webhook server |
| `WEBHOOK_SECRET` | Tidak | `changeme` | Secret untuk validasi request webhook |

---

## 🔧 Setup Bot Discord

### Membuat Bot

1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. Klik **New Application** → beri nama aplikasimu
3. Masuk ke menu **Bot** → klik **Add Bot**
4. Di bagian **Token**, klik **Reset Token** → salin tokennya → tempel ke `.env` sebagai `DISCORD_BOT_TOKEN`
5. Di bagian **Privileged Gateway Intents**, aktifkan:
   - **Server Members Intent**
   - **Message Content Intent**

### Mengundang Bot ke Server

1. Masuk ke **OAuth2 → URL Generator**
2. Pilih scope: `bot` dan `applications.commands`
3. Pilih permission berikut:
   - `Send Messages`
   - `Embed Links`
   - `Manage Roles`
   - `Read Message History`
4. Salin URL yang dihasilkan → buka di browser → undang bot ke servermu

### Mendapatkan Channel ID

1. Di Discord, buka **User Settings → Advanced** → aktifkan **Developer Mode**
2. Klik kanan channel tujuan → **Copy Channel ID**
3. Tempel ke `.env` sebagai `DISCORD_CHANNEL_ID`

---

## 🔗 Setup Webhook di CTFd

Bot ini membuka endpoint webhook di:

```
POST http://<ip-server-kamu>:<WEBHOOK_PORT>/ctfd-webhook
```

### Cara Konfigurasi di CTFd

1. Di panel admin CTFd, buka **Admin → Integrations / Webhooks**
2. Tambahkan webhook baru dengan URL mengarah ke server botmu:
   ```
   http://<ip-server-kamu>:5000/ctfd-webhook
   ```
3. Pilih event yang ingin di-subscribe:
   - `challenge.solved`
   - `challenge.visible`

> **Catatan:** Jika bot berjalan secara lokal, gunakan tool tunneling seperti [ngrok](https://ngrok.com) agar bisa diakses dari internet:
> ```bash
> ngrok http 5000
> ```
> Gunakan URL ngrok tersebut sebagai webhook URL di CTFd.

### Format Payload Webhook

Bot mengharapkan struktur JSON berikut dari CTFd:

```json
{
  "event": "challenge.solved",
  "data": {
    "challenge": {
      "id": 1,
      "name": "Nama Challenge"
    },
    "user": {
      "name": "nama_pengguna"
    }
  }
}
```

---

## 💬 Perintah Bot

| Perintah | Permission | Keterangan |
|---|---|---|
| `!status` | Semua orang | Menampilkan status bot, URL CTFd, dan jumlah first blood |
| `!sendrules` | Administrator | Mengirim embed peraturan CTF lengkap dengan tombol join peserta |

---

## 🖥️ CLI Sender

Selama bot berjalan, kamu bisa mengetik perintah langsung di terminal:

| Perintah | Keterangan |
|---|---|
| `say <pesan>` | Mengirim pesan teks biasa ke channel yang dikonfigurasi |
| `embed <pesan>` | Mengirim embed pengumuman berwarna ungu |
| `rules` | Mengirim panel peraturan CTF dengan tombol role peserta |

**Contoh penggunaan:**
```
CMD > say Selamat datang di CTF GCW 4.0!
CMD > embed Kompetisi dimulai dalam 10 menit!
CMD > rules
```

---

## 📁 Struktur Project

```
ctf-discord-bot/
├── main.py           # Bot utama + webhook server
├── .env              # Environment variables
├── requirements.txt  # Dependensi Python
└── README.md         # Dokumentasi ini
```

---

## 🐳 Menjalankan dengan Docker (Opsional)

Buat file `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Lalu jalankan:

```bash
docker build -t ctf-discord-bot .
docker run --env-file .env ctf-discord-bot
```

---

## 🔒 Catatan Keamanan

- **Jangan pernah commit file `.env` ke GitHub.** Tambahkan ke `.gitignore`:
  ```
  .env
  ```
- Validasi webhook secret sudah ada di kode namun **dinonaktifkan secara default**. Aktifkan di `main.py` untuk keamanan production:
  ```python
  secret = request.headers.get("X-CTFd-Secret")
  if secret != WEBHOOK_SECRET:
      return {"status": "unauthorized"}
  ```
- Untuk deployment production, jalankan bot di balik reverse proxy (misalnya nginx) dengan HTTPS.

---

## 🤝 Kontribusi

Pull request sangat disambut! Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan apa yang ingin kamu ubah.

---

## 📄 Lisensi

MIT License — bebas digunakan dan dimodifikasi untuk event CTF sendiri.

---

> Dibuat dengan ❤️ dari CCUG — GCW 2026
