# ────────────────────────────────────────────────────────────────────────────────
# 💻 code.py — Commande !code
# Affiche le lien vers le dépôt GitHub du bot
# Catégorie : 📂 Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # Gestion des embeds pour Discord
from discord.ext import commands              # Système de commandes (Cogs)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Code
# ────────────────────────────────────────────────────────────────────────────────
class Code(commands.Cog):
    """
    💻 Commande !code — Fournit le lien vers le code source du bot.
    Permet aux utilisateurs d’accéder directement au dépôt GitHub.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !code
    # Fournit un lien vers le dépôt GitHub du projet
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="code",                              # 🏷️ Nom de la commande
        help="Affiche le lien vers le dépôt GitHub du bot.",  # 🆘 Description help()
        description="Retourne le lien public du code source du bot Discord."  # 📚 Pour le help riche (si supporté)
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam : 1 usage toutes les 3 secondes par utilisateur
    async def code(self, ctx: commands.Context):
        """
        🔗 Envoie un embed contenant le lien vers le dépôt GitHub.
        Utilisation : !code
        """

        try:
            # ────────────────────────────────────────────────────────────────────
            # 📤 Création de l'embed contenant le lien GitHub
            # ────────────────────────────────────────────────────────────────────
            embed = discord.Embed(
                title="💻 Code source",
                description="[Clique ici pour voir le dépôt GitHub](https://github.com/kevinraphael95/ygotest)",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="Yu Gi Oooooh !")  # 🎴 Footer personnalisé

            # 📩 Envoi de l'embed dans le canal
            await ctx.send(embed=embed)

        except Exception as e:
            # 🚨 Gestion d’erreur
            print("[ERREUR CODE]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l’envoi du lien.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# Ajoute ce cog au bot et assigne une catégorie personnalisée
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup du Cog "Code".
    Enregistre le cog dans le bot principal et attribue une catégorie.
    """
    cog = Code(bot)  # 🧱 Instanciation du cog

    for command in cog.get_commands():
        # 🗂️ Catégorie personnalisée visible via !help
        command.category = "Général"

    await bot.add_cog(cog)
