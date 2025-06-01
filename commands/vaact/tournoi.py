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

    @commands.command(name="tournoi", aliases=["decks", "tournoivaact"])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV est manquante.")
                return

            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erreur lors du téléchargement du fichier CSV.")
                        return
                    text = (await resp.read()).decode("utf-8")

            df = pd.read_csv(io.StringIO(text), skiprows=1)
            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["DIFFICULTÉ"] = df.get("DIFFICULTÉ", "—").fillna("—")

            pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

            # Récupérer date tournoi supabase
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception:
                date_tournoi = "🗓️ à venir !"

            difficulte_order = ["1/3", "2/3", "3/3"]
            libres["DIFFICULTÉ"] = pd.Categorical(libres["DIFFICULTÉ"], categories=difficulte_order, ordered=True)
            pris["DIFFICULTÉ"] = pd.Categorical(pris["DIFFICULTÉ"], categories=difficulte_order, ordered=True)

            # Fonction pour créer la description texte d'une DataFrame
            def format_decks_section(df_section):
                texte = ""
                for _, row in df_section.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
                return texte if texte else "Aucun deck ici."

            # Construire pages : on alterne entre libres et pris, par difficulté
            pages = []
            titre_embed = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"

            for diff in difficulte_order:
                # Decks libres pour cette difficulté
                libres_diff = libres[libres["DIFFICULTÉ"] == diff]
                texte_libres = format_decks_section(libres_diff)

                # Decks pris pour cette difficulté
                pris_diff = pris[pris["DIFFICULTÉ"] == diff]
                texte_pris = format_decks_section(pris_diff)

                description = f"**Decks Libres — Difficulté {diff}**\n{texte_libres}\n\n" \
                              f"**Decks Pris — Difficulté {diff}**\n{texte_pris}"

                embed = discord.Embed(description=description, color=discord.Color.blurple())
                pages.append(embed)

            if not pages:
                await ctx.send("Aucun deck disponible ni pris trouvé.")
                return

            view = TournoiView(pages, titre_embed)
            await ctx.send(embed=pages[0], view=view)

        except Exception:
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    def cog_load(self):
        self.tournoi.category = "VAACT"

async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
