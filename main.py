# -*- coding: utf-8 -*-
import asyncio
import os
import threading
from datetime import datetime, timezone

import discord
import uvicorn
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from fastapi import FastAPI, Request

# ================= LOAD ENV =================
load_dotenv()

CTFD_BASE_URL = os.getenv("CTFD_API_URL", "").rstrip("/")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "changeme")

# Tracking first bloods in memory (reset setiap bot restart)
first_blood_announced = set()

webhook_started = False

# ================= DISCORD =================
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

# ================= WEBHOOK =================
app = FastAPI()


# ================= UTIL =================
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


# ================= WEBHOOK API =================
@app.post("/ctfd-webhook")
async def ctfd_webhook(request: Request):

    try:
        # optional secret validation
        # secret = request.headers.get("X-CTFd-Secret")

        # if secret != WEBHOOK_SECRET:
        #  return {"status": "unauthorized"}

        data = await request.json()

        event = data.get("event")
        payload = data.get("data", {})

        log(f"Webhook event: {event}")

        channel = client.get_channel(DISCORD_CHANNEL_ID)

        if not channel:
            return {"status": "channel_not_found"}

        # ================= SOLVE EVENT =================
        if event == "challenge.solved":
            challenge = payload.get("challenge", {})
            user = payload.get("user", {})

            cid = challenge.get("id")
            cname = challenge.get("name", "Unknown")
            username = user.get("name", "Unknown")

            # FIRST BLOOD
            if cid not in first_blood_announced:
                embed = discord.Embed(
                    title="🩸 FIRST BLOOD!",
                    description=(f"**{username}** solved **{cname}** first!"),
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc),
                )

                asyncio.run_coroutine_threadsafe(channel.send(embed=embed), client.loop)

                first_blood_announced.add(cid)

                log(f"🩸 FIRST BLOOD WEBHOOK: {cname} by {username}")

            else:
                asyncio.run_coroutine_threadsafe(
                    channel.send(f"✅ **{username}** solved **{cname}**"), client.loop
                )

        # ================= CHALLENGE RELEASE =================
        elif event == "challenge.visible":
            challenge = payload.get("challenge", {})

            embed = discord.Embed(
                title="🚀 New Challenge Released",
                description=f"**{challenge.get('name', 'Unknown')}** is now available!",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc),
            )

            asyncio.run_coroutine_threadsafe(channel.send(embed=embed), client.loop)

            log(f"🚀 New challenge released")

        return {"status": "ok"}

    except Exception as e:
        log(f"Webhook error: {e}")
        return {"status": "error"}


# ================= ROLE BUTTON =================
class ParticipantView(View):
    def __init__(self, role_name="Participant"):
        super().__init__(timeout=None)
        self.role_name = role_name

    @discord.ui.button(
        label="Join as Participant", style=discord.ButtonStyle.green, emoji="🎯"
    )
    async def join_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        role = discord.utils.get(guild.roles, name=self.role_name)

        if not role:
            await interaction.response.send_message(
                f"❌ Role `{self.role_name}` tidak ditemukan!", ephemeral=True
            )
            return

        if role in member.roles:
            await interaction.response.send_message(
                "⚠️ Kamu sudah punya role ini!", ephemeral=True
            )
            return

        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ Role `{self.role_name}` berhasil diberikan!", ephemeral=True
        )


# ================= CLI SENDER =================
async def cli_sender():
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if not channel:
        log("Channel not found for CLI sender")
        return

    while True:
        try:
            cmd = await asyncio.to_thread(input, "CMD > ")

            if cmd.startswith("say "):
                msg = cmd[4:]
                await channel.send(msg)
                log("Sent plain message")

            elif cmd.startswith("embed "):
                msg = cmd[6:]
                embed = discord.Embed(
                    title="📢 Announcement",
                    description=msg,
                    color=discord.Color.purple(),
                )
                await channel.send(embed=embed)
                log("Sent embed message")

            elif cmd == "rules":
                embed = discord.Embed(
                    title="📜 CTF Rules",
                    description=(
                        "1. Dilarang sharing flag\n"
                        "2. No brute force berlebihan\n"
                        "3. Hormati peserta lain\n"
                        "4. Semua aktivitas dimonitor\n\n"
                        "Klik tombol di bawah untuk join sebagai participant!"
                    ),
                    color=discord.Color.blue(),
                )
                view = ParticipantView()
                await channel.send(embed=embed, view=view)
                log("Sent rules panel")

        except Exception as e:
            log(f"CLI error: {e}")


# ================= COMMANDS =================
@client.command(name="status")
async def status_command(ctx):
    status_ctfd = "🟢 Webhook Mode"

    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="🌐 CTFd URL", value=CTFD_BASE_URL or "Not set", inline=False)
    embed.add_field(name="CTFd Status", value=status_ctfd, inline=True)
    embed.add_field(name="🩸 Announced", value=len(first_blood_announced), inline=True)
    embed.set_footer(text="CTF GCW BOT - RealTime")

    await ctx.send(embed=embed)


@client.command(name="sendrules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    embed = discord.Embed(
        title="📜 CTF Rules",
        description=(
            "1. Dilarang sharing flag atau bekerja sama dengan tim lain\n"
            "2. Dilarang melakukan brute force berlebihan / spam submission\n"
            "3. Tidak diperbolehkan menggunakan automated tools (nmap, sqlmap, dirbuster, dll)\n"
            "4. Dilarang melakukan serangan ke infrastruktur (DDoS, overload, dll)\n"
            "5. Dilarang merusak challenge atau mengganggu peserta lain\n"
            "6. Tidak boleh flag hoarding (menahan flag)\n"
            "7. Gunakan AI/tools hanya sebagai referensi, bukan solusi instan\n"
            "8. Wajib menjaga sportivitas & etika selama kompetisi\n"
            "9. Semua aktivitas akan dimonitor oleh panitia\n"
            "10. Pelanggaran akan berujung diskualifikasi\n\n"
            "Klik tombol di bawah untuk join sebagai participant!"
        ),
        color=discord.Color.blue(),
    )
    view = ParticipantView()
    await ctx.send(embed=embed, view=view)


# ================= EVENTS =================
@client.event
async def on_ready():
    print("=" * 60)
    print(f"✓ Logged in as {client.user}")
    print("=" * 60)

    global webhook_started

    if not webhook_started:
        threading.Thread(target=run_webhook_server, daemon=True).start()

        webhook_started = True
    activity = discord.Activity(
        type=discord.ActivityType.watching, name="Watching GCW 4.0"
    )
    await client.change_presence(status=discord.Status.online, activity=activity)

    # 🔥 CLI tetap jalan
    client.loop.create_task(cli_sender())


# ================= WEBHOOK SERVER =================
def run_webhook_server():
    log(f"Webhook server started on port {WEBHOOK_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT, log_level="warning")


# ================= RUN =================
if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
