# ────────────────────────────────────────────────────────────────────────────────
# 🎴 deck.py — Commande interactive !deck
# Objectif : Choisir une saison et un duelliste pour afficher son deck et ses astuces
# Catégorie : 🧠 VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données JSON — deck_data.json
# ────────────────────────────────────────────────────────────────────────────────
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

def load_deck_data():
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Sélection de saison et duelliste
# ────────────────────────────────────────────────────────────────────────────────
class DeckSelectView(View):
    def __init__(self, bot, deck_data, saison=None, duelliste=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison or list(deck_data.keys())[0]
        self.duelliste = duelliste
        self.add_item(SaisonSelect(self))
        self.add_item(DuellisteSelect(self))

class SaisonSelect(Select):
    def __init__(self, parent_view: DeckSelectView):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=s, value=s, default=(s == self.parent_view.saison))
            for s in self.parent_view.deck_data
        ]
        super().__init__(placeholder="📅 Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        if saison == self.parent_view.saison:
            await interaction.response.defer()
            return
        new_view = DeckSelectView(self.parent_view.bot, self.parent_view.deck_data, saison)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None
        )

class DuellisteSelect(Select):
    def __init__(self, parent_view: DeckSelectView):
        self.parent_view = parent_view
        duellistes = list(self.parent_view.deck_data[self.parent_view.saison].keys())
        options = [
            discord.SelectOption(label=d, value=d, default=(d == self.parent_view.duelliste))
            for d in duellistes
        ]
        super().__init__(placeholder="👤 Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.parent_view.saison
        duelliste = self.values[0]
        if duelliste == self.parent_view.duelliste:
            await interaction.response.defer()
            return

        infos = self.parent_view.deck_data[saison][duelliste]

        deck_data = infos.get("deck", "❌ Aucun deck trouvé.")
        astuces_data = infos.get("astuces", "❌ Aucune astuce disponible.")

        deck_text = "\n".join(f"• {c}" for c in deck_data) if isinstance(deck_data, list) else deck_data
        astuces_text = "\n".join(f"• {a}" for a in astuces_data) if isinstance(astuces_data, list) else astuces_data

        embed = discord.Embed(
            title=f"🧙‍♂️ Deck de {duelliste} (Saison {saison})",
            color=discord.Color.blue()
        )
        embed.add_field(name="📘 Deck(s)", value=deck_text, inline=False)
        embed.add_field(name="💡 Astuces", value=astuces_text, inline=False)

        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            embed=embed,
            view=DeckSelectView(self.parent_view.bot, self.parent_view.deck_data, saison, duelliste)
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Deck
# ────────────────────────────────────────────────────────────────────────────────
class Deck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="deck",
        help="Affiche les decks d’un duelliste par saison.",
        description="Affiche une interface interactive pour choisir une saison et un duelliste."
    )
    async def deck(self, ctx: commands.Context):
        try:
            deck_data = load_deck_data()
            view = DeckSelectView(self.bot, deck_data)
            await ctx.send("📦 Choisis une saison :", view=view)
        except Exception as e:
            print("[ERREUR DECK]", e)
            await ctx.send("❌ Une erreur est survenue lors du chargement des decks.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Deck(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
