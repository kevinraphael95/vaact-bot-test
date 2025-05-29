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
    # 🔹 COMMANDE : !vocabulaire / !voc [mot_clé...]
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="vocabulaire",
        aliases=["voc"],
        help="📘 Affiche un lexique des termes Yu-Gi-Oh!, ou recherche un terme."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def vocabulaire(self, ctx: commands.Context, *mots_cles):
        try:
            with open(VOCAB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return await ctx.send(f"❌ Erreur lors du chargement du vocabulaire : {e}")

        mots_cles = [m.lower() for m in mots_cles]

        if mots_cles:
            resultats = {}
            for categorie, termes in data.items():
                for mot, definition in termes.items():
                    texte_complet = f"{mot} {definition}".lower()
                    if all(motcle in texte_complet for motcle in mots_cles):
                        if categorie not in resultats:
                            resultats[categorie] = {}
                        resultats[categorie][mot] = definition

            if not resultats:
                return await ctx.send(f"🔍 Aucun terme trouvé pour : `{' '.join(mots_cles)}`")

            for categorie, termes in resultats.items():
                embed = discord.Embed(
                    title=f"📚 Résultat — {categorie}",
                    color=discord.Color.green()
                )
                for mot, definition in sorted(termes.items()):
                    embed.add_field(name=f"🔹 {mot}", value=definition, inline=False)
                await ctx.send(embed=embed)

        else:
            # Affichage complet comme avant
            for categorie, termes in data.items():
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
