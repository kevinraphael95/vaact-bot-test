import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
import ssl
from aiohttp import TCPConnector, ClientConnectionError
from supabase import create_client, Client
import os
import traceback

# ───────────────────────────────────────────────────────────────────────────────
# 🔐 Connexion Supabase & URL du CSV
# ───────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")  # https://docs.google.com/...&export=csv&gid=...

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
            # 🧪 Vérifie l'URL
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV est manquante.")
                return

            # 🔐 SSL Patch (Google Sheets aime pas toujours aiohttp)
            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)

            # 📥 Téléchargement du CSV
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(SHEET_CSV_URL) as resp:
                        if resp.status != 200:
                            print(f"[ERREUR HTTP] Statut: {resp.status}")
                            await ctx.send("❌ Le fichier CSV n'a pas pu être récupéré (code HTTP).")
                            return
                        data = await resp.read()
                        text = data.decode("utf-8")
            except ClientConnectionError as e:
                print(f"[ERREUR SSL AIOHTTP] {e}")
                await ctx.send("🚨 Erreur réseau lors du téléchargement du fichier.")
                return
            except Exception as e:
                print(f"[ERREUR AIOHTTP INCONNUE] {e}")
                await ctx.send("❌ Une erreur est survenue lors de la récupération du fichier CSV.")
                return

            # 🧾 Lecture & nettoyage du CSV
            try:
                df = pd.read_csv(io.StringIO(text), skiprows=1)

                df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
                df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
                df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
                df["MECANIQUES"] = df.get("MECANIQUES", "—").fillna("—")
                df["DIFFICULTE"] = df.get("DIFFICULTE", "—").fillna("—")

                pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
                libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]
            except Exception as e:
                print(f"[ERREUR CSV] {e}")
                traceback.print_exc()
                await ctx.send("📉 Le fichier CSV est invalide ou mal formaté.")
                return

            # 📆 Récupération de la date dans Supabase
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception as e:
                print(f"[ERREUR SUPABASE] {e}")
                date_tournoi = "🗓️ à venir !"

            # 🛠️ Construction de l'embed
            embed = discord.Embed(
                title="🎴 Tournoi Yu-Gi-Oh VAACT",
                description=f"Le prochain tournoi aura lieu : **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="🎮 Decks disponibles", value=str(len(libres)), inline=True)
            embed.add_field(name="🔒 Decks pris", value=str(len(pris)), inline=True)
            embed.add_field(name="📋 Total", value=str(len(df)), inline=True)

            # 📝 Détail des decks libres
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
            print(f"[ERREUR GLOBALE TOURNOI] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue lors de l'exécution de la commande.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog
# ───────────────────────────────────────────────────────────────────────────────
async def setup(bot):
    cog = Tournoi(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
