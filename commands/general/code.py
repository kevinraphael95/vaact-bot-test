# ────────────────────────────────────────────────────────────────────────────────
# 💻 COMMANDE — code.py
# Objectif : Affiche le lien vers le dépôt GitHub public du bot
# Catégorie : 📂 Général
# Accès : Public (pas de restriction de rôle ou permissions)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # 📚 Bibliothèque Discord — gestion des embeds et messages
from discord.ext import commands              # ⚙️ Système de commandes basé sur les Cogs (architecture modulaire)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Définition du Cog principal — class Code
# Sert à regrouper la commande !code dans un module réutilisable
# ────────────────────────────────────────────────────────────────────────────────
class Code(commands.Cog):
    """
    💻 Commande !code — Fournit un lien vers le code source du bot hébergé sur GitHub.
    Très utile pour les curieux, les contributeurs ou pour la transparence du projet.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !code
    # Utilisée pour envoyer un embed contenant le lien GitHub du bot
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="code",                              # 🏷️ Nom exact utilisé par l'utilisateur : !code
        help="Affiche le lien vers le dépôt GitHub du bot.",  # 🆘 Affiché dans !help
        description="Retourne un embed avec le lien public du dépôt GitHub (code source du bot)."  # 📚 Pour certains systèmes de help enrichis
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Anti-spam : 1 utilisation toutes les 3 secondes par utilisateur
    async def code(self, ctx: commands.Context):
        """
        🔗 Envoie un message embed contenant le lien vers le code source.
        Utilisation standard : !code
        """

        try:
            # ────────────────────────────────────────────────────────────────────
            # 🌐 Création de l'embed contenant le lien GitHub
            # ────────────────────────────────────────────────────────────────────
            embed = discord.Embed(
                title="💻 Code source du bot",
                description="[📂 Voir le dépôt GitHub](https://github.com/kevinraphael95/ygotest)",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="✨ Open-source, baby ! | Projet Yu Gi Oooooh !")  # 🖋️ Pied de page personnalisé

            await ctx.send(embed=embed)

        except Exception as e:
            # 🚨 Gestion d’erreur
            print("[ERREUR - COMMANDE !code]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l’envoi du lien vers le code source.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# Obligatoire pour tous les fichiers de commandes à base de Cogs
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup automatique du Cog "Code".
    Enregistre le Cog auprès du bot et définit une catégorie pour !help.
    """
    cog = Code(bot)  # 🧱 Instanciation du cog avec la référence au bot

    for command in cog.get_commands():
        # 🏷️ Attribution personnalisée pour !help (appelé lors du chargement du cog)
        if not hasattr(command, "category"):
            command.category = "Général"  # 🗂️ Catégorie affichée dans !help

    await bot.add_cog(cog)  # ✅ Ajout du cog au bot
