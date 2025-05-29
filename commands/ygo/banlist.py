# ──────────────────────────────────────────────────────────────
# 📁 BANLIST
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Imports
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp

# ──────────────────────────────────────────────────────────────
# 🔧 COG : BanlistCommand
# ──────────────────────────────────────────────────────────────
class BanlistCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !banlist
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="banlist",
        aliases=["banned", "tcgban"],
        help="🔒 Affiche la banlist TCG actuelle (banni, limité, semi-limité)."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def banlist(self, ctx: commands.Context):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?banlist=tcg"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("🚨 Impossible de récupérer la banlist.")
                        return
                    data = await resp.json()

            banned = []
            limited = []
            semi_limited = []

            for card in data.get("data", []):
                name = card.get("name", "Carte inconnue")
                ban_status = card.get("banlist_info", {}).get("ban_tcg", None)
                if ban_status == "Banned":
                    banned.append(name)
                elif ban_status == "Limited":
                    limited.append(name)
                elif ban_status == "Semi-Limited":
                    semi_limited.append(name)

            def format_cards(cards):
                return "\n".join(f"• {card}" for card in cards[:20]) + ("\n... *(liste coupée)*" if len(cards) > 20 else "")

            embed = discord.Embed(
                title="🚫 Banlist TCG — Yu-Gi-Oh!",
                description="Mise à jour via YGOPRODeck API",
                color=discord.Color.red()
            )
            embed.add_field(name="❌ Banni", value=format_cards(banned) or "Aucune carte", inline=False)
            embed.add_field(name="⚠️ Limité", value=format_cards(limited) or "Aucune carte", inline=False)
            embed.add_field(name="⚖️ Semi-limité", value=format_cards(semi_limited) or "Aucune carte", inline=False)
            embed.set_footer(text="Source : https://db.ygoprodeck.com/api-guide/")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR BANLIST] {e}")
            await ctx.send("💥 Une erreur est survenue lors de la récupération de la banlist.")

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.banlist.category = "Yu-Gi-Oh!"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(BanlistCommand(bot))
    print("✅ Cog chargé : BanlistCommand (catégorie = "🃏 Yu-Gi-Oh!")")
