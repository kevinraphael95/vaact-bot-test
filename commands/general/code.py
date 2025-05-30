# ────────────────────────────────────────────────────────────────────────────────
# 📁 code.py
# ────────────────────────────────────────────────────────────────────────────────
# Description : Commande !code — Affiche le lien vers le dépôt GitHub du bot
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                  # 🧱 Pour les embeds
from discord.ext import commands                # ⚙️ Pour la création de commandes

# ────────────────────────────────────────────────────────────────────────────────
# 🔗 COG : Code
# ────────────────────────────────────────────────────────────────────────────────
class Code(commands.Cog):
    """Affiche le lien du code source du bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Référence au bot

    # ────────────────────────────────────────────────────────────────────────────
    # 💻 COMMANDE : !code
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="code",
        help="Affiche le lien vers le dépôt GitHub du bot.",
        description="Retourne le lien public du code source du bot Discord."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam 3s
    async def code(self, ctx: commands.Context):
        # 🔗 Création de l'embed
        embed = discord.Embed(
            title="💻 Code source",
            description="[Clique ici pour voir le dépôt GitHub](https://github.com/kevinraphael95/ygotest)",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Yu Gi Oooooh !")  # 🎴 Footer fun

        # 📤 Envoi
        await ctx.send(embed=embed)

    # 🏷️ Définition de la catégorie pour !help
    def cog_load(self):
        self.code.category = "📁 Général"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    Enregistre ce cog dans le bot principal et assigne une catégorie personnalisée.
    """
    cog = Code(bot)

    # 🗂️ Attribution manuelle de la catégorie pour toutes les commandes du cog
    for command in cog.get_commands():
        command.category = "📁 Général"

    await bot.add_cog(cog)
