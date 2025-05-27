import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup

class Banlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="banlist", aliases=["bl"])
    async def banlist(self, ctx, statut: str = "ban"):
        """
        Affiche les cartes bannies, limitées ou semi-limitées en TCG.
        Utilisation : !banlist ban / limité / semi-limité ou b / l / sl
        """
        mapping = {
            "ban": "Interdite",
            "b": "Interdite",
            "limité": "Limitée",
            "l": "Limitée",
            "semi-limité": "Semi-Limitée",
            "sl": "Semi-Limitée"
        }

        statut = statut.lower()
        if statut not in mapping:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité`, ou leurs raccourcis (`b`, `l`, `sl`).")
            return

        statut_fr = mapping[statut]
        url = "https://www.db.yugioh-card.com/yugiohdb/forbidden_limited.action"

        await ctx.send(f"🔄 Récupération des cartes **{statut_fr}s** depuis le site officiel...")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis le site officiel.")
                    return
                html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')
        cartes = []

        # Parcours des listes d'interdiction
        for item in soup.select("div.fl-card-list > div.t_row"):
            label = item.select_one("div.label_box")
            name = item.select_one("dt.card_name")

            if label and name and statut_fr in label.text:
                cartes.append(name.text.strip())

        if not cartes:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{statut_fr}**.")
            return

        chunk_size = 30
        for i in range(0, len(cartes), chunk_size):
            chunk = cartes[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {statut_fr}s (TCG)",
                description="\n".join(chunk),
                color=discord.Color.red() if statut_fr == "Interdite" else (
                    discord.Color.orange() if statut_fr == "Limitée" else discord.Color.gold()
                )
            )
            await ctx.send(embed=embed)

    # Commande de test pour vérifier que le cog est bien chargé
    @commands.command(name="pingban")
    async def pingban(self, ctx):
        await ctx.send("✅ Banlist cog chargé correctement.")

async def setup(bot):
    await bot.add_cog(Banlist(bot))
