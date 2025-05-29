# ───────────────────────────────────────────────────────────────────────────────
# 🎴 tournoi.py — Commande !tournoi
# Affiche la date du prochain tournoi ainsi que les decks disponibles.
# Utilise Google Sheets (CSV) et Supabase.
# Catégorie : "VAACT"
# ───────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
from supabase import create_client, Client
import os

# ───────────────────────────────────────────────────────────────────────────────
# 🔐 Connexion à Supabase + URL CSV
# ───────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────

class Tournoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tournoi",
        help="Affiche les infos du prochain tournoi et les decks disponibles."
    )
    async def tournoi(self, ctx):
        try:
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV n'est pas configurée.")
                return

            # 🔗 Lecture du CSV via texte (contourne erreur SSL)
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer le fichier de données.")
                        return
                    text = await resp.text()

            # 📊 Parsing CSV
            df = pd.read_csv(io.StringIO(text))
            df["PRIS ?"] = df["PRIS ?"].fillna("").str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["MECANIQUES"] = df.get("MECANIQUES", "—").fillna("—")
            df["DIFFICULTE"] = df.get("DIFFICULTE", "—").fillna("—")

            pris = df[df["PRIS ?"].astype(str).str.lower().isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].astype(str).str.lower().isin(["true", "✅"])]

            # 📅 Date du tournoi depuis Supabase
            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            if tournoi_data.data and "prochaine_date" in tournoi_data.data[0]:
                date_tournoi = tournoi_data.data[0]["prochaine_date"]
            else:
                date_tournoi = "🗓️ à venir !"

            # 🛠️ Embed Discord
            embed = discord.Embed(
                title="🎴 Tournoi Yu-Gi-Oh VAACT",
                description=f"Le prochain tournoi aura lieu : **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="🎮 Decks disponibles", value=str(len(libres)), inline=True)
            embed.add_field(name="🔒 Decks pris", value=str(len(pris)), inline=True)
            embed.add_field(name="📋 Total", value=str(len(df)), inline=True)

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

            embed.set_footer(text="Données fournies par l'organisation du tournoi.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR TOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue lors de la récupération des données du tournoi.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Setup
# ───────────────────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = Tournoi(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
