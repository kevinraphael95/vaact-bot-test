import discord
from discord.ext import commands
import aiohttp

class Banlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="banlist", aliases=["bl"])
    async def banlist(self, ctx, statut: str = "ban"):
        """
        Affiche les cartes bannies, limitées ou semi-limitées selon le statut.
        Utilisation : !banlist ban / limité / semi-limité ou b / l / sl
        """

        # Mapping user input ➜ API value
        mapping = {
            "ban": "Banned",
            "b": "Banned",
            "limité": "Limited",
            "l": "Limited",
            "semi-limité": "Semi-Limited",
            "sl": "Semi-Limited"
        }

        statut = statut.lower()
        if statut not in mapping:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité`, ou leurs raccourcis (`b`, `l`, `sl`).")
            return

        api_status = mapping[statut]
        url = "https://db.ygoprodeck.com/api/v7/banlist"

        await ctx.send(f"🔄 Récupération des cartes **{statut}**...")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis la banlist officielle.")
                    return
                data = await resp.json()

        # Filtrage des cartes selon leur statut
        cartes = [card["card_name"] for card in data["data"] if card["ban_tcg"] == api_status]

        if not cartes:
            await ctx.send("❌ Aucune carte trouvée avec ce statut.")
            return

        # Envoi en blocs (30 cartes max par embed)
        chunk_size = 30
        for i in range(0, len(cartes), chunk_size):
            chunk = cartes[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {api_status} (TCG)",
                description="\n".join(chunk),
                color=discord.Color.red() if api_status == "Banned" else (
                    discord.Color.orange() if api_status == "Limited" else discord.Color.gold()
                )
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Banlist(bot))
