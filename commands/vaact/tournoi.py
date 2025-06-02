import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime
import csv
import io

class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("🔧 TournoiCommand initialisé")

    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi et l'état des decks."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            await ctx.send("❌ Configuration du bot incorrecte (clés Supabase manquantes).")
            return

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        # Récupération de la date du tournoi via Supabase REST API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{SUPABASE_URL}/rest/v1/tournoi?select=date&order=date.asc&limit=1",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        await ctx.send("❌ Erreur lors de la récupération de la date du tournoi.")
                        return
                    data = await response.json()
        except Exception as e:
            await ctx.send(f"❌ Erreur réseau: {e}")
            return

        if not data:
            await ctx.send("❌ Aucune date de tournoi trouvée.")
            return

        raw_date = data[0].get("date")
        try:
            parsed_date = datetime.fromisoformat(raw_date)
            formatted_date = parsed_date.strftime("%A %d %B %Y à %Hh%M")
        except Exception:
            formatted_date = raw_date

        # Exemple : charger les decks depuis un CSV local (modifie selon ta source)
        # Le CSV pourrait avoir des colonnes : nom_deck, difficulte (1,2,3), status (libre/pris)
        decks_libres = []
        decks_pris = []
        try:
            with open("data/decks.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    deck_name = row.get("nom_deck", "Inconnu")
                    difficulte = row.get("difficulte", "1")
                    status = row.get("status", "libre")
                    # Regroupement selon le status
                    if status.lower() == "libre":
                        decks_libres.append((deck_name, difficulte))
                    else:
                        decks_pris.append((deck_name, difficulte))
        except FileNotFoundError:
            # Pas de fichier CSV : placeholder
            decks_libres = [("Aucun deck libre", "1")]
            decks_pris = [("Aucun deck pris", "1")]

        # Trier par difficulté croissante
        decks_libres.sort(key=lambda x: int(x[1]))
        decks_pris.sort(key=lambda x: int(x[1]))

        # Construire l’embed
        embed = discord.Embed(
            title="📅 Prochain Tournoi",
            description=f"**Date :** {formatted_date}",
            color=discord.Color.blurple()
        )

        # Champs decks libres, affichage simple listé par difficulté
        def format_decks(decks):
            lines = []
            current_diff = None
            for name, diff in decks:
                if diff != current_diff:
                    current_diff = diff
                    lines.append(f"**Difficulté {diff} :**")
                lines.append(f"- {name}")
            return "\n".join(lines)

        embed.add_field(name="📥 Decks libres", value=format_decks(decks_libres), inline=False)
        embed.add_field(name="📤 Decks pris", value=format_decks(decks_pris), inline=False)

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiCommand")
