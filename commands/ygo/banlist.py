# =======================
# 📦 IMPORTS
# =======================

import discord
from discord.ext import commands
import aiohttp

# =======================
# 🧠 CLASSE BANLIST
# =======================

class Banlist(commands.Cog):
    """Commandes liées à la banlist officielle TCG de Yu-Gi-Oh!"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🚫 COMMANDE BANLIST
    @commands.command(
        name="banlist",
        aliases=["bl"],
        help="Affiche la banlist TCG depuis l'API officielle.",
        description="Utilisation : !banlist ban | limité | semi-limité ou b | l | sl"
    )
    async def banlist(self, ctx: commands.Context, statut: str = "ban"):
        """
        Commande !banlist [statut]
        Affiche les cartes Interdites / Limitées / Semi-Limitées du format TCG.
        """

        # 🔁 Table de correspondance entre l'input utilisateur et les statuts d'API
        statut_map = {
            "ban": ("Banned", "Interdites", discord.Color.red()),
            "b": ("Banned", "Interdites", discord.Color.red()),
            "limité": ("Limited", "Limitées", discord.Color.orange()),
            "l": ("Limited", "Limitées", discord.Color.orange()),
            "semi-limité": ("Semi-Limited", "Semi-Limitées", discord.Color.gold()),
            "sl": ("Semi-Limited", "Semi-Limitées", discord.Color.gold())
        }

        # 🔎 Nettoyage de l'argument utilisateur
        statut = statut.lower()
        if statut not in statut_map:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité` ou `b`, `l`, `sl`.")
            return

        api_statut, label_statut, couleur = statut_map[statut]
        await ctx.send(f"🔄 Récupération des cartes **{label_statut}** depuis l’API officielle...")

        # 🌐 Requête vers l'API YGOPRODeck
        api_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?banlist=tcg"
        cartes_filtrées = []

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Erreur lors de la récupération des données depuis l'API.")
                    return
                data = await resp.json()

        # 🧹 Filtrage des cartes selon le statut demandé
        for card in data.get("data", []):
            ban_info = card.get("banlist_info", {})
            if ban_info.get("ban_tcg") == api_statut:
                cartes_filtrées.append(card["name"])

        # 🛑 Aucun résultat trouvé
        if not cartes_filtrées:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{label_statut}**.")
            return

        # ✂️ Envoi des cartes par blocs de 30
        chunk_size = 30
        cartes_filtrées = sorted(set(cartes_filtrées))
        for i in range(0, len(cartes_filtrées), chunk_size):
            chunk = cartes_filtrées[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {label_statut} (TCG)",
                description="\n".join(chunk),
                color=couleur
            )
            await ctx.send(embed=embed)

    # =======================
    # ✅ COMMANDE DE TEST
    # =======================
    
    @commands.command(name="pingban", help="Commande de test pour le cog banlist.")
    async def pingban(self, ctx: commands.Context):
        await ctx.send("✅ Le cog banlist est bien chargé et fonctionnel.")
# =======================
# ⚙️ SETUP DU COG
# =======================

async def setup(bot: commands.Bot):
    """Ajout du cog au bot et catégorisation des commandes."""
    cog = Banlist(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
