from keep_alive import keep_alive

import os
import json
import random
import discord
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand
from discord.ui import View, Select
from discord import SelectOption, Embed
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import pytz

# Charger les variables d’environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Charger les citations Yu-Gi-Oh!
with open("quotes.json", encoding="utf-8") as f:
    YUGIOH_QUOTES = json.load(f)

# Charger les données JSON pour les decks
with open("deck_data.json", encoding="utf-8") as f:
    DECK_DATA = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

# 💬 Help personnalisé
class YuGiOhHelpCommand(DefaultHelpCommand):
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
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Ton deck est prêt.")
        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)

# ─────────────────────────────────────────────
# Commandes général
# ─────────────────────────────────────────────

@bot.command(name="ping")
async def ping(ctx):
    """Affiche la latence du bot."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Latence du bot : **{latency}ms**",
        color=discord.Color.green() if latency < 150 else discord.Color.orange()
    )
    await ctx.send(embed=embed)

ping.category = "Général"

# ─────────────────────────────────────────────
# Fun
# ─────────────────────────────────────────────

@bot.command(name="quote")
async def quote(ctx):
    """Affiche une citation aléatoire de Yu-Gi-Oh!."""
    citation = random.choice(YUGIOH_QUOTES)
    embed = discord.Embed(
        title="🎙️ Citation Yu-Gi-Oh!",
        description=f"\"{citation}\"",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Crois au cœur des cartes !")
    await ctx.send(embed=embed)

quote.category = "Fun"

# ─────────────────────────────────────────────
# VAACT : Decks
# ─────────────────────────────────────────────

@bot.command(name="deck")
async def deck(ctx):
    """Choisis une saison puis un duelliste pour voir son deck."""
    class SaisonSelect(Select):
        def __init__(self):
            options = [SelectOption(label=saison, value=saison) for saison in DECK_DATA.keys()]
            super().__init__(
                placeholder="📅 Choisis une saison",
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, interaction: discord.Interaction):
            saison = self.values[0]
            duellistes = DECK_DATA[saison]

            class DuellisteSelect(Select):
                def __init__(self):
                    options = [SelectOption(label=nom, value=nom) for nom in duellistes.keys()]
                    super().__init__(
                        placeholder=f"🎭 Duellistes de {saison}",
                        options=options,
                        min_values=1,
                        max_values=1
                    )

                async def callback(self2, interaction2: discord.Interaction):
                    nom = self2.values[0]
                    description = duellistes[nom]
                    embed = Embed(
                        title=f"🃏 Deck de {nom}",
                        description=description,
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"Saison sélectionnée : {saison}")
                    await interaction2.response.send_message(embed=embed, ephemeral=True)

            duel_view = View()
            duel_view.add_item(DuellisteSelect())
            await interaction.response.send_message(
                content=f"🎴 Sélectionne un duelliste pour la saison **{saison}** :",
                view=duel_view,
                ephemeral=True
            )

    view = View()
    view.add_item(SaisonSelect())
    await ctx.send("📚 Sélectionne une saison du tournoi Yu-Gi-Oh VAACT :", view=view)

deck.category = "VAACT"

# ─────────────────────────────────────────────
# 🏆 Commande tournoi
# ─────────────────────────────────────────────

@bot.command(name="tournoi")
async def tournoi(ctx):
    """Affiche les infos du prochain tournoi."""
    try:
        data = supabase.table("tournoi").select("*").limit(1).execute()
        if not data.data:
            await ctx.send("❌ Aucun tournoi n’est actuellement planifié.")
            return

        tournoi = data.data[0]
        date_obj = datetime.fromisoformat(tournoi["date"]).astimezone(pytz.timezone("Europe/Paris"))
        decks_pris = tournoi.get("decks_pris", [])
        decks_disponibles = tournoi.get("decks_disponibles", [])
        max_places = tournoi.get("max_places", 0)
        places_restantes = max_places - len(decks_pris)

        embed = discord.Embed(
            title="📅 Prochain Tournoi Yu-Gi-Oh!",
            color=discord.Color.red()
        )
        embed.add_field(name="🗓️ Date", value=date_obj.strftime("%d %B %Y à %Hh%M"), inline=False)
        embed.add_field(name="🎟️ Places restantes", value=f"{places_restantes} / {max_places}", inline=False)
        embed.add_field(name="🃏 Decks pris", value=", ".join(decks_pris) if decks_pris else "Aucun", inline=False)
        embed.add_field(name="📦 Decks restants", value=", ".join(decks_disponibles) if decks_disponibles else "Aucun", inline=False)
        embed.set_footer(text="Inscris-toi vite avant que les decks ne disparaissent !")

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Erreur tournoi: {e}")
        await ctx.send("❌ Une erreur est survenue en accédant aux infos du tournoi.")

tournoi.category = "VAACT"

# ▶️ Lancer le bot
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
