# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands

class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # Stocke l'instance du bot

    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        # Réponse simple
        await ctx.send("📅 Prochain tournoi : date non disponible pour l’instant.")

async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    # On catégorise la commande pour l'aide
    cog.tournoi.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiCommand (catégorie = "VAACT")")
