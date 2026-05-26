# -*- coding: utf-8 -*-
import asyncio
import os
from datetime import datetime, timezone

import aiohttp
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

CTFD_BASE_URL = os.getenv("CTFD_API_URL", "").rstrip("/")
CTFD_API_KEY = os.getenv("CTFD_API_KEY")

DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ================= TRACKER =================
first_blood_announced = set()
announced_solves = set()

# ================= DISCORD =================
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)


# ================= UTIL =================
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


# ================= ROLE BUTTON =================
class ParticipantView(View):
    def __init__(self, role_name="Participant"):
        super().__init__(timeout=None)
        self.role_name = role_name

    @discord.ui.button(
        label="Join as Participant",
        style=discord.ButtonStyle.green,
        emoji="🎯",
    )
    async def join_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        role = discord.utils.get(guild.roles, name=self.role_name)

        if not role:
            await interaction.response.send_message(
                f"❌ Role `{self.role_name}` tidak ditemukan!",
                ephemeral=True,
            )
            return

        if role in member.roles:
            await interaction.response.send_message(
                "⚠️ Kamu sudah punya role ini!",
                ephemeral=True,
            )
            return

        await member.add_roles(role)

        await interaction.response.send_message(
            f"✅ Role `{self.role_name}` berhasil diberikan!",
            ephemeral=True,
        )


async def poll_ctfd_solves():
    await client.wait_until_ready()

    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if not channel:
        log("Discord channel not found!")
        return

    headers = {
        "Authorization": f"Token {CTFD_API_KEY}",
        "Content-Type": "application/json",
    }

    log("CTFd polling started")

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                url = f"{CTFD_BASE_URL}/api/v1/submissions"

                async with session.get(url, headers=headers, timeout=10) as r:
                    if r.status != 200:
                        log(f"CTFd API Error: {r.status}")

                        await asyncio.sleep(10)
                        continue

                    data = await r.json()

                submissions = data.get("data", [])

                for sub in submissions:
                    if sub.get("type") != "correct":
                        continue

                    sid = sub.get("id")

                    if sid in announced_solves:
                        continue

                    announced_solves.add(sid)

                    challenge = sub.get("challenge", {})
                    user = sub.get("user", {})

                    cname = challenge.get("name", "Unknown")
                    username = user.get("name", "Unknown")

                    cid = challenge.get("id") or cname

                    log(f"NEW SOLVE -> {username} solved {cname}")

                    # FIRST BLOOD
                    if cid not in first_blood_announced:
                        embed = discord.Embed(
                            title="🩸 FIRST BLOOD!",
                            description=(f"**{username}** solved **{cname}** first!"),
                            color=discord.Color.red(),
                            timestamp=datetime.now(timezone.utc),
                        )

                        await channel.send(embed=embed)

                        first_blood_announced.add(cid)

                        log(f"FIRST BLOOD -> {cname} by {username}")

                    else:
                        await channel.send(f"✅ **{username}** solved **{cname}**")

                await asyncio.sleep(5)

            except Exception as e:
                log(f"Polling Error: {e}")

                await asyncio.sleep(10)


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


# ================= COMMANDS =================
@client.command(name="status")
async def status_command(ctx):

    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )

    embed.add_field(
        name="🌐 CTFd URL",
        value=CTFD_BASE_URL,
        inline=False,
    )

    embed.add_field(
        name="🩸 First Blood",
        value=len(first_blood_announced),
        inline=True,
    )

    embed.add_field(
        name="✅ Total Solve Seen",
        value=len(announced_solves),
        inline=True,
    )

    embed.set_footer(text="GCW CTF BOT")

    await ctx.send(embed=embed)

@client.command(name="ping")
async def ping_command(ctx):

    latency = round(client.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: `{latency}ms`",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )

    embed.set_footer(text="GCW CTF BOT")

    await ctx.reply(embed=embed)

@client.command(name="sendrules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):

    embed = discord.Embed(
        title="📜 CTF GCW Rules",
        description=(
            "• Dilarang sharing flag atau bekerja sama dengan tim lain\n"
            "• Dilarang melakukan brute force berlebihan / spam submission\n"
            "• Tidak diperbolehkan menggunakan automated tools "
            "(nmap, sqlmap, dirbuster, dll)\n"
            "• Dilarang melakukan serangan ke infrastruktur "
            "(DDoS, overload, dll)\n"
            "• Dilarang merusak challenge atau mengganggu peserta lain\n"
            "• Tidak boleh flag hoarding (menahan flag)\n"
            "• Gunakan AI/tools hanya sebagai referensi, bukan solusi instan\n"
            "• Wajib menjaga sportivitas & etika selama kompetisi\n"
            "• Semua aktivitas akan dimonitor oleh panitia\n"
            "• Pelanggaran akan berujung diskualifikasi\n\n"
            "Klik tombol di bawah untuk join sebagai participant!"
        ),
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc),
    )

    embed.set_footer(text="GCW CTF BOT")

    view = ParticipantView()

    await ctx.send(embed=embed, view=view)


# ================= EVENTS =================
@client.event
async def on_ready():

    print("=" * 60)
    print(f"✓ Logged in as {client.user}")
    print("=" * 60)

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="Watching GCW 4.0",
    )

    await client.change_presence(
        status=discord.Status.online,
        activity=activity,
    )

    # START TASKS
    client.loop.create_task(cli_sender())
    client.loop.create_task(poll_ctfd_solves())

    log("All background tasks started")


# ================= RUN =================
if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
