import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os

# Chemin vers le JSON
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

def load_deck_data():
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

class DeckSelectView(View):
    def __init__(self, bot, deck_data):
        super().__init__(timeout=60)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self, list(deck_data.keys())))

class SaisonSelect(Select):
    def __init__(self, view, saisons):
        options = [discord.SelectOption(label=saison, value=saison) for saison in saisons]
        super().__init__(placeholder="Choisis une saison", min_values=1, max_values=1, options=options)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        duellistes = list(self.view.deck_data[saison].keys())
        new_view = DuellisteSelectView(self.view.bot, self.view.deck_data, saison, duellistes)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None
        )

class DuellisteSelectView(View):
    def __init__(self, bot, deck_data, saison, duellistes):
        super().__init__(timeout=60)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self, saison, duellistes))

class DuellisteSelect(Select):
    def __init__(self, view, saison, duellistes):
        options = [discord.SelectOption(label=d, value=d) for d in duellistes]
        super().__init__(placeholder="Choisis un duelliste", min_values=1, max_values=1, options=options)
        self.view = view
        self.saison = saison

    async def callback(self, interaction: discord.Interaction):
        duelliste = self.values[0]
        info = self.view.deck_data[self.saison][duelliste]
        embed = discord.Embed(
            title=f"📘 Deck de {duelliste} ({self.saison})",
            description=info,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(content=None, embed=embed, view=None)

class DeckCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deck", help="Choisis une saison et un duelliste pour voir son deck.")
    async def deck(self, ctx):
        deck_data = load_deck_data()
        view = DeckSelectView(self.bot, deck_data)
        await ctx.send("📚 Sélectionne une saison :", view=view)

    def cog_load(self):
        self.deck.category = "Général"

async def setup(bot):
    await bot.add_cog(DeckCommand(bot))
