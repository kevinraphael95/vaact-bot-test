# ────────────────────────────────────────────────────────────────────────────────
# 🧱 TEMPLATE DE COMMANDE — ping.py
# Utilisation : commande pour vérifier la latence du bot
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # Gestion des embeds et interactions Discord
from discord.ext import commands              # Système de commandes basé sur les Cogs

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Ping
# ────────────────────────────────────────────────────────────────────────────────
class Ping(commands.Cog):
    """
    🧩 Commande !ping : affiche la latence actuelle du bot.
    Permet de tester la réactivité du bot via un joli embed.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !ping / !test
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="ping",                              # 🏷️ Nom utilisé pour invoquer la commande
        aliases=["test"],                         # 🗂️ Aliases possibles
        help="Affiche la latence du bot."         # 🆘 Pour le help()
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Cooldown utilisateur : 3s
    async def ping(self, ctx: commands.Context):
        """
        📚 Affiche la latence actuelle du bot Discord en millisecondes.
        Utile pour tester si le bot répond rapidement.
        """

        try:
            # ────────────────────────────────────────────────────────────────────
            # 💡 LOGIQUE DE LA COMMANDE
            # Calcul de la latence actuelle
            # ────────────────────────────────────────────────────────────────────
            latence = round(self.bot.latency * 1000)  # 📶 Latence en ms

            embed = discord.Embed(
                title="🏓 Pong !",
                description=f"📶 Latence actuelle : `{latence} ms`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            # 🚨 Gestion des erreurs
            print("[ERREUR PING]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l'exécution de la commande.")

    # 🏷️ Attribution d’une catégorie personnalisée (au chargement du cog)
    def cog_load(self):
        self.ping.category = "📂 Général"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# À utiliser pour ajouter le cog à votre bot et définir sa catégorie
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup du Cog Ping.
    Ajoute la commande au bot et définit une catégorie personnalisée.
    """
    cog = Ping(bot)  # 🧱 Instanciation du Cog

    for command in cog.get_commands():
        # 🎯 Attribution d’une catégorie personnalisée si absente
        if not hasattr(command, "category"):
            command.category = "Général"

    await bot.add_cog(cog)
