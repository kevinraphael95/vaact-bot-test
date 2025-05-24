from keep_alive import keep_alive


# bot.py

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("Yu-Gi-Oh! Duelist Mode"))

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong !")

@bot.command(name="carte")
async def carte(ctx, *, nom: str):
    """Renvoie une carte Yu-Gi-Oh en fonction de son nom (mock pour l'instant)."""
    await ctx.send(f"🔍 Recherche de la carte **{nom}**... (fonction à venir)")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
