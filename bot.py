import discord
from discord.ext import commands
from pathlib import Path
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and message.author != bot.user:
        embed = discord.Embed(
            title="👋 Salut !",
            description="Je suis un bot Yu-Gi-Oh!
Tapez `!help` pour voir les commandes disponibles.",
            color=discord.Color.purple()
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

async def load_commands_from_folder(folder_path, module_base):
    for file in folder_path.glob("*.py"):
        if file.name != "__init__.py":
            await bot.load_extension(f"{module_base}.{file.stem}")

async def start():
    await load_commands_from_folder(Path("commands/general"), "commands.general")
    await load_commands_from_folder(Path("commands/ygo"), "commands.ygo")
    await bot.start(TOKEN)

if __name__ == "__main__":
    keep_alive()
    import asyncio
    asyncio.run(start())
