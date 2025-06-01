import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector, ClientConnectionError
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

            # Récupération du CSV
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erreur lors du téléchargement du fichier CSV.")
                        return
                    text = (await resp.read()).decode("utf-8")

            # Lecture CSV et séparation decks pris / libres
            df = pd.read_csv(io.StringIO(text), skiprows=1)
            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["DIFFICULTÉ"] = df.get("DIFFICULTÉ", "—").fillna("—")

            pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

            # Récupération date tournoi Supabase
            tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            if tournoi_data.data and "prochaine_date" in tournoi_data.data[0]:
                date_tournoi = tournoi_data.data[0]["prochaine_date"]
            else:
                date_tournoi = "🗓️ à venir !"

            difficulte_order = ["1/3", "2/3", "3/3"]

            # Fonction utilitaire pour générer les textes par difficulté
            def format_decks_par_difficulte(df_decks):
                textes = []
                for diff in difficulte_order:
                    part = df_decks[df_decks["DIFFICULTÉ"] == diff]
                    if not part.empty:
                        textes.append(f"**Difficulté {diff}**")
                        for _, row in part.iterrows():
                            textes.append(f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*")
                        textes.append("")  # ligne vide entre les sections
                return "\n".join(textes)

            # Texte des decks libres
            texte_libres = format_decks_par_difficulte(libres)
            # Texte des decks pris
            texte_pris = format_decks_par_difficulte(pris)

            # Pour alléger, on découpe en pages de ~1000 caractères max
            def chunk_text(text, max_len=900):
                lines = text.split('\n')
                chunks = []
                current = []
                length = 0
                for line in lines:
                    length += len(line) + 1
                    if length > max_len and current:
                        chunks.append("\n".join(current))
                        current = [line]
                        length = len(line) + 1
                    else:
                        current.append(line)
                if current:
                    chunks.append("\n".join(current))
                return chunks

            pages = []

            # On prépare les pages qui vont alterner libre/pris (ex : page1 = decks libres 1ère partie, page2 = decks pris 1ère partie, etc)

            libres_chunks = chunk_text(texte_libres) if texte_libres else ["*Aucun deck libre*"]
            pris_chunks = chunk_text(texte_pris) if texte_pris else ["*Aucun deck pris*"]

            max_pages = max(len(libres_chunks), len(pris_chunks))

            for i in range(max_pages):
                desc = ""
                if i < len(libres_chunks):
                    desc += f"🟢 **Decks Libres**\n{libres_chunks[i]}\n"
                if i < len(pris_chunks):
                    desc += f"🔴 **Decks Pris**\n{pris_chunks[i]}"
                embed = discord.Embed(description=desc, color=discord.Color.blurple())
                pages.append(embed)

            titre_embed = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"

            view = TournoiView(pages, titre_embed)

            await ctx.send(embed=pages[0], view=view)

        except Exception as e:
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
