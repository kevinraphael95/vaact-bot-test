# ──────────────────────────────────────────────────────────────
# 📁 TOURNOI
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────
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

# 🔐 Variables d’environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="tournoi",
        aliases=["decks", "tournoivaact"],
        help="📅 Affiche la date du prochain tournoi et la liste des decks disponibles et pris."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV est manquante.")
                return

            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)

            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(SHEET_CSV_URL) as resp:
                        if resp.status != 200:
                            await ctx.send("❌ Erreur lors du téléchargement du fichier CSV.")
                            return
                        text = (await resp.read()).decode("utf-8")
            except ClientConnectionError as e:
                print(f"[ERREUR AIOHTTP] {e}")
                await ctx.send("🚨 Erreur réseau lors de la récupération du fichier.")
                return

            try:
                df = pd.read_csv(io.StringIO(text), skiprows=1)
                df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
                df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
                df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
                pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
                libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]
            except Exception as e:
                print(f"[ERREUR CSV] {e}")
                traceback.print_exc()
                await ctx.send("📉 Fichier CSV invalide ou mal formaté.")
                return

            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception as e:
                print(f"[ERREUR SUPABASE] {e}")
                date_tournoi = "🗓️ à venir !"

            embed = discord.Embed(
                title="🎴 Prochain Tournoi Yu-Gi-Oh VAACT",
                description=f"📅 **{date_tournoi}**",
                color=discord.Color.purple()
            )

            # Decks libres
            texte_libres = ""
            for _, row in libres.iterrows():
                ligne = f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                if len(texte_libres) + len(ligne) < 1000:
                    texte_libres += ligne
                else:
                    texte_libres += "\n... *(liste coupée)*"
                    break
            embed.add_field(
                name="🆓 Decks disponibles",
                value=texte_libres or "Aucun deck disponible.",
                inline=False
            )

            # Decks pris
            texte_pris = ""
            for _, row in pris.iterrows():
                ligne = f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                if len(texte_pris) + len(ligne) < 1000:
                    texte_pris += ligne
                else:
                    texte_pris += "\n... *(liste coupée)*"
                    break
            embed.add_field(
                name="🔒 Decks déjà pris",
                value=texte_pris or "Aucun deck réservé.",
                inline=False
            )

            embed.set_footer(text="Decks fournis par l'organisation du tournoi.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR GLOBALE] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
