# ────────────────────────────────────────────────────────────────────────────────
# 🧱 TEMPLATE DE COMMANDE — help.py
# Utilisation : commande d’aide personnalisée affichant la liste des commandes
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # Gestion des embeds et interactions Discord
from discord.ext import commands              # Système de commandes basé sur les Cogs

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Classe principale du Cog — Help
# ────────────────────────────────────────────────────────────────────────────────
class Help(commands.Cog):
    """
    🧩 Commande !help : affiche la liste des commandes disponibles ou l’aide d’une commande spécifique.
    Ex :
    - !help            → Liste de toutes les commandes
    - !help ping       → Aide détaillée de la commande ping
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔗 Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎯 Commande principale — !help / !aide / !h
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="help",                              # 🏷️ Nom utilisé pour invoquer la commande
        aliases=["aide", "h"],                    # 🗂️ Aliases possibles
        help="Affiche la liste des commandes ou les infos sur une commande spécifique.",  # 🆘 Aide rapide
        description=(
            "Utilisation : !help [commande]\n"
            "Sans argument : liste toutes les commandes disponibles.\n"
            "Avec une commande : affiche ses détails complets."
        )
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Cooldown utilisateur : 3s
    async def help_func(self, ctx: commands.Context, commande: str = None):
        """
        📚 Affiche soit :
        - la liste regroupée des commandes (si aucune commande précisée),
        - soit les infos détaillées sur une commande.
        """

        prefix = "!"  # 🎯 À personnaliser si nécessaire

        try:
            if commande is None:
                # 🗂️ Regrouper les commandes par catégories
                categories = {}

                for cmd in self.bot.commands:
                    if cmd.hidden:
                        continue  # 🚫 Ne pas inclure les commandes cachées

                    cat = getattr(cmd, "category", "Autres")  # 📁 Catégorie personnalisée ou par défaut
                    categories.setdefault(cat, []).append(cmd)

                embed = discord.Embed(
                    title="📜 Commandes disponibles",
                    description="Voici les commandes regroupées par catégorie :",
                    color=discord.Color.green()
                )

                for cat, cmds in sorted(categories.items()):
                    cmds.sort(key=lambda c: c.name)
                    lignes = [f"`{prefix}{c.name}` : {c.help or 'Pas de description.'}" for c in cmds]
                    embed.add_field(name=f"📂 {cat}", value="\n".join(lignes), inline=False)

                embed.set_footer(text=f"💡 Astuce : utilise {prefix}help <commande> pour les détails.")
                await ctx.send(embed=embed)

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

                # 🔁 Ajout des alias si disponibles
                if cmd.aliases:
                    embed.add_field(name="🔁 Alias", value=", ".join(f"`{a}`" for a in cmd.aliases), inline=False)

                embed.set_footer(text="📌 <obligatoire> — [optionnel]")
                await ctx.send(embed=embed)

        except Exception as e:
            print("[ERREUR HELP]", e)
            await ctx.send("🚨 Une erreur est survenue lors de l'exécution de la commande d’aide.")

    # 🏷️ Attribution personnalisée pour !help (appelé lors du chargement du cog)
    def cog_load(self):
        self.help_func.category = "📂 Général"  # 🏷️ Catégorie par défaut ou personnalisée

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# À utiliser pour ajouter le cog à votre bot et définir sa catégorie
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔧 Setup du Cog Help.
    Ajoute la commande au bot et définit une catégorie personnalisée.
    """
    cog = Help(bot)  # 🧱 Instanciation du Cog

    for command in cog.get_commands():
        # 🎯 Attribution d’une catégorie personnalisée si absente
        if not hasattr(command, "category"):
            command.category = "📂 Général"  # 🏷️ Modifier selon votre projet

    await bot.add_cog(cog)
