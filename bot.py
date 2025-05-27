# ──────────────────────────────────────────────────────────────
# 🟢 Serveur Keep-Alive (Render)
# ──────────────────────────────────────────────────────────────
from keep_alive import keep_alive

import discord
from discord.ext import commands
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# 🔐 Chargement des variables d'environnement
# ──────────────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ──────────────────────────────────────────────────────────────
# ⚙️ Configuration du bot
# ──────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

# ──────────────────────────────────────────────────────────────
# 📦 Chargement des extensions (commandes)
# ──────────────────────────────────────────────────────────────
async def load_commands_from_folder(folder: Path, base_module: str):
    for file in folder.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_path = f"{base_module}.{file.stem}"
        try:
            await bot.load_extension(module_path)
            print(f"✅ Commande chargée : {module_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {module_path} : {e}")

# ──────────────────────────────────────────────────────────────
# 🚀 Lancement du bot
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive()

    async def start():
        await load_commands_from_folder(Path("commands/ygo"), "commands.ygo")
        await load_commands_from_folder(Path("commands/general"), "commands.general")
        await bot.start(TOKEN)

    asyncio.run(start())
