# ────────────────────────────────────────────────────────────────────────────────
# 🎴 deck.py — Commande interactive !deck
# Objectif : Choisir une saison et un duelliste pour afficher son deck et ses astuces
# Catégorie : 🧠 VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # 🎨 Embeds, interactions et menus
from discord.ext import commands              # 🧩 Framework de commandes avec Cogs
from discord.ui import View, Select           # 🎛️ Menus déroulants interactifs
import json                                    # 📄 Lecture de fichiers JSON
import os                                      # 🗂️ Gestion des chemins

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données JSON — deck_data.json
# ────────────────────────────────────────────────────────────────────────────────
DECK_JSON_PATH = os.path.join("data", "deck_data.json")

def load_deck_data():
    """Charge les données des decks depuis le fichier JSON."""
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Sélection de saison
# ────────────────────────────────────────────────────────────────────────────────
class DeckSelectView(View):
    """Vue principale pour choisir une saison."""
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))

class SaisonSelect(Select):
    """Menu pour sélectionner une saison."""
    def __init__(self, parent_view: DeckSelectView):
        self.parent_view = parent_view
        options = [discord.SelectOption(label=s, value=s) for s in self.parent_view.deck_data]
        super().__init__(placeholder="📅 Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.values[0]
        new_view = DuellisteSelectView(self.parent_view.bot, self.parent_view.deck_data, saison)
        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Sélection de duelliste
# ────────────────────────────────────────────────────────────────────────────────
class DuellisteSelectView(View):
    """Vue secondaire pour choisir un duelliste."""
    def __init__(self, bot, deck_data, saison):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self))

class DuellisteSelect(Select):
    """Menu pour sélectionner un duelliste."""
    def __init__(self, parent_view: DuellisteSelectView):
        self.parent_view = parent_view
        duellistes = list(self.parent_view.deck_data[self.parent_view.saison].keys())
        options = [discord.SelectOption(label=d, value=d) for d in duellistes]
        super().__init__(placeholder="👤 Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        saison = self.parent_view.saison
        duelliste = self.values[0]
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
            content=None,
            embed=embed,
            view=None
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Deck
# ────────────────────────────────────────────────────────────────────────────────
class Deck(commands.Cog):
    """
    🎴 Commande !deck — Interface interactive pour consulter les decks
    Permet de naviguer par saison et duelliste pour afficher les données liées.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !deck
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="deck",
        help="Affiche les decks d’un duelliste par saison.",
        description="Affiche une interface interactive pour choisir une saison et un duelliste."
    )
    async def deck(self, ctx: commands.Context):
        """
        📚 Affiche un menu déroulant pour consulter les decks disponibles selon les saisons et les duellistes.
        """
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
    """
    🔧 Setup du Cog : ajoute le cog au bot et attribue une catégorie personnalisée
    """
    cog = Deck(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
