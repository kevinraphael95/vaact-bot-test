# ──────────────────────────────────────────────────────────────
# 📁 SAY
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands

# ──────────────────────────────────────────────────────────────
# 🔧 COG : SayCommand
# ──────────────────────────────────────────────────────────────
class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # 🔌 Stockage de l’instance du bot

    # ──────────────────────────────────────────────────────────
    # 💬 COMMANDE : !say <message>
    # ──────────────────────────────────────────────────────────
    @commands.command(
        help="Fait répéter un message par le bot et supprime le message d'origine."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam : 3 secondes
    async def say(self, ctx: commands.Context, *, message: str):
        # 🧽 Tente de supprimer le message original
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer le message.")
            return
        except discord.HTTPException:
            await ctx.send("⚠️ Une erreur est survenue lors de la suppression du message.")
            return

        # 📢 Le bot répète le message
        await ctx.send(message)

    # 🏷️ Catégorisation de la commande pour le système de help personnalisé
    def cog_load(self):
        self.say.category = "Général"  # ✅ Attribue la catégorie visible dans !help

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(SayCommand(bot))
    print("✅ Cog chargé : SayCommand (catégorie = Général)")
