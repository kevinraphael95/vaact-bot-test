# ────────────────────────────────────────────────────────────────────────────────
# 📌 fusionimpossible.py — Version avec fusion réelle des effets des cartes
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import requests
import random

class FusionImpossible(commands.Cog):
    """Commande !fusionimpossible — Fusionne deux vraies cartes Yu-Gi-Oh!"""

    def __init__(self, bot):
        self.bot = bot

    def generer_nom(self, nom1, nom2):
        """Fusionne deux noms de cartes."""
        nom1_part = nom1.split()[0] if " " in nom1 else nom1[:len(nom1)//2]
        nom2_part = nom2.split()[-1] if " " in nom2 else nom2[len(nom2)//2:]
        return f"{nom1_part} {nom2_part}"

    def fusionner_types(self, t1, t2):
        types = list({t1, t2} - {None})
        return " / ".join(types) if types else "Inconnu"

    def fusionner_effets(self, effet1, effet2):
        """Assemble les deux effets proprement."""
        if not effet1 and not effet2:
            return "Aucun effet."
        elif effet1 and effet2:
            return f"{effet1.strip()}\n\n{effet2.strip()}"
        return effet1 or effet2

    @commands.command(
        name="fusionimpossible",
        help="Fusionne deux cartes Yu-Gi-Oh! et combine leurs effets.",
        description="Fusionne nom, type et effets de deux cartes Yu-Gi-Oh! aléatoires."
    )
    async def fusionimpossible(self, ctx):
        await ctx.typing()

        try:
            url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"
            carte1 = requests.get(url).json()
            carte2 = requests.get(url).json()

            nom_fusion = self.generer_nom(carte1["name"], carte2["name"])
            type_fusion = self.fusionner_types(carte1.get("type"), carte2.get("type"))
            effet_fusion = self.fusionner_effets(carte1.get("desc"), carte2.get("desc"))

            embed = discord.Embed(
                title=f"🧪 Fusion Impossible : {nom_fusion}",
                description=f"**Type :** {type_fusion}\n\n**Effet combiné :**\n{effet_fusion}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=carte1.get("card_images", [{}])[0].get("image_url", ""))
            embed.set_image(url=carte2.get("card_images", [{}])[0].get("image_url", ""))
            embed.set_footer(text=f"Fusion de « {carte1['name']} » + « {carte2['name']} »")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR fusionimpossible] {e}")
            await ctx.send("❌ Une erreur est survenue lors de la fusion des cartes.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = FusionImpossible(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Yu-Gi-Oh"
    await bot
.add_cog(cog)
