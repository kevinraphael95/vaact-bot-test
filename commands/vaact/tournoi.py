# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import os, aiohttp, io, ssl, traceback
import pandas as pd
from aiohttp import TCPConnector
from supabase import create_client, Client

# 🔐 Variables d'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CSV_URL = os.getenv("SHEET_CSV_URL")


# 🔌 Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ──────────────────────────────────────────────────────────────
# 🔧 View pour pagination
# ──────────────────────────────────────────────────────────────
class DeckPagination(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], title: str, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.title = title
        self.page = 0

    async def update(self, interaction: discord.Interaction):
        embed = self.pages[self.page]
        embed.title = self.title
        embed.set_footer(text=f"Page {self.page + 1}/{len(self.pages)} • Decks triés par difficulté")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, _):
        self.page = (self.page - 1) % len(self.pages)
        await self.update(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, _):
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
        help="📅 Affiche la date du tournoi et les decks disponibles/pris."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            # 🔄 Récupération CSV
            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer le fichier CSV.")
                        return
                    content = await resp.read()
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            df.fillna("", inplace=True)

            # 🧹 Nettoyage
            df["PRIS ?"] = df["PRIS ?"].str.lower().isin(["true", "✅"])
            df["DIFFICULTÉ"] = df["DIFFICULTÉ"].astype(str)
            df["DIFFICULTÉ"] = pd.Categorical(df["DIFFICULTÉ"], categories=["1/3", "2/3", "3/3"], ordered=True)
            df.sort_values(["DIFFICULTÉ", "PERSONNAGE"], inplace=True)

            # 🟥 Séparation des decks
            libres = df[df["PRIS ?"] == False]
            pris = df[df["PRIS ?"] == True]

            # 📅 Date du tournoi
            try:
                res = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = res.data[0]["prochaine_date"] if res.data else "🗓️ à venir"
            except Exception:
                date_tournoi = "🗓️ à venir"

            # 📘 Pages embeds decks libres
            pages = []
            group = []
            for _, row in libres.iterrows():
                group.append(f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})")
                if len(group) == 10:
                    embed = discord.Embed(description="\n".join(group), color=discord.Color.green())
                    pages.append(embed)
                    group = []
            if group:
                embed = discord.Embed(description="\n".join(group), color=discord.Color.green())
                pages.append(embed)

            titre = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"
            view = DeckPagination(pages, titre)

            # 📕 Decks pris (1 seul embed si possible)
            texte_pris = ""
            for _, row in pris.iterrows():
                line = f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
                if len(texte_pris) + len(line) < 1000:
                    texte_pris += line
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

            # ▶️ Envoi principal
            await ctx.send(embed=pages[0], view=view)

        except Exception as e:
            traceback.print_exc()
            await ctx.send("⚠️ Une erreur est survenue lors de l'exécution de la commande.")

    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
