# =======================
# 📦 IMPORTS
# =======================
import discord  # Pour créer les embeds
from discord.ext import commands  # Pour les commandes Discord
import aiohttp  # Pour les requêtes HTTP asynchrones
from bs4 import BeautifulSoup  # Pour parser le HTML de la banlist

# =======================
# 🧠 CLASSE Banlist
# =======================
class Banlist(commands.Cog):
    """Cog contenant les commandes liées à la banlist officielle TCG."""

    def __init__(self, bot: commands.Bot):
        """
        Constructeur du cog.
        :param bot: instance du bot Discord
        """
        self.bot = bot

    # =======================
    # 🚫 COMMANDE banlist
    # =======================
    @commands.command(
        name="banlist",
        aliases=["bl"],
        help="Affiche la banlist TCG.",
        description="Utilisation : !banlist ban | limité | semi-limité ou b | l | sl"
    )
    async def banlist(self, ctx: commands.Context, statut: str = "ban"):
        """
        Commande !banlist [statut]
        Permet d'afficher les cartes bannies / limitées / semi-limitées
        depuis le site officiel de Yu-Gi-Oh! (TCG).
        """

        # 🗺️ Correspondance entre les termes d'entrée et les statuts officiels
        statut_map = {
            "ban": ("Interdite", "Interdites", discord.Color.red()),
            "b": ("Interdite", "Interdites", discord.Color.red()),
            "limité": ("Limitée", "Limitées", discord.Color.orange()),
            "l": ("Limitée", "Limitées", discord.Color.orange()),
            "semi-limité": ("Semi-Limitée", "Semi-Limitées", discord.Color.gold()),
            "sl": ("Semi-Limitée", "Semi-Limitées", discord.Color.gold()),
        }

        # 🔎 Nettoyage de l'entrée utilisateur
        statut = statut.lower()
        if statut not in statut_map:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité` ou `b`, `l`, `sl`.")
            return

        statut_singulier, statut_pluriel, couleur = statut_map[statut]

        # 🌐 URL de la banlist TCG officielle
        url = "https://www.db.yugioh-card.com/yugiohdb/forbidden_limited.action"
        await ctx.send(f"🔄 Récupération des cartes **{statut_pluriel}** depuis le site officiel...")

        # 🔍 Récupération et parsing HTML
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis le site officiel.")
                    return
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        cartes = set()  # 📛 On utilise un set pour éviter les doublons

        # 🧹 Recherche dans les blocs de cartes
        for row in soup.select("div.fl-card-list > div.t_row"):
            label = row.select_one("div.label_box")
            name = row.select_one("dt.card_name")
            if label and name and statut_singulier in label.text:
                cartes.add(name.text.strip())

        # 🛑 Si aucune carte trouvée
        if not cartes:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{statut_pluriel}**.")
            return

        # ✂️ Envoi des résultats par blocs de 30 cartes max
        chunk_size = 30
        cartes = sorted(cartes)
        for i in range(0, len(cartes), chunk_size):
            chunk = cartes[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {statut_pluriel} (TCG)",
                description="\n".join(chunk),
                color=couleur
            )
            await ctx.send(embed=embed)

    # =======================
    # 🧪 COMMANDE pingban
    # =======================
    @commands.command(name="pingban", help="Commande de test pour vérifier le chargement du cog banlist.")
    async def pingban(self, ctx: commands.Context):
        await ctx.send("✅ Banlist cog chargé correctement.")

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    Ajoute aussi la catégorie "YGO" pour l'affichage dans !help.
    """
    cog = Banlist(bot)

    # 🗂️ Ajout manuel de la catégorie pour chaque commande du cog
    for command in cog.get_commands():
        command.category = "YGO"

    await bot.add_cog(cog)
