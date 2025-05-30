# ────────────────────────────────────────────────────────────────────────────────
# 📁 deck.py — Commande interactive !deck
# ────────────────────────────────────────────────────────────────────────────────
# Permet à l'utilisateur de sélectionner une saison et un duelliste pour consulter
# son deck et ses astuces. Utilise les menus déroulants interactifs (UI Discord).
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                  # 🎨 Embeds et UI Discord
from discord.ext import commands                # ⚙️ Framework de commandes
from discord.ui import View, Select             # 🎛️ Interfaces utilisateur (menus déroulants)
import json                                     # 📄 Lecture des fichiers JSON
import os                                       # 🗂️ Gestion des chemins de fichiers

# ────────────────────────────────────────────────────────────────────────────────
# 📂 CHEMIN VERS LE FICHIER JSON
# ────────────────────────────────────────────────────────────────────────────────
DECK_JSON_PATH = os.path.join("data", "deck_data.json")  # 📁 data/deck_data.json

# ────────────────────────────────────────────────────────────────────────────────
# 📚 Chargement du contenu JSON
# ────────────────────────────────────────────────────────────────────────────────
def load_deck_data():
    """Charge les données de deck depuis le fichier JSON."""
    with open(DECK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ VUE 1 — Choix de la saison
# ────────────────────────────────────────────────────────────────────────────────
class DeckSelectView(View):
    """Vue interactive pour choisir une saison."""
    def __init__(self, bot, deck_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.add_item(SaisonSelect(self))  # Ajoute le menu déroulant des saisons

class SaisonSelect(Select):
    """Menu déroulant pour sélectionner une saison."""
    def __init__(self, parent_view: DeckSelectView):
        self.parent_view = parent_view

        # Génère les options du menu depuis les clés JSON (saisons)
        options = [
            discord.SelectOption(label=saison, value=saison)
            for saison in self.parent_view.deck_data.keys()
        ]
        super().__init__(placeholder="📅 Choisis une saison", options=options)

    async def callback(self, interaction: discord.Interaction):
        """Action lorsque l'utilisateur sélectionne une saison."""
        saison = self.values[0]
        new_view = DuellisteSelectView(self.parent_view.bot, self.parent_view.deck_data, saison)

        await interaction.response.edit_message(
            content=f"🎴 Saison choisie : **{saison}**\nSélectionne un duelliste :",
            view=new_view,
            embed=None  # Supprime l’ancien embed
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ VUE 2 — Choix du duelliste
# ────────────────────────────────────────────────────────────────────────────────
class DuellisteSelectView(View):
    """Vue interactive pour choisir un duelliste d'une saison donnée."""
    def __init__(self, bot, deck_data, saison):
        super().__init__(timeout=120)
        self.bot = bot
        self.deck_data = deck_data
        self.saison = saison
        self.add_item(DuellisteSelect(self))  # Menu déroulant des duellistes

class DuellisteSelect(Select):
    """Menu déroulant pour choisir un duelliste."""
    def __init__(self, parent_view: DuellisteSelectView):
        self.parent_view = parent_view

        duellistes = list(self.parent_view.deck_data[self.parent_view.saison].keys())
        options = [
            discord.SelectOption(label=d, value=d)
            for d in duellistes
        ]
        super().__init__(placeholder="👤 Choisis un duelliste", options=options)

    async def callback(self, interaction: discord.Interaction):
        """Action lorsque l'utilisateur choisit un duelliste."""
        saison = self.parent_view.saison
        duelliste = self.values[0]
        infos = self.parent_view.deck_data[saison][duelliste]

        # 🔎 Récupération des données
        deck_data = infos.get("deck", "❌ Aucun deck trouvé.")
        astuces_data = infos.get("astuces", "❌ Aucune astuce disponible.")

        # 🧾 Formatage propre (liste ou texte brut)
        deck_text = "\n".join(f"• {item}" for item in deck_data) if isinstance(deck_data, list) else deck_data
        astuces_text = "\n".join(f"• {item}" for item in astuces_data) if isinstance(astuces_data, list) else astuces_data

        # 📑 Embed final
        embed = discord.Embed(
            title=f"🧙‍♂️ Deck de {duelliste} (Saison {saison})",
            color=discord.Color.blue()
        )
        embed.add_field(name="📘 Deck(s)", value=deck_text, inline=False)
        embed.add_field(name="💡 Astuces", value=astuces_text, inline=False)

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None  # ❌ Supprime les menus pour figer la réponse
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 COG : Deck
# ────────────────────────────────────────────────────────────────────────────────
class Deck(commands.Cog):
    """Commande interactive pour consulter les decks des duellistes par saison."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────
    # 📥 COMMANDE : !deck
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="deck",
        help="Affiche les decks d’un duelliste par saison.",
        description="Affiche une interface pour choisir une saison et un duelliste."
    )
    async def deck_command(self, ctx: commands.Context):
        """Commande principale appelée avec !deck"""
        try:
            deck_data = load_deck_data()  # 📦 Charge les données depuis le fichier
            view = DeckSelectView(self.bot, deck_data)
            await ctx.send("📦 Choisis une saison :", view=view)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du chargement des decks : {e}")

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """Fonction appelée pour enregistrer ce cog."""
    cog = Deck(bot)

    # 🏷️ Attribution manuelle d'une catégorie personnalisée
    for command in cog.get_commands():
        command.category = "VAACT"

    await bot.add_cog(cog)
