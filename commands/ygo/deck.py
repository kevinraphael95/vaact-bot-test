import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os

# Chemin vers le fichier JSON
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

def load_deck_data():
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────
# Vue principale : Choix saison
# ─────────────────────────────
class DeckSelectView(View):
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))

class SaisonSelect(Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = [discord.SelectOption(label=saison, value=saison) for saison in self.parent_view.deck_data.keys()]
        super().__init__(placeholder="Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        new_view = DuellisteSelectView(self.parent_view.bot, self.parent_view.deck_data, saison)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None
        )

# ───────────────────────────────
# Vue secondaire : Choix duelliste
# ───────────────────────────────
class DuellisteSelectView(View):
    def __init__(self, bot, deck_data, saison):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self))

class DuellisteSelect(Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        duellistes = list(self.parent_view.deck_data[self.parent_view.saison].keys())
        options = [discord.SelectOption(label=d, value=d) for d in duellistes]
        super().__init__(placeholder="Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.parent_view.saison
        duelliste = self.values[0]
        cartes = self.parent_view.deck_data[saison][duelliste]

        embed = discord.Embed(
            title=f"Deck de {duelliste} (Saison {saison})",
            description=cartes,
            color=discord.Color.blue()
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# ────────────────────────────────
# 📦 Cog pour enregistrer la commande
# ────────────────────────────────
class Deck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deck")
    async def deck_command(self, ctx):
        """Affiche le deck d’un duelliste"""
        try:
            deck_data = load_deck_data()
            view = DeckSelectView(self.bot, deck_data)
            await ctx.send("📦 Choisis une saison :", view=view)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du chargement des decks : {e}")

# ─────────────
# Setup du Cog
# ─────────────
async def setup(bot):
    await bot.add_cog(Deck(bot))
