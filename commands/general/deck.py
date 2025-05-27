import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
from pathlib import Path

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user in message.mentions:
        embed = discord.Embed(
            title="👋 Salut !",
            description="Je suis un bot Yu-Gi-Oh!\nTapez `!help` pour voir les commandes disponibles.",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

def load_commands_from_folder(folder: Path, base_module: str):
    for file in folder.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_path = f"{base_module}.{file.stem}"
        try:
            bot.load_extension(module_path)
            print(f"✅ Commande chargée : {module_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {module_path} : {e}")

load_commands_from_folder(Path("commands/general"), "commands.general")
load_commands_from_folder(Path("commands/ygo"), "commands.ygo")

if __name__ == "__main__":
    keep_alive()
    asyncio.run(bot.start(TOKEN))
