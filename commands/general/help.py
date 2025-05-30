# ────────────────────────────────────────────────────────────────────────────────
# 📁 help.py — Commande !help personnalisée
# ────────────────────────────────────────────────────────────────────────────────
# Fournit un système d’aide dynamique :
# - !help           → Liste des commandes regroupées par catégorie
# - !help <commande> → Détails sur une commande spécifique
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                  # 🧱 Pour les embeds
from discord.ext import commands                # ⚙️ Pour créer des commandes de bot

# ────────────────────────────────────────────────────────────────────────────────
# 📚 COG : Help
# ────────────────────────────────────────────────────────────────────────────────
class Help(commands.Cog):
    """Affiche la liste des commandes disponibles ou l'aide d'une commande précise."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stockage de l’instance du bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🆘 COMMANDE : !help / !aide / !h
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="help",
        aliases=["aide", "h"],
        help="Affiche la liste des commandes ou les infos sur une commande spécifique.",
        description=(
            "Utilisation : !help [commande]\n"
            "Sans argument : liste toutes les commandes disponibles.\n"
            "Avec une commande : affiche ses détails complets."
        )
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Cooldown utilisateur : 3s
    async def help_func(self, ctx: commands.Context, commande: str = None):
        prefix = "!"  # 🎯 Préfixe à personnaliser selon le serveur si besoin

        # ──────────────────────────────────────────────────────
        # 🗂️ CAS 1 : Affichage de toutes les commandes
        # ──────────────────────────────────────────────────────
        if commande is None:
            categories = {}

            for cmd in self.bot.commands:
                if cmd.hidden:
                    continue  # 🚫 Commandes cachées non listées

                cat = getattr(cmd, "category", "Autres")  # 📁 Catégorie ou fallback
                categories.setdefault(cat, []).append(cmd)

            embed = discord.Embed(
                title="📜 Commandes disponibles",
                description="Voici les commandes regroupées par catégorie :",
                color=discord.Color.green()
            )

            # 🔠 Affichage trié par catégorie
            for cat, cmds in sorted(categories.items()):
                cmds.sort(key=lambda c: c.name)
                lignes = [f"`{prefix}{c.name}` : {c.help or 'Pas de description.'}" for c in cmds]
                embed.add_field(name=f"📂 {cat}", value="\n".join(lignes), inline=False)

            embed.set_footer(text=f"💡 Astuce : utilise {prefix}help <commande> pour les détails.")
            await ctx.send(embed=embed)

        # ──────────────────────────────────────────────────────
        # 🔍 CAS 2 : Aide pour une commande précise
        # ──────────────────────────────────────────────────────
        else:
            cmd = self.bot.get_command(commande)
            if cmd is None:
                await ctx.send(f"❌ La commande `{commande}` n'existe pas.")
                return

            embed = discord.Embed(
                title=f"ℹ️ Aide sur la commande : `{prefix}{cmd.name}`",
                color=discord.Color.blue()
            )
            embed.add_field(name="📝 Description", value=cmd.help or "Pas de description disponible.", inline=False)

            # 🔁 Alias éventuels
            if cmd.aliases:
                embed.add_field(name="🔁 Alias", value=", ".join(f"`{a}`" for a in cmd.aliases), inline=False)

            embed.set_footer(text="📌 <obligatoire> — [optionnel]")
            await ctx.send(embed=embed)

    # 🏷️ Attribution personnalisée pour !help
    def cog_load(self):
        self.help_func.category = "📁 Général"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer le cog Help dans le bot principal.
    """
    cog = Help(bot)

    # 🗂️ Attribution d'une catégorie par défaut
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "📁 Général"

    await bot.add_cog(cog)
