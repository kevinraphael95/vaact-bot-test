import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime
import locale

# Optionnel : pour avoir la date en français dans strftime, mais nécessite que le système supporte la locale française
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    pass  # Sur certains serveurs ça ne fonctionne pas, fallback en anglais

class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("🔧 TournoiCommand initialisé")

    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi et l'état des decks (placeholder)."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        print(f"➡️ Commande !tournoi appelée par {ctx.author} (ID {ctx.author.id})")

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Variables SUPABASE_URL ou SUPABASE_KEY manquantes")
            await ctx.send("❌ Configuration du bot incorrecte (clés manquantes).")
            return

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{SUPABASE_URL}/rest/v1/tournoi?select=date&order=date.desc&limit=1"
                async with session.get(url, headers=headers) as response:
                    print(f"🔗 Requête vers Supabase status: {response.status}")
                    if response.status != 200:
                        await ctx.send(f"❌ Erreur lors de la récupération des données (code {response.status}).")
                        return
                    data = await response.json()
                    print(f"📥 Données reçues: {data}")
        except Exception as e:
            print(f"❌ Erreur lors de la requête HTTP : {e}")
            await ctx.send("❌ Erreur lors de la récupération des données.")
            return

        if not data:
            await ctx.send("❌ Aucune date de tournoi trouvée.")
            return

        raw_date = data[0].get("date")
        if not raw_date:
            await ctx.send("❌ Date de tournoi invalide ou manquante.")
            return

        try:
            parsed_date = datetime.fromisoformat(raw_date)
            formatted_date = parsed_date.strftime("%A %d %B %Y à %Hh%M")
            # Exemple: "mardi 02 juin 2025 à 20h30"
        except Exception as e:
            print(f"❌ Erreur parsing date : {e}")
            formatted_date = raw_date  # fallback brut

        embed = discord.Embed(
            title="📅 Prochain Tournoi",
            description=f"**Date :** {formatted_date}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="📥 Decks libres", value="- Aucune info disponible", inline=False)
        embed.add_field(name="📤 Decks pris", value="- Aucune info disponible", inline=False)

        await ctx.send(embed=embed)
        print("✅ Embed envoyé avec succès")

async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    # On ajoute la catégorie "VAACT" à la commande 'tournoi' dans ce cog
    cmd = cog.get_command("tournoi")
    if cmd:
        cmd.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
