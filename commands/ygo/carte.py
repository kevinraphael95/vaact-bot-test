# ────────────────────────────────────────────────────────────────────────────────
# 📁 ygo/carte.py — Commande !carte
# Objectif : Rechercher une carte Yu-Gi-Oh! dans plusieurs langues via l'API YGOPRODeck
# Catégorie : 🃏 Yu-Gi-Oh!
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import urllib.parse

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 Fonction utilitaire pour suggestions si carte non trouvée
# ────────────────────────────────────────────────────────────────────────────────
async def chercher_suggestions(nom: str):
    """Recherche jusqu'à 5 cartes proches en multilingue si la carte exacte est introuvable."""
    suggestions = []
    langues = {"fr": "🇫🇷", "en": "🇬🇧", "de": "🇩🇪", "it": "🇮🇹", "pt": "🇵🇹"}
    nom_encode = urllib.parse.quote(nom)

    async with aiohttp.ClientSession() as session:
        for code, flag in langues.items():
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={nom_encode}&language={code}&num=5"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data:
                        for carte in data["data"]:
                            suggestions.append((carte["name"], flag))
                if len(suggestions) >= 5:
                    break
    return suggestions[:5]

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 COG : Carte
# ────────────────────────────────────────────────────────────────────────────────
class Carte(commands.Cog):
    """
    🔎 Cog contenant la commande !carte permettant de chercher une carte
    Yu-Gi-Oh! dans plusieurs langues via l'API YGOPRODeck.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !carte / !card
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="carte",
        aliases=["card"],
        help="📄 Affiche les infos d’une carte Yu-Gi-Oh! (FR, EN, DE, IT, PT)."
    )
    async def carte(self, ctx: commands.Context, *, nom: str):
        """
        🧠 Commande !carte <nom>
        Recherche une carte Yu-Gi-Oh! par son nom (exact), et affiche ses infos.
        """

        nom_encode = urllib.parse.quote(nom)
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={nom_encode}&language=fr"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("🚨 Impossible de contacter l’API.")
                        return
                    data = await resp.json()

            if "data" not in data:
                suggestions = await chercher_suggestions(nom)
                if suggestions:
                    suggestion_txt = "\n".join(f"{flag} **{name}**" for name, flag in suggestions)
                    await ctx.send(
                        f"❌ Carte introuvable en français. Voici quelques suggestions proches :\n{suggestion_txt}"
                    )
                else:
                    await ctx.send("❌ Aucune carte trouvée. Vérifie l’orthographe ou essaie un autre nom.")
                return

            carte = data["data"][0]
            embed = discord.Embed(
                title=carte.get("name", "Carte inconnue"),
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

        except Exception as e:
            print(f"[ERREUR CARTE] {e}")
            await ctx.send("💥 Une erreur est survenue lors de la recherche de la carte.")

    def cog_load(self):
        self.carte.category = "🃏 Yu-Gi-Oh!"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Carte(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
    print("✅ Cog chargé : Carte (catégorie = 🃏 Yu-Gi-Oh!)")
