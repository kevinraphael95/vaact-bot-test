import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, description=f"Je suis un bot Yu-Gi-Oh! Tapez {COMMAND_PREFIX}help pour voir les commandes.")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} ({bot.user.id})")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        embed = discord.Embed(
            title="👋 Salut !",
            description=f"Je suis un bot Yu-Gi-Oh! Tapez `{COMMAND_PREFIX}help` pour voir les commandes disponibles.",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

async def load_extensions():
    await bot.load_extension("commands.general.ping")

if __name__ == "__main__":
    keep_alive()

    import asyncio
    async def main():
        await load_extensions()
        await bot.start(TOKEN)

    asyncio.run(main())
