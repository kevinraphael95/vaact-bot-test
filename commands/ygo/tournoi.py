import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
from supabase import create_client, Client
import os

# Connexion à Supabase (⚠️ remplace par tes clés ou utilise des variables d’environnement)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Tournoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tournoi")
    async def tournoi(self, ctx):
        try:
            # 🔗 Télécharge le CSV depuis Google Sheets
            sheet_csv_url = "https://docs.google.com/spreadsheets/d/1ifAWeG16Q-wULckgOVOBpsjgYJ25k-9gtQYtivYBCtI/export?format=csv&gid=0"
            async with aiohttp.ClientSession() as session:
                async with session.get(sheet_csv_url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer le fichier Google Sheet.")
                        return
                    data = await resp.read()

            # 📊 Lecture du fichier CSV
            df = pd.read_csv(io.BytesIO(data))

            # 🔧 Nettoyage et normalisation
            df["PRIS ?"] = df["PRIS ?"].fillna("").str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["MECANIQUES"] = df.get("MECANIQUES", "—").fillna("—")
            df["DIFFICULTE"] = df.get("DIFFICULTE", "—").fillna("—")

            # 🎯 Séparation des decks pris/libres
            pris = df[df["PRIS ?"] == "✅"]
            libres = df[df["PRIS ?"] != "✅"]

            # 📅 Récupération de la date depuis Supabase
            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            if tournoi_data.data and "prochaine_date" in tournoi_data.data[0]:
                date_tournoi = tournoi_data.data[0]["prochaine_date"]
            else:
                date_tournoi = "🗓️ à venir !"

            # 📦 Embed Discord
            embed = discord.Embed(
                title="🎴 Tournoi Yu-Gi-Oh VAACT",
                description=f"Le prochain tournoi **Yu-Gi-Oh VAACT** aura lieu : **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="🎮 Decks disponibles", value=str(len(libres)), inline=True)
            embed.add_field(name="🔒 Decks pris", value=str(len(pris)), inline=True)
            embed.add_field(name="📋 Total", value=str(len(df)), inline=True)

            # 📝 Liste des decks libres
            lignes = []
            for _, row in libres.iterrows():
                ligne = f"• **{row['PERSONNAGE']}** — *{row['ARCHETYPE(S)']}*\n"
                ligne += f"    ⚙️ {row['MECANIQUES']} | 🎯 Difficulté {row['DIFFICULTE']}\n"
                lignes.append(ligne)

            texte = "\n".join(lignes)
            if len(texte) > 1024:
                texte = "\n".join(lignes[:15]) + "\n... *(liste coupée)*"

            embed.add_field(
                name="🆓 Liste des decks libres",
                value=texte if lignes else "Aucun deck disponible.",
                inline=False
            )
            embed.set_footer(text="Données récupérées depuis le Google Sheet officiel du tournoi.")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR TOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue lors de la récupération des données du tournoi.")

# Enregistrement du Cog
async def setup(bot):
    await bot.add_cog(Tournoi(bot))
