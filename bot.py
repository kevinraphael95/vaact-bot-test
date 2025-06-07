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
from discord.ui import View, button
from discord import ButtonStyle, Interaction
from discord.ext.commands import Context

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
            title="👑 Atem, Roi des Duellistes, s’avance.",
            description=(
                f"Je suis **Atem**, l’esprit du Pharaon, gardien des **Duels des Ténèbres** et protecteur du **Royaume des Ombres**.\n"
                "Tu m’as appelé, duelliste ?\n\n"
                f"Utilise la commande `{prefix}help` pour voir mes commandes.\n"
                f"Utilise la commande `{prefix}info` pour voir les derniers ajouts du bot."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Tu dois croire en l'âme des cartes 🎴")

        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        ctx = await bot.get_context(message)
        view = MentionButtons(bot, ctx)
        msg = await message.channel.send(embed=embed, view=view)
        view.response_message = msg
        return




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
# 🔘 Boutons
# ──────────────────────────────────────────────────────────────

class MentionButtons(View):
    def __init__(self, bot, ctx: Context):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.response_message = None

    async def invoke_command(self, interaction: Interaction, command_name: str):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Ce bouton ne t'est pas destiné.", ephemeral=True)
            return

        await interaction.response.defer()

        # Créer un contexte à partir de l'interaction
        ctx = await self.bot.get_context(interaction.message)
        ctx.interaction = interaction  # Important : pour que la commande sache d'où vient l'interaction
        ctx.author = interaction.user
        ctx.channel = interaction.channel
        ctx.guild = interaction.guild
        ctx.message = interaction.message

        # Simuler la commande tapée : "!help" ou "!info"
        # Attention, bot.command_prefix est dynamique, mais ici on utilise directement le préfixe
        prefix = self.bot.command_prefix(self.bot, ctx.message)
        fake_message_content = f"{prefix}{command_name}"
        ctx.message.content = fake_message_content

        # Refaire le contexte depuis ce faux message
        ctx = await self.bot.get_context(ctx.message, cls=type(ctx))

        # Invoker la commande
        await self.bot.invoke(ctx)

    @button(label="📖 Help", style=ButtonStyle.primary)
    async def help_button(self, interaction: Interaction, button):
        await self.invoke_command(interaction, "help")

    @button(label="ℹ️ Info", style=ButtonStyle.secondary)
    async def info_button(self, interaction: Interaction, button):
        await self.invoke_command(interaction, "info")

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.response_message:
            await self.response_message.edit(view=self)




# ──────────────────────────────────────────────────────────────
# 🚀 Lancement
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive()

    async def start():
        await load_commands()
        await bot.start(TOKEN)

    asyncio.run(start())
