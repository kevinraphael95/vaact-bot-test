import discord
from discord.ext import commands
import os
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

# Fonction pour charger tous les fichiers .py dans un dossier de commandes
def load_commands_from_folder(folder: Path):
    for file in folder.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_path = f"commands.{folder.name}.{file.stem}"
        try:
            bot.load_extension(module_path)
            print(f"✅ Commande chargée : {module_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {module_path} : {e}")

# Charger les commandes des sous-dossiers 'ygo' et 'general'
for subfolder in ["general", "ygo"]:
    load_commands_from_folder(Path("commands") / subfolder)

# Lancer le bot
if __name__ == "__main__":
    bot.run(TOKEN)
