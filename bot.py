from keep_alive import keep_alive
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

# 💬 Help personnalisé
class YuGiOhHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return f"Utilise `{self.context.prefix}help <commande>` pour plus de détails sur une commande."

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

# 🔁 Charger les cogs
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("Yu-Gi-Oh! Duelist Mode"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions and len(message.mentions) == 1:
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
    await bot.process_commands(message)

# Charger les commandes
bot.load_extension("commands.general")
bot.load_extension("commands.ygo")
bot.load_extension("commands.vaact")

# ▶️ Lancer le bot
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
