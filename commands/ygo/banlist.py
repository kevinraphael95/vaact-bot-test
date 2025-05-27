import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup

class Banlist(commands.Cog, name="Banlist"):
    """Affiche les cartes bannies, limitées ou semi-limitées en TCG depuis le site officiel."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="banlist",
        aliases=["bl"],
        help="Affiche la banlist TCG",
        description="Utilisation : !banlist ban / limité / semi-limité ou b / l / sl"
    )
    async def banlist(self, ctx, statut: str = "ban"):
        statut_map = {
            "ban": ("Interdite", "Interdites", discord.Color.red()),
            "b": ("Interdite", "Interdites", discord.Color.red()),
            "limité": ("Limitée", "Limitées", discord.Color.orange()),
            "l": ("Limitée", "Limitées", discord.Color.orange()),
            "semi-limité": ("Semi-Limitée", "Semi-Limitées", discord.Color.gold()),
            "sl": ("Semi-Limitée", "Semi-Limitées", discord.Color.gold()),
        }

        statut = statut.lower()
        if statut not in statut_map:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité` ou `b`, `l`, `sl`.")
            return

        statut_singulier, statut_pluriel, couleur = statut_map[statut]

        url = "https://www.db.yugioh-card.com/yugiohdb/forbidden_limited.action"
        await ctx.send(f"🔄 Récupération des cartes **{statut_pluriel}** depuis le site officiel...")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis le site officiel.")
                    return
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        cartes = set()  # éviter les doublons

        for row in soup.select("div.fl-card-list > div.t_row"):
            label = row.select_one("div.label_box")
            name = row.select_one("dt.card_name")
            if label and name and statut_singulier in label.text:
                cartes.add(name.text.strip())

        if not cartes:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{statut_pluriel}**.")
            return

        # Envoi par morceaux
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

    @commands.command(name="pingban", help="Commande de test pour vérifier le chargement du cog banlist.")
    async def pingban(self, ctx):
        await ctx.send("✅ Banlist cog chargé correctement.")

async def setup(bot):
    await bot.add_cog(Banlist(bot))
