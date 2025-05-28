# =======================
# 📦 IMPORTS
# =======================
import discord
from discord.ext import commands

# =======================
# 🔗 Cog : Code
# =======================
class Code(commands.Cog):
    """Affiche le lien du code source du bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="code",
        help="Affiche le lien vers le dépôt GitHub du bot.",
        description="Retourne le lien public du code source du bot Discord."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def code(self, ctx: commands.Context):
        embed = discord.Embed(
            title="💻 Code source",
            description="[Clique ici pour voir le dépôt GitHub](https://github.com/kevinraphael95/ygotest)",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Yu Gi Oooooh !")
        await ctx.send(embed=embed)

    def cog_load(self):
        self.code.category = "Général"

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    cog = Code(bot)

    # 🏷️ Attribution manuelle de la catégorie
    for command in cog.get_commands():
        command.category = "Général"

    await bot.add_cog(cog)
