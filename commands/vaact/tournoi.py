import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DIFFICULTE_ORDER = ["1/3", "2/3", "3/3"]

class TournoiView(discord.ui.View):
    def __init__(self, data_dict, titre, timeout=180):
        super().__init__(timeout=timeout)
        self.data = data_dict  # dict { "Libre 1/3": [embed, embed, ...], "Pris 2/3": [...], ... }
        self.titre = titre
        self.page = 0
        self.current_key = list(self.data.keys())[0]

        # Select unique avec toutes les catégories + difficultés
        options = [discord.SelectOption(label=k, value=k) for k in self.data.keys()]
        self.select = discord.ui.Select(
            placeholder="Choisissez catégorie + difficulté",
            options=options,
            row=0
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

        # Boutons précédent / suivant
        self.prev_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary, row=1)
        self.next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary, row=1)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def select_callback(self, interaction: discord.Interaction):
        self.current_key = self.select.values[0]
        self.page = 0
        await self.update_embed(interaction)

    async def prev_page(self, interaction: discord.Interaction):
        self.page = (self.page - 1) % len(self.data[self.current_key])
        await self.update_embed(interaction)

    async def next_page(self, interaction: discord.Interaction):
        self.page = (self.page + 1) % len(self.data[self.current_key])
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        embed = self.data[self.current_key][self.page]
        embed.title = f"{self.titre}\n📂 {self.current_key}"
        embed.set_footer(text=f"Page {self.page+1}/{len(self.data[self.current_key])} • Decks triés par difficulté")
        await interaction.response.edit_message(embed=embed, view=self)

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

            # Récupération date tournoi depuis Supabase
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception:
                date_tournoi = "🗓️ à venir !"

            def make_pages(df_cat, couleur):
                # Trier par difficulté définie
                df_cat["DIFFICULTÉ"] = pd.Categorical(df_cat["DIFFICULTÉ"], categories=DIFFICULTE_ORDER, ordered=True)
                df_cat = df_cat.sort_values("DIFFICULTÉ")
                pages = []
                # 15 decks max par page
                for i in range(0, len(df_cat), 15):
                    chunk = df_cat.iloc[i:i+15]
                    texte = ""
                    for _, row in chunk.iterrows():
                        texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
                    if not texte:
                        texte = "Aucun deck."
                    embed = discord.Embed(description=texte, color=couleur)
                    pages.append(embed)
                return pages

            data_dict = {}
            for cat_name, df_cat in [("Libre", libres), ("Pris", pris)]:
                for diff in DIFFICULTE_ORDER:
                    df_diff = df_cat[df_cat["DIFFICULTÉ"] == diff]
                    key = f"{cat_name} {diff}"
                    pages = make_pages(df_diff, discord.Color.green() if cat_name == "Libre" else discord.Color.red())
                    if pages:
                        data_dict[key] = pages

            if not data_dict:
                await ctx.send("Aucun deck trouvé.")
                return

            titre_embed = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"
            view = TournoiView(data_dict, titre_embed)

            # Envoie le premier embed (première clé, première page)
            first_key = list(data_dict.keys())[0]
            first_embed = data_dict[first_key][0]
            first_embed.title = f"{titre_embed}\n📂 {first_key}"
            first_embed.set_footer(text=f"Page 1/{len(data_dict[first_key])} • Decks triés par difficulté")

            await ctx.send(embed=first_embed, view=view)

        except Exception:
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
