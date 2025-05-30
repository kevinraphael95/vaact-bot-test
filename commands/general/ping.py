# ────────────────────────────────────────────────────────────────────────────────
# 🧱 TEMPLATE DE COMMANDE — ping.py
# Utilisation : vérifie la latence du bot avec la commande !ping
# Objectif : démonstration conforme du template général pour les commandes
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # 🎨 Embeds, interactions et couleurs Discord
from discord.ext import commands              # 🧩 Système de commandes modulaire via Cogs

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Ping
# ────────────────────────────────────────────────────────────────────────────────
class Ping(commands.Cog):
    """
    🧩 Commande !ping : vérifie si le bot est réactif en renvoyant sa latence.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal pour interagir avec Discord

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !ping
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="ping",                               # 🏷️ Nom pour invoquer la commande
        aliases=["pong", "latence"],               # 🗂️ Alias alternatifs pour la commande
        help="Affiche la latence actuelle du bot." # 🆘 Description pour !help
    )
    async def ping(self, ctx: commands.Context):
        """
        📚 Affiche la latence actuelle du bot (en millisecondes).
        Permet de tester la réactivité du bot sur le serveur Discord.
        """

        try:
            # ────────────────────────────────────────────────────────────────────
            # 💡 LOGIQUE DE LA COMMANDE ICI
            # Mesure de la latence et affichage dans le chat
            # ────────────────────────────────────────────────────────────────────
            latence = round(self.bot.latency * 1000)  # 🔢 Conversion en millisecondes
            await ctx.send(f"🏓 Pong ! Latence : {latence} ms")  # ✉️ Réponse utilisateur

        except Exception as e:
            # 🚨 Gestion d'erreur propre
            print("[ERREUR PING]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l'exécution de la commande.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup du Cog : ajoute le cog au bot et attribue une catégorie personnalisée
    """
    cog = Ping(bot)  # 🧱 Instanciation du Cog

    for command in cog.get_commands():
        # 🏷️ Attribution d’une catégorie personnalisée (affichée dans !help)
        if not hasattr(command, "category"):
            command.category = "Général"  # 🗂️ Personnalise selon la catégorie du module

    await bot.add_cog(cog)  # ⚙️ Enregistrement du Cog dans le bot
