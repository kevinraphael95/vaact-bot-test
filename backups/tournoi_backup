# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector, ClientConnectionError
from supabase import create_client, Client

# 🔐 Variables d'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

# 🔌 Connexion Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔧 View pour pagination
class TournoiView(discord.ui.View):
    def __init__(self, pages, titre, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page = 0
        self.titre = titre

    async def update_embed(self, interaction: discord.Interaction):
        embed = self.pages[self.page]
        embed.title = self.titre
        embed.set_footer(text=f"Page {self.page + 1}/{len(self.pages)} • Decks triés par difficulté")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % len(self.pages)
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % len(self.pages)
        await self.update_embed(interaction)

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="tournoi",
        aliases=["decks", "tournoivaact"],
        help="📅 Affiche la date du tournoi et les decks disponibles/pris."
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
                await ctx.send("🚨 Erreur réseau lors de la récupération du fichier.")
                return

            try:
                df = pd.read_csv(io.StringIO(text), skiprows=1)
                df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
                df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
                df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
                df["DIFFICULTÉ"] = df.get("DIFFICULTÉ", "—").fillna("—")
                pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
                libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]
            except Exception as e:
                traceback.print_exc()
                await ctx.send("📉 Fichier CSV invalide ou mal formaté.")
                return

            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception as e:
                date_tournoi = "🗓️ à venir !"

            difficulte_order = ["1/3", "2/3", "3/3"]
            libres["DIFFICULTÉ"] = pd.Categorical(libres["DIFFICULTÉ"], categories=difficulte_order, ordered=True)
            libres_sorted = libres.sort_values("DIFFICULTÉ")
            chunks = [libres_sorted[i:i+15] for i in range(0, len(libres_sorted), 15)]

            pages = []
            for chunk in chunks:
                texte = ""
                for _, row in chunk.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
                embed = discord.Embed(description=texte, color=discord.Color.green())
                pages.append(embed)

            titre_embed = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"
            view = TournoiView(pages, titre_embed)

            texte_pris = ""
            for _, row in pris.iterrows():
                ligne = f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                if len(texte_pris) + len(ligne) < 1000:
                    texte_pris += ligne
                else:
                    texte_pris += "\n... *(liste coupée)*"
                    break

            if texte_pris:
                embed_pris = discord.Embed(
                    title="🔒 Decks déjà pris",
                    description=texte_pris,
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed_pris)

            await ctx.send(embed=pages[0], view=view)

        except Exception as e:
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
