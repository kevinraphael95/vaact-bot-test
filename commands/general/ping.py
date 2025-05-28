# =======================
# 📦 IMPORTS
# =======================
import discord
from discord.ext import commands

# =======================
# 🏓 Cog : Ping
# =======================
class Ping(commands.Cog):
    """Affiche la latence actuelle du bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="ping",
        aliases=["test"],
        help="Affiche la latence du bot.",
        description="Retourne le ping actuel du bot Discord en millisecondes.",
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        latence = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"📶 Latence actuelle : `{latence} ms`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    def cog_load(self):
        self.ping.category = "Général"

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    cog = Ping(bot)

    # Ajout de la catégorie manuellement
    for command in cog.get_commands():
        command.category = "Général"

    await bot.add_cog(cog)
