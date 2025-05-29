# ──────────────────────────────────────────────────────────────
# 📁 VOCABULAIRE
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import json
import os

# 🔍 Chemin vers le fichier JSON
VOCAB_PATH = os.path.join("data", "vocabulaire.json")

# ──────────────────────────────────────────────────────────────
# 🔧 COG : VocabulaireCommand
# ──────────────────────────────────────────────────────────────
class VocabulaireCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !vocabulaire / !voc
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="vocabulaire",
        aliases=["voc"],
        help="📘 Affiche un lexique des termes Yu-Gi-Oh! classés par catégorie."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def vocabulaire(self, ctx: commands.Context):
        try:
            with open(VOCAB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return await ctx.send(f"❌ Erreur lors du chargement du vocabulaire : {e}")

        for categorie, termes in data.items():
            # Trie les termes alphabétiquement
            termes_tries = dict(sorted(termes.items()))

            embed = discord.Embed(
                title=f"📚 Vocabulaire — {categorie}",
                color=discord.Color.teal()
            )

            for mot, definition in termes_tries.items():
                embed.add_field(name=f"🔹 {mot}", value=definition, inline=False)

            await ctx.send(embed=embed)

    def cog_load(self):
        self.vocabulaire.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(VocabulaireCommand(bot))
    print("✅ Cog chargé : VocabulaireCommand (catégorie = VAACT)")
