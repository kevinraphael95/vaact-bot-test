import discord
from discord.ext import commands
import aiohttp

class Banlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="banlist", aliases = ["bl"])
    async def banlist(self, ctx, statut: str = "ban"):
        """
        Affiche les cartes bannies, limitées ou semi-limitées en TCG.
        Utilisation : !banlist ban / limité / semi-limité ou b / l / sl
        """

        # Mapping des options françaises vers les statuts TCG de l’API
        mapping = {
            "ban": "forbidden",
            "b": "forbidden",
            "limité": "limited",
            "l": "limited",
            "semi-limité": "semi-limited",
            "sl": "semi-limited"
        }

        # Normalisation
        statut = statut.lower()
        if statut not in mapping:
            await ctx.send("❌ Statut invalide. Utilisez `ban`, `limité`, `semi-limité`, ou leurs raccourcis (`b`, `l`, `sl`).")
            return

        api_status = mapping[statut]

        await ctx.send(f"🔄 Récupération des cartes **{statut}**...")

        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données.")
                    return
                data = await resp.json()

        # Filtrage des cartes selon le statut demandé
        cartes = [
            carte["name"] for carte in data["data"]
            if "banlist_info" in carte and carte["banlist_info"].get("ban_tcg", "") == api_status
        ]

        if not cartes:
            await ctx.send("❌ Aucune carte trouvée avec ce statut.")
            return

        # Envoi des cartes en plusieurs embeds si nécessaire
        chunk_size = 30
        for i in range(0, len(cartes), chunk_size):
            chunk = cartes[i:i+chunk_size]
            embed = discord.Embed(
                title=f"📋 Cartes {statut.capitalize()} (TCG)",
                description="\n".join(chunk),
                color=discord.Color.red() if api_status == "forbidden" else (
                    discord.Color.orange() if api_status == "limited" else discord.Color.gold()
                )
            )
            await ctx.send(embed=embed)

# Ajout à ton bot
async def setup(bot):
    await bot.add_cog(Banlist(bot))
