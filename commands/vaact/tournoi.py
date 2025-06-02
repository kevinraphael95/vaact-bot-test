# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import pandas as pd
import aiohttp, os, io, ssl, traceback
from aiohttp import TCPConnector
from supabase import create_client, Client

# 🔐 Variables d’environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

# 🔌 Connexion Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔧 View pagination
class TournoiView(discord.ui.View):
    def __init__(self, pages, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page = 0

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.pages[self.page], view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % len(self.pages)
        await self.update(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % len(self.pages)
        await self.update(interaction)

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
        help="📅 Affiche la date du tournoi et les decks libres/pris par difficulté"
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            # Récupération CSV
            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    text = (await resp.read()).decode("utf-8")
            df = pd.read_csv(io.StringIO(text), skiprows=1)

            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.lower()
            df["DIFFICULTE"] = df["DIFFICULTE"].fillna("—")
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")

            pris = df[df["PRIS ?"].isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].isin(["true", "✅"])]

            difficulte_order = ["1", "2", "3"]

            def embed_decks(df_filtré, pris, difficulté):
                noms = df_filtré[df_filtré["DIFFICULTE"] == difficulté]["PERSONNAGE"].tolist()
                if not noms:
                    texte = "Aucun deck trouvé."
                else:
                    texte = "\n".join(f"• {nom}" for nom in noms)
                titre = f"{'🔒' if pris else '🟢'} {'Pris' if pris else 'Libres'} — Difficulté {difficulté}/3"
                couleur = discord.Color.red() if pris else discord.Color.green()
                return discord.Embed(title=titre, description=texte, color=couleur)

            pages = []
            for d in difficulte_order:
                pages.append(embed_decks(libres, False, d))
            for d in difficulte_order:
                pages.append(embed_decks(pris, True, d))

            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data else "🗓️ à venir"

            pages[0].insert_field_at(0, name="📅 Prochain Tournoi Yu-Gi-Oh VAACT", value=f"**{date_tournoi}**", inline=False)

            await ctx.send(embed=pages[0], view=TournoiView(pages))

        except Exception as e:
            traceback.print_exc()
            await ctx.send("❌ Une erreur est survenue.")

    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
