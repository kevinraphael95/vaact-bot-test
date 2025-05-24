# bot.py

from keep_alive import keep_alive

import os
import discord
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True

# 💬 Help personnalisé avec catégories
class YuGiOhHelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        return f"Utilise `{self.clean_prefix}help <commande>` pour plus de détails sur une commande."

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=YuGiOhHelpCommand(
    command_attrs={
        "name": "help",
        "help": "Affiche les commandes disponibles, classées par catégories.",
    }
))

# 🔔 Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("Yu-Gi-Oh! Duelist Mode"))

# 📌 Répondre à la mention du bot
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
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else discord.Embed.Empty)
        embed.set_footer(text="Ton deck est prêt.")
        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)

# Commandes simples
@bot.command(name="ping")
async def ping(ctx):
    """Test de latence."""
    await ctx.send("🏓 Pong !")
ping.category = "Général"

@bot.command(name="carte")
async def carte(ctx, *, nom: str):
    """Renvoie une carte Yu-Gi-Oh en fonction de son nom (mock)."""
    await ctx.send(f"🔍 Recherche de la carte **{nom}**... (fonction à venir)")
carte.category = "Cartes"

# ▶️ Lancer le bot
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
