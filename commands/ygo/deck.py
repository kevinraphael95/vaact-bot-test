import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os

# ───────────────────────────────────────────────
# Chargement des données
# ───────────────────────────────────────────────
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

def load_deck_data():
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ───────────────────────────────────────────────
# Vue principale : Choix de saison
# ───────────────────────────────────────────────
class DeckSelectView(View):
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))

class SaisonSelect(Select):
    def __init__(self, view):
        self.view = view
        options = [discord.SelectOption(label=saison, value=saison) for saison in self.view.deck_data]
        super().__init__(placeholder="Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        new_view = DuellisteSelectView(self.view.bot, self.view.deck_data, saison)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None
        )

# ───────────────────────────────────────────────
# Vue secondaire : Choix de duelliste
# ───────────────────────────────────────────────
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
        duellistes = self.view.deck_data[self.view.saison]
        options = [discord.SelectOption(label=name, value=name) for name in duellistes]
        super().__init__(placeholder="Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        duelliste = self.values[0]
        deck = self.view.deck_data[self.view.saison][duelliste]

        embed = discord.Embed(
            title=f"🃏 Deck de {duelliste}",
            description=deck,
            color=discord.Color.gold()
        )

        await interaction.response.edit_message(content=None, view=None, embed=embed)

# ───────────────────────────────────────────────
# Commande du bot
# ───────────────────────────────────────────────
class Deck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deck")
    async def deck(self, ctx):
        try:
            deck_data = load_deck_data()
        except Exception as e:
            await ctx.send("❌ Erreur lors du chargement des decks.")
            return

        await ctx.send("📚 Choisis une saison :", view=DeckSelectView(self.bot, deck_data))

# ───────────────────────────────────────────────
# Setup
# ───────────────────────────────────────────────
async def setup(bot):
    await bot.add_cog(Deck(bot))
