# ────────────────────────────────────────────────────────────────────────────────
# 📁 testtournoi.py
# ────────────────────────────────────────────────────────────────────────────────
# Cette commande affiche :
# 1. La date du prochain tournoi (depuis Supabase)
# 2. Les decks disponibles
# 3. Les decks déjà pris
# Les données sont lues depuis un fichier CSV (Google Sheets publié).
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                          # Composants Discord (Embed, etc.)
from discord.ext import commands                        # Système de commandes
import pandas as pd                                     # Manipulation du CSV
import aiohttp                                          # Requêtes HTTP asynchrones
import io, ssl, os, traceback                           # Utilitaires système
from aiohttp import TCPConnector, ClientConnectionError # Connexions sécurisées
from supabase import create_client, Client              # Accès base Supabase

# ────────────────────────────────────────────────────────────────────────────────
# 🔐 VARIABLES D’ENVIRONNEMENT
# ────────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")               # URL Supabase
SUPABASE_KEY = os.getenv("SUPABASE_KEY")               # Clé API Supabase
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")             # URL du CSV en ligne

# 🔌 Connexion à Supabase (objet global)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ────────────────────────────────────────────────────────────────────────────────
class TestTournoiCommand(commands.Cog):
    """Commande !testtournoi — Affiche la liste des decks et la prochaine date."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Référence du bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !testtournoi
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(name="testtournoi",aliases=[],help="📅 Affiche la date du tournoi et la liste des decks disponibles/pris.") # noms de commande
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 cooldown
    async def testtournoi(self, ctx: commands.Context):
        try:
            # ───── Étape 1 : Vérifie que l’URL du CSV est présente ─────
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV est manquante.")
                return

            # ───── Étape 2 : Téléchargement du CSV (avec SSL custom) ─────
            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')  # 🔐 Niveau de sécurité modifié
            connector = TCPConnector(ssl=sslcontext)

            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(SHEET_CSV_URL) as resp:
                        if resp.status != 200:
                            await ctx.send("❌ Erreur lors du téléchargement du fichier CSV.")
                            return
                        text = (await resp.read()).decode("utf-8")  # 📄 Contenu brut
            except ClientConnectionError as e:
                print(f"[ERREUR AIOHTTP] {e}")
                await ctx.send("🚨 Erreur réseau lors de la récupération du fichier.")
                return

            # ───── Étape 3 : Lecture et nettoyage du CSV ─────
            try:
                df = pd.read_csv(io.StringIO(text), skiprows=1)  # 📊 Charge les données en ignorant l’en-tête double
                df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()  # ✅ Nettoie les colonnes
                df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
                df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")

                pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]      # 🔒 Decks pris
                libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]   # 🆓 Decks libres
            except Exception as e:
                print(f"[ERREUR CSV] {e}")
                traceback.print_exc()
                await ctx.send("📉 Fichier CSV invalide ou mal formaté.")
                return

            # ───── Étape 4 : Récupération de la date du tournoi (Supabase) ─────
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception as e:
                print(f"[ERREUR SUPABASE] {e}")
                date_tournoi = "🗓️ à venir !"

            # ───── Étape 5 : Construction de l'embed Discord ─────
            embed = discord.Embed(
                title="🎴 Prochain Tournoi Yu-Gi-Oh VAACT",
                description=f"📅 **Le prochain tournoi aura lieu :**\n🎯 __**{date_tournoi}**__",
                color=discord.Color.dark_orange()
            )  


            # 🆓 Decks disponibles groupés par saison
            texte_libres = ""
            if "SAISON" in libres.columns:
                groupes_libres = libres.groupby("SAISON")
                for saison, decks in groupes_libres:
                    bloc = f"▸ **{saison}**\n"
                    for _, row in decks.iterrows():
                        bloc += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                    texte_libres += f"> {bloc}\n"
            else:
                texte_libres = "⚠️ Colonne 'SAISON' manquante dans le fichier."


            # 🔒 Decks déjà pris
            # 🔒 Decks pris groupés par saison
            texte_pris = ""
            if "SAISON" in pris.columns:
                groupes_pris = pris.groupby("SAISON")
                for saison, decks in groupes_pris:
                    bloc = f"▸ **{saison}**\n"
                    for _, row in decks.iterrows():
                        bloc += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                    texte_pris += f"> {bloc}\n"
            else:
                texte_pris = "⚠️ Colonne 'SAISON' manquante dans le fichier."


            embed.set_footer(text="Decks fournis par l'organisation du tournoi.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR GLOBALE] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    # ────────────────────────────────────────────────────────────────────────────
    # 🏷️ CATÉGORISATION
    # ────────────────────────────────────────────────────────────────────────────
    def cog_load(self):
        """Classement de la commande pour !help"""
        self.testtournoi.category = "VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 SETUP : Chargement automatique du cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """Fonction appelée pour ajouter ce cog au bot."""
    await bot.add_cog(TestTournoiCommand(bot))
    print("✅ Cog chargé : TestTournoiCommand (catégorie = VAACT)")
