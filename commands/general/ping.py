# ────────────────────────────────────────────────────────────────────────────────
# 📁 ping.py — Commande !ping
# ────────────────────────────────────────────────────────────────────────────────
# Fournit une commande simple pour tester la latence du bot.
# Affiche le ping en millisecondes avec un joli embed.
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                  # 🧱 Embeds et outils Discord
from discord.ext import commands                # ⚙️ Framework des commandes

# ────────────────────────────────────────────────────────────────────────────────
# 🏓 COG : Ping
# ────────────────────────────────────────────────────────────────────────────────
class Ping(commands.Cog):
    """Affiche la latence actuelle du bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stockage de l'instance du bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔧 COMMANDE : !ping / !test
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="ping",
        aliases=["test"],
        help="Affiche la latence du bot.",
        description="Retourne le ping actuel du bot Discord en millisecondes."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam utilisateur
    async def ping(self, ctx: commands.Context):
        latence = round(self.bot.latency * 1000)  # 📶 Conversion en ms
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"📶 Latence actuelle : `{latence} ms`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # 🏷️ Catégorie pour la commande dans le système d’aide
    def cog_load(self):
        self.ping.category = "📁 Général"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    Fonction appelée automatiquement pour enregistrer ce cog dans le bot.
    """
    cog = Ping(bot)

    # 🗂️ Attribution manuelle de la catégorie
    for command in cog.get_commands():
        command.category = "📁 Général"

    await bot.add_cog(cog)
