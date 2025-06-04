# ────────────────────────────────────────────────────────────────────────────────
# 📌 help.py — Commande interactive !help
# Objectif : Fournir un système d’aide détaillé et lisible aux utilisateurs
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import os
import discord
from discord.ext import commands

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal — Help
# ────────────────────────────────────────────────────────────────────────────────
class Help(commands.Cog):
    """
    📚 Commande !help : système d’aide contextuelle
    - Sans argument : affiche toutes les commandes regroupées par catégorie
    - Avec argument  : affiche l’aide détaillée d’une commande spécifique
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["aide", "h"],
        help="Affiche la liste des commandes ou les infos d’une commande spécifique.",
        description=(
            "📌 Utilisation : `!help` ou `!help <commande>`\n"
            "- Sans argument : liste complète des commandes\n"
            "- Avec un nom : détails complets de la commande"
        )
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def help_func(self, ctx: commands.Context, commande: str = None):
        prefix = os.getenv("COMMAND_PREFIX", "!")

        try:
            if commande is None:
                categories = {}

                for cmd in self.bot.commands:
                    if cmd.hidden:
                        continue

                    cat = getattr(cmd, "category", "Autres")
                    categories.setdefault(cat, []).append(cmd)

                embed = discord.Embed(
                    title="📜 Liste des commandes disponibles",
                    description="Voici les commandes regroupées par catégorie :",
                    color=discord.Color.green()
                )

                for cat, cmds in sorted(categories.items()):
                    cmds.sort(key=lambda c: c.name)
                    lignes = [
                        f"`{prefix}{c.name}` : {c.help or 'Pas de description.'}"
                        for c in cmds
                    ]
                    embed.add_field(name=f"📂 {cat}", value="\n".join(lignes), inline=False)

                embed.set_footer(text=f"💡 Utilise {prefix}help <commande> pour plus de détails.")
                await ctx.send(embed=embed)

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
            print("[ERREUR HELP]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l'exécution de la commande d’aide.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Help(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"
    await bot.add_cog(cog)
