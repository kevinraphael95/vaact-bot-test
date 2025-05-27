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

        # Mapping des statuts possibles
        mapping = {
            "ban": "Interdites",
            "b": "Interdites",
            "limité": "Limitées",
            "l": "Limitées",
            "semi-limité": "Semi-Limitées",
            "sl": "Semi-Limitées"
        }

        statut = statut.lower()
        if statut not in mapping:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité`, ou leurs raccourcis (`b`, `l`, `sl`).")
            return

        statut_fr = mapping[statut]
        url = "https://www.db.yugioh-card.com/yugiohdb/forbidden_limited.action"

        await ctx.send(f"🔄 Récupération des cartes **{statut_fr}** depuis le site officiel...")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis le site officiel.")
                    return
                html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Extraction des cartes selon le statut
        sections = soup.find_all("section", class_="forbidden")
        cartes = []

        for section in sections:
            header = section.find("h3")
            if header and statut_fr.lower() in header.text.lower():
                card_elements = section.find_all("span", class_="card_name")
                cartes = [card.text.strip() for card in card_elements]
                break

        if not cartes:
            await ctx.send(f"❌ Aucune carte trouvée avec le statut **{statut_fr}**.")
            return

        # Envoi des cartes par blocs (max 30 par embed)
        chunk_size = 30
        for i in range(0, len(cartes), chunk_size):
            chunk = cartes[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {statut_fr} (TCG)",
                description="\n".join(chunk),
                color=discord.Color.red() if statut_fr == "Interdites" else (
                    discord.Color.orange() if statut_fr == "Limitées" else discord.Color.gold()
                )
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Banlist(bot))
