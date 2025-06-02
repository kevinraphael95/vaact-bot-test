# ──────────────────────────────────────────────────────────────
# 📁 code.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !code
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands

# ──────────────────────────────────────────────────────────────
# 🔧 COG : CodeCommand
# ──────────────────────────────────────────────────────────────
class CodeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !code
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="code",
        help="💻 Affiche le lien vers le dépôt GitHub du bot."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam
    async def code(self, ctx: commands.Context):
        try:
            embed = discord.Embed(
                title="💻 Code source du bot",
                description="[📂 Voir le dépôt GitHub](https://github.com/kevinraphael95/ygotest)",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="✨ Open-source, baby ! | Projet Yu Gi Oooooh !")
            await ctx.send(embed=embed)
        except Exception as e:
            print("[ERREUR - COMMANDE !code]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l’envoi du lien vers le code source.")

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = CodeCommand(bot)
    cog.code.category = "Général"
    await bot.add_cog(cog)
    print("✅ Cog chargé : CodeCommand (catégorie = Général)")
