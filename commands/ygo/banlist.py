# =======================
# 📦 IMPORTS
# =======================
import discord
from discord.ext import commands
import aiohttp  # Pour les requêtes HTTP asynchrones

# =======================
# 🧠 CLASSE Banlist
# =======================
class Banlist(commands.Cog):
    """🃏 Commandes liées à la banlist TCG (via API YGOPRODeck)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =======================
    # 🚫 COMMANDE !banlist
    # =======================
    @commands.command(
        name="banlist",
        aliases=["bl"],
        help="Affiche la banlist TCG (interdites / limitées / semi-limitées).",
        description="Utilisation : !banlist ban | limité | semi-limité ou b | l | sl"
    )
    async def banlist(self, ctx: commands.Context, statut: str = "ban"):
        """
        Commande principale !banlist
        Permet d'afficher les cartes bannies / limitées / semi-limitées depuis l'API officielle YGOPRODeck.
        """

        # 🗺️ Correspondance entre input utilisateur et statut API
        statut_map = {
            "ban":      ("Banned", "Interdites", discord.Color.red()),
            "b":        ("Banned", "Interdites", discord.Color.red()),
            "limité":   ("Limited", "Limitées", discord.Color.orange()),
            "l":        ("Limited", "Limitées", discord.Color.orange()),
            "semi-limité": ("Semi-Limited", "Semi-Limitées", discord.Color.gold()),
            "sl":       ("Semi-Limited", "Semi-Limitées", discord.Color.gold())
        }

        statut = statut.lower()
        if statut not in statut_map:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité` ou `b`, `l`, `sl`.")
            return

        api_statut, label_statut, couleur = statut_map[statut]

        await ctx.send(f"🔄 Récupération des cartes **{label_statut}** depuis l’API officielle...")

        # 🌐 URL de l’API officielle
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?banlist=tcg"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erreur lors de la récupération des données API.")
                        return
                    data = await resp.json()
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la connexion à l’API : `{e}`")
            return

        # 🗃️ Filtrage des cartes selon le statut
        cartes_filtrées = []
        for card in data.get("data", []):
            if "banlist_info" in card and card["banlist_info"].get("ban_tcg") == api_statut:
                cartes_filtrées.append(card["name"])

        # 📭 Aucun résultat ?
        if not cartes_filtrées:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{label_statut}**.")
            return

        # ✂️ Envoi par blocs de 30 cartes max
        chunk_size = 30
        cartes_filtrées = sorted(cartes_filtrées)
        for i in range(0, len(cartes_filtrées), chunk_size):
            chunk = cartes_filtrées[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {label_statut} (TCG)",
                description="\n".join(chunk),
                color=couleur
            )
            await ctx.send(embed=embed)

    # =======================
    # ✅ COMMANDE pingban
    # =======================
    @commands.command(name="pingban", help="Vérifie si le cog Banlist est bien chargé.")
    async def pingban(self, ctx: commands.Context):
        await ctx.send("✅ Le cog `Banlist` est prêt à l’emploi.")

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    cog = Banlist(bot)

    # 🗂️ Ajout manuel de la catégorie "Yu-Gi-Oh!"
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
