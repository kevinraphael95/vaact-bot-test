# ────────────────────────────────────────────────────────────────────────────────
# 📌 infos_vaact.py — Commande interactive !infosvaact
# Objectif : Affiche des informations issues d'un fichier JSON structuré (type VAAct)
# Catégorie : VAACT
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
# 📂 Chargement des données JSON
# ────────────────────────────────────────────────────────────────────────────────
DATA_JSON_PATH = os.path.join("data", "vaact_infos.json")

def load_data():
    """Charge les données depuis le fichier JSON."""
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Menu principal de sélection
# ────────────────────────────────────────────────────────────────────────────────
class FirstSelectView(View):
    """Vue principale pour choisir une catégorie."""
    def __init__(self, bot, data):
        super().__init__(timeout=120)
        self.bot = bot
        self.data = data
        self.add_item(FirstSelect(self))

class FirstSelect(Select):
    """Menu déroulant pour sélectionner une catégorie."""
    def __init__(self, parent_view: FirstSelectView):
        self.parent_view = parent_view
        options = [discord.SelectOption(label=key, value=key) for key in self.parent_view.data.keys()]
        super().__init__(placeholder="Choisis une catégorie", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_key = self.values[0]
        new_view = SecondSelectView(self.parent_view.bot, self.parent_view.data, selected_key)
        await interaction.response.edit_message(
            content=f"Catégorie sélectionnée : **{selected_key}**\nChoisis maintenant un élément :",
            embed=None,
            view=new_view
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Menu secondaire de sélection
# ────────────────────────────────────────────────────────────────────────────────
class SecondSelectView(View):
    """Vue secondaire pour choisir un élément dans une catégorie."""
    def __init__(self, bot, data, key):
        super().__init__(timeout=120)
        self.bot = bot
        self.data = data
        self.key = key
        self.add_item(SecondSelect(self))

class SecondSelect(Select):
    """Menu déroulant pour sélectionner un élément."""
    def __init__(self, parent_view: SecondSelectView):
        self.parent_view = parent_view
        sub_options = list(self.parent_view.data[self.parent_view.key].keys())
        options = [discord.SelectOption(label=sub, value=sub) for sub in sub_options]
        super().__init__(placeholder="Choisis un élément", options=options)

    async def callback(self, interaction: discord.Interaction):
        key = self.parent_view.key
        sub_key = self.values[0]
        infos = self.parent_view.data[key][sub_key]

        embed = discord.Embed(
            title=f"{sub_key} ({key})",
            color=discord.Color.teal()
        )
        for field_name, field_value in infos.items():
            if isinstance(field_value, list):
                value = "\n".join(f"• {item}" for item in field_value)
            else:
                value = str(field_value)
            embed.add_field(name=field_name.capitalize(), value=value, inline=False)

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class InfosVaact(commands.Cog):
    """
    Commande !infosvaact — Affiche des infos interactives depuis un fichier structuré
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="infosvaact",
        help="Affiche des infos VAAct de manière interactive.",
        description="Affiche les informations d'une base VAAct via un menu interactif."
    )
    async def infosvaact(self, ctx: commands.Context):
        """Commande principale pour interagir avec les infos VAAct."""
        try:
            data = load_data()
            view = FirstSelectView(self.bot, data)
            await ctx.send("🔍 Choisis une catégorie :", view=view)
        except Exception as e:
            print(f"[ERREUR infosvaact] {e}")
            await ctx.send("❌ Une erreur est survenue lors du chargement des données.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = InfosVaact(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)

