import discord
from discord.ext import commands
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

# Fonction pour charger les extensions
async def load_commands():
    for folder in ["commands.ygo", "commands.general"]:
        path = Path("commands") / folder.split(".")[-1]
        for file in path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            try:
                await bot.load_extension(f"{folder}.{file.stem}")
                print(f"✅ Commande chargée : {folder}.{file.stem}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {folder}.{file.stem} : {e}")

if __name__ == "__main__":
    keep_alive()

    async def start():
        await load_commands()
        await bot.start(TOKEN)

    asyncio.run(start())
