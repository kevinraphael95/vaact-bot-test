# ────────────────────────────────────────────────────────────────────────────────
# 🧱 COMMANDE — help.py
# Objectif : Fournir un système d’aide détaillé et lisible aux utilisateurs
# Structure basée sur le modèle pédagogique ultra structuré
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import os                                      # 🌍 Accès aux variables d’environnement
import discord                                 # 🎨 Embeds et interactions riches Discord
from discord.ext import commands              # ⚙️ Gestion des commandes avec Cogs

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Help
# ────────────────────────────────────────────────────────────────────────────────
class Help(commands.Cog):
    """
    📚 Commande !help : système d’aide contextuelle
    - Sans argument : affiche toutes les commandes regroupées par catégorie
    - Avec argument  : affiche l’aide détaillée d’une commande spécifique
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !help
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="help",                              # 🏷️ Nom de la commande
        aliases=["aide", "h"],                    # 🔁 Aliases alternatifs
        help="Affiche la liste des commandes ou les infos d’une commande spécifique.",  # 🆘 Aide rapide
        description=(
            "📌 Utilisation : `!help` ou `!help <commande>`\n"
            "- Sans argument : liste complète des commandes\n"
            "- Avec un nom : détails complets de la commande"
        )
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Limite d'utilisation
    async def help_func(self, ctx: commands.Context, commande: str = None):
        """
        📚 Comportement :
        - !help         → liste regroupée des commandes
        - !help ping    → détails de la commande ping
        """

        prefix = os.getenv("COMMAND_PREFIX", "!")  # 🔄 Récupération du préfixe dynamique

        try:
            # ────────────────────────────────────────────────────────────────────
            # 🔎 CAS 1 — Affichage global des commandes
            # ────────────────────────────────────────────────────────────────────
            if commande is None:
                categories = {}

                for cmd in self.bot.commands:
                    if cmd.hidden:
                        continue  # 🚫 Ne pas afficher les commandes cachées

                    cat = getattr(cmd, "category", "Autres")  # 📂 Catégorie par défaut
                    categories.setdefault(cat, []).append(cmd)

                embed = discord.Embed(
                    title="📜 Liste des commandes disponibles",
                    description="Voici les commandes regroupées par catégorie :",
                    color=discord.Color.green()
                )

                for cat, cmds in sorted(categories.items()):
                    cmds.sort(key=lambda c: c.name)  # 🔠 Tri alphabétique
                    lignes = [
                        f"`{prefix}{c.name}` : {c.help or 'Pas de description.'}"
                        for c in cmds
                    ]
                    embed.add_field(name=f"📂 {cat}", value="\n".join(lignes), inline=False)

                embed.set_footer(text=f"💡 Utilise {prefix}help <commande> pour plus de détails.")
                await ctx.send(embed=embed)

            # ────────────────────────────────────────────────────────────────────
            # 🔎 CAS 2 — Aide sur une commande spécifique
            # ────────────────────────────────────────────────────────────────────
            else:
                cmd = self.bot.get_command(commande)

                if cmd is None:
                    await ctx.send(f"❌ La commande `{commande}` n’existe pas.")
                    return

                embed = discord.Embed(
                    title=f"ℹ️ Aide pour : `{prefix}{cmd.name}`",
                    color=discord.Color.blue()
                )

                embed.add_field(
                    name="📝 Description",
                    value=cmd.help or "Pas de description disponible.",
                    inline=False
                )

                if cmd.aliases:
                    aliases = ", ".join(f"`{a}`" for a in cmd.aliases)
                    embed.add_field(name="🔁 Alias", value=aliases, inline=False)

                embed.set_footer(text="📌 <obligatoire> — [optionnel]")
                await ctx.send(embed=embed)

        except Exception as e:
            # 🚨 Gestion d'erreur
            print("[ERREUR HELP]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l'exécution de la commande d’aide.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# Ajoute la commande au bot et assigne une catégorie
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup du Cog Help.
    Ajoute la commande au bot et définit une catégorie si absente.
    """
    cog = Help(bot)  # 🧱 Instanciation du Cog

    for command in cog.get_commands():
        # 🏷️ Attribution personnalisée pour l’aide (visible dans !help)
        if not hasattr(command, "category"):
            command.category = "Général"  # 🗂️ Regroupement par défaut

    await bot.add_cog(cog)  # ✅ Ajout final du cog
