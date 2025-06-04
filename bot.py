# ──────────────────────────────────────────────────────────────
# 🟢 Serveur Keep-Alive (Render)
# ──────────────────────────────────────────────────────────────
from keep_alive import keep_alive

# ──────────────────────────────────────────────────────────────
# 📦 Modules standards
# ──────────────────────────────────────────────────────────────
import os
import json
import uuid
import random
from datetime import datetime, timezone
import asyncio

# ──────────────────────────────────────────────────────────────
# 📦 Modules tiers
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from dotenv import load_dotenv
from dateutil import parser

# ──────────────────────────────────────────────────────────────
# 📦 Modules internes
# ──────────────────────────────────────────────────────────────
from supabase_client import supabase

# ──────────────────────────────────────────────────────────────
# 🔧 Initialisation de l’environnement
# ──────────────────────────────────────────────────────────────

# Se placer dans le dossier du script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d’environnement (.env)
load_dotenv()

# Clés importantes
TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
INSTANCE_ID = str(uuid.uuid4())

# Enregistrer cette instance
with open("instance_id.txt", "w") as f:
    f.write(INSTANCE_ID)

# Fonction pour le préfixe dynamique (ici statique)
def get_prefix(bot, message):
    return COMMAND_PREFIX

# ──────────────────────────────────────────────────────────────
# ⚙️ Intents & Création du bot
# ──────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)
bot.is_main_instance = False

# ──────────────────────────────────────────────────────────────
# 🔌 Chargement dynamique des commandes depuis /commands/*
# ──────────────────────────────────────────────────────────────
async def load_commands():
    for category in os.listdir("commands"):
        cat_path = os.path.join("commands", category)
        if os.path.isdir(cat_path):
            for filename in os.listdir(cat_path):
                if filename.endswith(".py"):
                    path = f"commands.{category}.{filename[:-3]}"
                    try:
                        await bot.load_extension(path)
                        print(f"✅ Loaded {path}")
                    except Exception as e:
                        print(f"❌ Failed to load {path}: {e}")

# ──────────────────────────────────────────────────────────────
# 🔔 On Ready : présence + verrouillage forcé de l’instance
# ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Duel Monsters"))

    try:
        # Forcer le verrou avec la nouvelle instance à chaque redémarrage
        now = datetime.now(timezone.utc).isoformat()
        supabase.table("bot_lock").upsert({
            "id": "bot_lock",
            "instance_id": INSTANCE_ID,
            "updated_at": now
        }).execute()

        print(f"🔐 Verrou mis à jour pour cette instance : {INSTANCE_ID}")
        bot.is_main_instance = True

    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du verrou : {e}")
        bot.is_main_instance = False

# ──────────────────────────────────────────────────────────────
# 📩 Message reçu : réagir aux mots-clés et lancer les commandes
# ──────────────────────────────────────────────────────────────
@bot.event
async def on_message(message):
    try:
        lock = supabase.table("bot_lock").select("instance_id").eq("id", "bot_lock").execute()
        if lock.data and isinstance(lock.data, list):
            if lock.data and lock.data[0].get("instance_id") != INSTANCE_ID:
                return
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du lock : {e}")
        return

    if message.author.bot:
        return

    contenu = message.content.lower()

    # Réponse en embed si le bot est mentionné seul
    if bot.user in message.mentions and len(message.mentions) == 1:
        prefix = get_prefix(bot, message)

        embed = discord.Embed(
            title="👋 Yo, je suis le bot YuGiOh !",
            description=f"Utilise `{prefix}help` pour voir ce que je peux faire.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Tu dois croire en l'âme des cartes 🎴")

        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        else:
            embed.set_thumbnail(url=bot.user.default_avatar.url)

        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)


# ──────────────────────────────────────────────────────────────
# ❗ Gestion des erreurs de commandes
# ──────────────────────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry = round(error.retry_after, 1)
        await ctx.send(f"⏳ Cette commande est en cooldown. Réessaie dans `{retry}` secondes.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas les permissions pour cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Il manque un argument à cette commande.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        raise error

# ──────────────────────────────────────────────────────────────
# 🚀 Lancement
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive()

    async def start():
        await load_commands()
        await bot.start(TOKEN)

    asyncio.run(start())
