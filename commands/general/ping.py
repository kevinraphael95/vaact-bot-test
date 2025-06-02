# ────────────────────────────────────────────────────────────────────────────────
# 📌 ping.py — Commande interactive !ping
# Objectif : Vérifie la latence du bot
# Catégorie : 🧱 Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Ping(commands.Cog):
    """
    Commande !ping — Vérifie la latence du bot
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="ping",
        aliases=["pong", "latence"],
        help="Affiche la latence actuelle du bot.",
        description="Affiche la latence actuelle du bot en millisecondes."
    )
    async def ping(self, ctx: commands.Context):
        """Commande simple pour tester la réactivité du bot."""
        try:
            latence = round(self.bot.latency * 1000)
            await ctx.send(f"🏓 Pong ! Latence : {latence} ms")
        except Exception as e:
            print("[ERREUR ping]", e)
            await ctx.send("❌ Une erreur est survenue lors de l'exécution de la commande.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Ping(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"
    await bot.add_cog(cog)
