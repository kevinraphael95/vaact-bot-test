# ───────────────────────────────────────────────────────────────────────────────
# 🎴 tournoi.py — Commande !tournoi
# Cette commande affiche la date du prochain tournoi ainsi que les decks disponibles.
# Elle utilise un fichier CSV et une table Supabase pour afficher dynamiquement l'état.
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
# 🔐 Connexion à Supabase via variables d'environnement (Render / .env)
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
            # 📥 Vérifie l’URL du CSV
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV n'est pas configurée.")
                return

            # 🔗 Téléchargement du CSV via HTTP
            async with aiohttp.ClientSession() as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer le fichier de données.")
                        return
                    data = await resp.read()

            # 📊 Lecture et parsing du CSV avec Pandas
            df = pd.read_csv(io.BytesIO(data), encoding="utf-8", sep=",")
            df.columns = df.columns.str.strip().str.upper()  # 🧼 Nettoyage noms de colonnes

            # 📌 Vérifie la présence des colonnes essentielles
            required = ["PERSONNAGE", "ARCHETYPE(S)", "MECANIQUES", "DIFFICULTE", "PRIS ?"]
            for col in required:
                if col not in df.columns:
                    await ctx.send(f"🚨 Colonne manquante dans le CSV : `{col}`")
                    return

            # 🧼 Nettoyage des valeurs
            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.lower().str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df["ARCHETYPE(S)"].fillna("—")
            df["MECANIQUES"] = df["MECANIQUES"].fillna("—")
            df["DIFFICULTE"] = df["DIFFICULTE"].fillna("—")

            # 🎯 Filtrage des decks pris et libres
            pris = df[df["PRIS ?"].isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].isin(["true", "✅"])]

            # 📅 Récupération de la date depuis Supabase
            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            if tournoi_data.data and "prochaine_date" in tournoi_data.data[0]:
                date_tournoi = tournoi_data.data[0]["prochaine_date"]
            else:
                date_tournoi = "🗓️ à venir !"

            # 🛠️ Construction de l'embed
            embed = discord.Embed(
                title="🎴 Tournoi Yu-Gi-Oh VAACT",
                description=f"📅 Prochain tournoi : **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="🆓 Decks disponibles", value=str(len(libres)), inline=True)
            embed.add_field(name="🔒 Decks pris", value=str(len(pris)), inline=True)
            embed.add_field(name="📋 Total", value=str(len(df)), inline=True)

            # 📃 Liste des decks disponibles
            lignes = []
            for _, row in libres.iterrows():
                ligne = f"• **{row['PERSONNAGE']}** — *{row['ARCHETYPE(S)']}*\n"
                ligne += f"   ⚙️ {row['MECANIQUES']} | 🎯 Difficulté {row['DIFFICULTE']}\n"
                lignes.append(ligne)

            texte = "\n".join(lignes)
            if len(texte) > 1024:
                texte = "\n".join(lignes[:15]) + "\n... *(liste coupée)*"

            embed.add_field(
                name="📜 Liste des decks libres",
                value=texte if lignes else "Aucun deck disponible.",
                inline=False
            )

            embed.set_footer(text="Données fournies par l'organisation du tournoi.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR TOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue lors de la récupération des données du tournoi.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog
# Attribution de la catégorie "VAACT" pour les systèmes de help personnalisés
# ───────────────────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = Tournoi(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
