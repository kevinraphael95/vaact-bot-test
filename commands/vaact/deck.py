# =======================
# 📦 IMPORTS
# =======================
import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os

# =======================
# 📂 CHEMIN VERS LE FICHIER JSON
# =======================
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

# =======================
# 📚 Chargement des données JSON
# =======================
def load_deck_data():
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# =======================
# 🎛️ Vue 1 : Choix de la saison
# =======================
class DeckSelectView(View):
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))


class SaisonSelect(Select):
    def __init__(self, parent_view: DeckSelectView):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=saison, value=saison)
            for saison in self.parent_view.deck_data.keys()
        ]
        super().__init__(placeholder="📅 Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        new_view = DuellisteSelectView(
            self.parent_view.bot,
            self.parent_view.deck_data,
            saison
        )
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\n👤 Choisis un duelliste :",
            view=new_view,
            embed=None
        )

# =======================
# 🎛️ Vue 2 : Choix du duelliste
# =======================
class DuellisteSelectView(View):
    def __init__(self, bot, deck_data, saison):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self))


class DuellisteSelect(Select):
    def __init__(self, parent_view: DuellisteSelectView):
        self.parent_view = parent_view
        duellistes = list(self.parent_view.deck_data[self.parent_view.saison].keys())
        options = [
            discord.SelectOption(label=d, value=d)
            for d in duellistes
        ]
        super().__init__(placeholder="👤 Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.parent_view.saison
        duelliste = self.values[0]
        infos = self.parent_view.deck_data[saison][duelliste]

        deck_text = infos.get("deck", "❌ Aucun deck trouvé.")
        astuces_text = infos.get("astuces", "❌ Aucune astuce disponible.")

        embed = discord.Embed(
            title=f"🧙‍♂️ Deck de {duelliste}",
            description=f"📅 Saison : **{saison}**",
            color=discord.Color.dark_blue()
        )
        embed.add_field(name="📘 Deck(s)", value=deck_text, inline=False)
        embed.add_field(name="💡 Astuces", value=astuces_text, inline=False)

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# =======================
# 🧠 COG Deck
# =======================
class Deck(commands.Cog):
    """Commande interactive pour consulter les decks des duellistes par saison."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="deck",
        help="Affiche les decks d’un duelliste par saison.",
        description="Affiche une interface pour choisir une saison et un duelliste.",
    )
    async def deck_command(self, ctx: commands.Context):
        try:
            deck_data = load_deck_data()
            view = DeckSelectView(self.bot, deck_data)
            await ctx.send("📦 Choisis une saison :", view=view)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du chargement des decks : {e}")

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    cog = Deck(bot)

    # Ajout de la catégorie personnalisée "VAACT"
    for command in cog.get_commands():
        command.category = "VAACT"

    await bot.add_cog(cog)
