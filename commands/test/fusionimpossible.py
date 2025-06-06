# ────────────────────────────────────────────────────────────────────────────────
# 📌 fusionimpossible.py — Commande interactive /slash fusionimpossible
# Objectif : Fusionne nom, type et effets de deux vraies cartes Yu-Gi-Oh!
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from discord.ui import View, Button
import requests

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 Fonctions utilitaires
# ────────────────────────────────────────────────────────────────────────────────
def generer_nom(nom1, nom2):
    nom1_part = nom1.split()[0] if " " in nom1 else nom1[:len(nom1)//2]
    nom2_part = nom2.split()[-1] if " " in nom2 else nom2[len(nom2)//2:]
    return f"{nom1_part} {nom2_part}"

def fusionner_types(type1, type2):
    types = list({type1, type2} - {None})
    return " / ".join(types) if types else "Inconnu"

def fusionner_effets(effet1, effet2):
    if not effet1 and not effet2:
        return "Aucun effet."
    if effet1 and effet2:
        return f"{effet1.strip()}\n\n{effet2.strip()}"
    return effet1 or effet2

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Vue interactive avec bouton pour lancer la fusion
# ────────────────────────────────────────────────────────────────────────────────
class FusionImpossibleView(View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.carte1 = None
        self.carte2 = None

    @discord.ui.button(label="Fusionner deux cartes aléatoires", style=discord.ButtonStyle.primary)
    async def fusion_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        try:
            url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"
            self.carte1 = requests.get(url).json()
            self.carte2 = requests.get(url).json()

            nom_fusion = generer_nom(self.carte1["name"], self.carte2["name"])
            type_fusion = fusionner_types(self.carte1.get("type"), self.carte2.get("type"))
            effet_fusion = fusionner_effets(self.carte1.get("desc"), self.carte2.get("desc"))

            embed = discord.Embed(
                title=f"🧪 Fusion Impossible : {nom_fusion}",
                description=f"**Type :** {type_fusion}\n\n**Effet combiné :**\n{effet_fusion}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=self.carte1.get("card_images", [{}])[0].get("image_url", ""))
            embed.set_image(url=self.carte2.get("card_images", [{}])[0].get("image_url", ""))
            embed.set_footer(text=f"Fusion de « {self.carte1['name']} » + « {self.carte2['name']} »")

            await interaction.edit_original_response(embed=embed, content=None, view=None)

        except Exception as e:
            print(f"[ERREUR fusionimpossible] {e}")
            await interaction.edit_original_response(content="❌ Une erreur est survenue lors de la fusion.", embed=None, view=None)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class FusionImpossible(commands.Cog):
    """
    Commande /fusionimpossible — Fusionne deux vraies cartes Yu-Gi-Oh!
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="fusionimpossible",
        description="Fusionne deux cartes Yu-Gi-Oh! et combine leurs effets."
    )
    async def fusionimpossible(self, ctx: discord.ApplicationContext):
        """Commande principale avec bouton interactif."""
        try:
            view = FusionImpossibleView(self.bot)
            await ctx.respond("Clique sur le bouton pour fusionner deux cartes aléatoires.", view=view, ephemeral=False)
        except Exception as e:
            print(f"[ERREUR fusionimpossible] {e}")
            await ctx.respond("❌ Une erreur est survenue lors de la commande.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = FusionImpossible(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Tests"
    await bot.add_cog(cog)
