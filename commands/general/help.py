# =============================================================
# 📁 help.py — Commande !help personnalisée
# Ce fichier fournit une commande !help avancée pour afficher
# soit la liste des commandes par catégorie, soit l'aide d'une
# commande spécifique.
# =============================================================

import discord
from discord.ext import commands

# =============================================================
# 📚 Cog : Help
# =============================================================
class Help(commands.Cog):
    """Affiche la liste des commandes disponibles ou l'aide d'une commande précise."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["aide", "h"],
        help="Affiche la liste des commandes ou les infos sur une commande spécifique.",
        description="Utilisation : !help [commande]\nSans argument : liste toutes les commandes.\nAvec une commande : affiche les détails de cette commande."
    )
    async def help_func(self, ctx, commande: str = None):
        prefix = "!"  # 🎯 Tu peux remplacer ce prefix par un système dynamique (selon serveur par exemple)

        # ──────────────────────────────────────────────────────
        # 🗂️ Affichage général : liste de toutes les commandes
        # ──────────────────────────────────────────────────────
        if commande is None:
            categories = {}

            for cmd in self.bot.commands:
                if cmd.hidden:
                    continue  # 🚫 Ignore les commandes masquées

                cat = getattr(cmd, "category", "Autres")  # 📦 Catégorie personnalisée ou fallback
                categories.setdefault(cat, []).append(cmd)

            embed = discord.Embed(
                title="📜 Commandes disponibles",
                description="Voici les commandes regroupées par catégorie :",
                color=discord.Color.green()
            )

            # Ajoute chaque catégorie avec ses commandes
            for cat, cmds in sorted(categories.items()):
                cmds.sort(key=lambda c: c.name)
                lignes = [f"`{prefix}{c.name}` : {c.help or 'Pas de description.'}" for c in cmds]
                embed.add_field(name=f"📂 {cat}", value="\n".join(lignes), inline=False)

            embed.set_footer(text=f"💡 Utilise {prefix}help <commande> pour plus d'infos sur une commande.")
            await ctx.send(embed=embed)

        # ──────────────────────────────────────────────────────
        # 🔍 Aide spécifique à une commande donnée
        # ──────────────────────────────────────────────────────
        else:
            cmd = self.bot.get_command(commande)
            if cmd is None:
                await ctx.send(f"❌ La commande `{commande}` n'existe pas.")
                return

            embed = discord.Embed(
                title=f"ℹ️ Aide : `{prefix}{cmd.name}`",
                color=discord.Color.blue()
            )
            embed.add_field(name="📝 Description", value=cmd.help or "Pas de description.", inline=False)

            # Affiche les alias, s'il y en a
            if cmd.aliases:
                embed.add_field(name="🔁 Alias", value=", ".join(f"`{a}`" for a in cmd.aliases), inline=False)

            # Notes d'utilisation
            embed.set_footer(text="📌 Les paramètres entre < > sont obligatoires, ceux entre [ ] sont optionnels.")
            await ctx.send(embed=embed)

    def cog_load(self):
        # 🏷️ Définit la catégorie visible dans le système d’aide personnalisé
        self.help_func.category = "Général"

# =============================================================
# ⚙️ Setup du Cog
# =============================================================
async def setup(bot):
    cog = Help(bot)

    # Associe une catégorie par défaut si non définie
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"

    await bot.add_cog(cog)
