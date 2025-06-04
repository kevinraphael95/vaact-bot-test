# ────────────────────────────────────────────────────────────────────────────────
# 📌 carte.py — Commande interactive !carte
# Objectif : Rechercher et afficher les détails d’une carte Yu-Gi-Oh! dans plusieurs langues
# Catégorie : 🃏 Yu-Gi-Oh!
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import urllib.parse

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Carte(commands.Cog):
    """
    Commande !carte — Rechercher une carte Yu-Gi-Oh! et afficher ses informations.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="carte",
        aliases=["card"],
        help="🔍 Rechercher une carte Yu-Gi-Oh! dans plusieurs langues.",
        description="Affiche les infos d’une carte Yu-Gi-Oh! à partir de son nom (FR, EN, DE, IT, PT)."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def carte(self, ctx: commands.Context, *, nom: str):
        """Commande principale pour chercher une carte Yu-Gi-Oh!"""

        lang_codes = ["fr", "en", "de", "it", "pt"]
        nom_encode = urllib.parse.quote(nom)

        carte = None
        langue_detectee = "?"
        nom_corrige = nom

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={nom_encode}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "data" in data:
                            for card in data["data"]:
                                if nom.lower() in card.get("name", "").lower():
                                    langue_detectee = card.get("language", "?")
                                    if langue_detectee not in lang_codes:
                                        langue_detectee = "en"
                                    carte = card
                                    nom_corrige = card.get("name", nom)
                                    break
                    else:
                        # Pas de message en cas d'erreur HTTP, on ignore
                        return
        except Exception as e:
            print(f"[ERREUR commande !carte] {e}")
            # Pas de message pour éviter spam, on log seulement
            return

        if not carte:
            # Aucune carte trouvée => on ne répond pas
            return

        if nom_corrige.lower() != nom.lower():
            await ctx.send(f"🔍 Résultat trouvé pour **{nom_corrige}** ({langue_detectee.upper()})")

        embed = discord.Embed(
            title=f"{carte.get('name', 'Carte inconnue')} ({langue_detectee.upper()})",
            description=carte.get("desc", "Pas de description disponible."),
            color=discord.Color.red()
        )

        embed.add_field(name="🧪 Type", value=carte.get("type", "?"), inline=True)

        if carte.get("type", "").lower().startswith("monstre"):
            atk = carte.get("atk", "?")
            defe = carte.get("def", "?")
            level = carte.get("level", "?")
            attr = carte.get("attribute", "?")
            race = carte.get("race", "?")

            embed.add_field(name="⚔️ ATK / DEF", value=f"{atk} / {defe}", inline=True)
            embed.add_field(name="⭐ Niveau / Rang", value=str(level), inline=True)
            embed.add_field(name="🌪️ Attribut", value=attr, inline=True)
            embed.add_field(name="👹 Race", value=race, inline=True)

        embed.set_thumbnail(url=carte["card_images"][0]["image_url"])
        await ctx.send(embed=embed)

    def cog_load(self):
        self.carte.category = "🃏 Yu-Gi-Oh!"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Carte(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
