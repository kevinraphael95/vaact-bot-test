# ──────────────────────────────────────────────────────────────
# 📁 tournoi
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi et l'état des decks (placeholder)."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Anti-spam
    async def tournoi(self, ctx: commands.Context):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SUPABASE_URL}/rest/v1/tournoi?select=date&order=date.desc&limit=1",
                headers=headers
            ) as response:
                data = await response.json()

        if not data:
            await ctx.send("❌ Aucune date de tournoi trouvée.")
            return

        raw_date = data[0]["date"]
        try:
            parsed_date = datetime.fromisoformat(raw_date)
            formatted_date = parsed_date.strftime("%A %d %B %Y à %Hh%M")
        except Exception:
            formatted_date = raw_date  # fallback brut

        embed = discord.Embed(
            title="📅 Prochain Tournoi",
            description=f"**Date :** {formatted_date}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="📥 Decks libres", value="- Aucune info disponible", inline=False)
        embed.add_field(name="📤 Decks pris", value="- Aucune info disponible", inline=False)

        await ctx.send(embed=embed)

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.tournoi.category = "Tournoi"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = Tournoi)")
