import os
import json
import discord
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand
from dotenv import load_dotenv
from pathlib import Path
from keep_alive import keep_alive  # Optionnel si tu l'utilises

# Charger les variables d’environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")
intents = discord.Intents.default()
intents.message_content = True

# 💬 Commande help personnalisée
class YuGiOhHelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        return f"Utilise `{self.context.prefix}help <commande>` pour plus de détails."

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=YuGiOhHelpCommand(
        command_attrs={
            "name": "help",
            "help": "Affiche les commandes disponibles, classées par catégories.",
        }
    )
)

# 🔔 Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("Yu-Gi-Oh! Duelist Mode"))

# 📌 Répond à la mention du bot
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions and len(message.mentions) == 1 and message.content.strip().startswith(f"<@"):
        embed = discord.Embed(
            title="Yu-Gi-Oh Bot",
            description="👁️ Tu as activé ma carte piège !\n"
                        f"Mon préfixe est : `{PREFIX}`\n\n"
                        f"📜 Tape `{PREFIX}help` pour voir toutes les commandes disponibles.",
            color=discord.Color.dark_red()
        )
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Ton deck est prêt.")
        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)

# 📦 Charger dynamiquement tous les Cogs dans commands/
def load_cogs():
    for folder in ["commands/general", "commands/ygo"]:
        for file in Path(folder).glob("*.py"):
            module = f"{folder.replace('/', '.')}.{file.stem}"
            bot.load_extension(module)

# ▶️ Lancer le bot
if __name__ == "__main__":
    load_cogs()
    keep_alive()  # Si utilisé
    bot.run(TOKEN)
