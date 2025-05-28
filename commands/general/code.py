# ────────────────────────────────────────────────────────────────
# 📁 code.py — Commande !code
# Ce fichier contient une commande simple qui envoie le lien du code source du bot.
# Elle est catégorisée sous "Général" pour une meilleure organisation dans !help.
# ────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands

class Code(commands.Cog):
    """
    📦 Cog contenant la commande liée au code source du bot.
    Cette commande affiche simplement le lien GitHub du projet.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="code",
        help="Affiche le lien du code du bot sur GitHub."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🕒 1 utilisation toutes les 3 secondes par utilisateur
    async def code(self, ctx):
        """
        🔗 Envoie le lien vers le dépôt GitHub du bot.
        """
        await ctx.send("🔗 Code source du bot : https://github.com/kevinraphael95/ygotest")

# ────────────────────────────────────────────────────────────────
# 🔧 Chargement du Cog
# On définit dynamiquement la catégorie pour les systèmes de help personnalisés.
# ────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = Code(bot)

    # 🏷️ Attribution manuelle de la catégorie "Général" à toutes les commandes du Cog
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"

    await bot.add_cog(cog)
