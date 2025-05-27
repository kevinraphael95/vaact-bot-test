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

# Vue pour choisir une saison
class DeckSelectView(View):
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))

class SaisonSelect(Select):
    def __init__(self, view):
        self.view = view
        options = [discord.SelectOption(label=saison, value=saison) for saison in self.view.deck_data.keys()]
        super().__init__(placeholder="Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        new_view = DuellisteSelectView(self.view.bot, self.view.deck_data, saison)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :", 
            view=new_view,
            embed=None
        )

# Vue pour choisir un duelliste
class DuellisteSelectView(View):
    def __init__(self, bot, deck_data, saison):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self))

class DuellisteSelect(Select):
    def __init__(self, view):
        self.view = view
        duellistes = list(self.view.deck_data[self.view.saison].keys())
        options = [discord.SelectOption(label=d, value=d) for d in duellistes]
        super().__init__(placeholder="Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.view.saison
        duelliste = self.values[0]
        cartes = self.view.deck_data[saison][duelliste]

        embed = discord.Embed(
            title=f"Deck de {duelliste} (Saison {saison})",
            description="\n".join(f"- {carte}" for carte in cartes),
            color=discord.Color.blue()
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# ──────────────────────────────────────────────────────────────
# 📦 Cog pour enregistrer la commande
# ──────────────────────────────────────────────────────────────

class DeckCommand(commands.Cog):
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

# Setup pour charger le cog
async def setup(bot):
    await bot.add_cog(DeckCommand(bot))
