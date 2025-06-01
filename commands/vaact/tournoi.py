# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi avec menus déroulants
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from discord import app_commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector, ClientConnectionError
from supabase import create_client, Client

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

    # Helper : charge les données du CSV
    async def load_decks(self):
        sslcontext = ssl.create_default_context()
        sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
        connector = TCPConnector(ssl=sslcontext)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(SHEET_CSV_URL) as resp:
                if resp.status != 200:
                    raise Exception("Erreur téléchargement CSV")
                text = (await resp.read()).decode("utf-8")

        df = pd.read_csv(io.StringIO(text), skiprows=1)
        df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
        df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
        df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
        df["DIFFICULTE"] = df.get("DIFFICULTE", "Inconnue").fillna("Inconnue")

        pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
        libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

        # Group by difficulty
        libres_grouped = {k: v for k, v in libres.groupby("DIFFICULTE")}
        pris_grouped = {k: v for k, v in pris.groupby("DIFFICULTE")}

        return libres_grouped, pris_grouped

    # Helper : récupère la date du tournoi
    async def get_date_tournoi(self):
        try:
            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            return tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
        except Exception as e:
            print(f"[ERREUR SUPABASE] {e}")
            return "🗓️ à venir !"

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="tournoi",
        aliases=["decks", "tournoivaact"],
        help="📅 Affiche la date du tournoi et la liste des decks disponibles/pris avec menus déroulants."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):

        try:
            libres_grouped, pris_grouped = await self.load_decks()
            date_tournoi = await self.get_date_tournoi()

            # Embed avec la date
            embed = discord.Embed(
                title="🎴 Prochain Tournoi Yu-Gi-Oh VAACT",
                description=f"📅 **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Decks fournis par l'organisation du tournoi.")

            # Components : 2 menus déroulants, un pour libres, un pour pris
            view = discord.ui.View(timeout=180)  # 3 minutes de timeout

            # Menu déroulant pour decks libres
            options_libres = [
                discord.SelectOption(label=diff, description=f"{len(df)} deck(s)")
                for diff, df in libres_grouped.items()
            ]
            select_libres = discord.ui.Select(
                placeholder="Sélectionnez la difficulté des decks libres",
                options=options_libres,
                custom_id="select_libres"
            )
            # Callback menu libres
            async def callback_libres(interaction: discord.Interaction):
                diff = interaction.data["values"][0]
                decks = libres_grouped.get(diff)
                if decks is None:
                    await interaction.response.send_message("❌ Difficulté inconnue.", ephemeral=True)
                    return

                texte = f"**Decks libres — Difficulté {diff} :**\n"
                for _, row in decks.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"

                # Envoyer une réponse éphémère
                await interaction.response.send_message(texte, ephemeral=True)

            select_libres.callback = callback_libres
            view.add_item(select_libres)

            # Menu déroulant pour decks pris
            options_pris = [
                discord.SelectOption(label=diff, description=f"{len(df)} deck(s)")
                for diff, df in pris_grouped.items()
            ]
            select_pris = discord.ui.Select(
                placeholder="Sélectionnez la difficulté des decks pris",
                options=options_pris,
                custom_id="select_pris"
            )
            # Callback menu pris
            async def callback_pris(interaction: discord.Interaction):
                diff = interaction.data["values"][0]
                decks = pris_grouped.get(diff)
                if decks is None:
                    await interaction.response.send_message("❌ Difficulté inconnue.", ephemeral=True)
                    return

                texte = f"**Decks pris — Difficulté {diff} :**\n"
                for _, row in decks.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"

                await interaction.response.send_message(texte, ephemeral=True)

            select_pris.callback = callback_pris
            view.add_item(select_pris)

            await ctx.send(embed=embed, view=view)

        except Exception as e:
            print(f"[ERREUR GLOBALE] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    # ──────────────────────────────────────────────────────────
    # 🏷️ Catégorisation pour !help
    # ──────────────────────────────────────────────────────────
    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
