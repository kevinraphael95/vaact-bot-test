# tournoi.py

import discord
from discord.ext import commands
import pandas as pd
import aiohttp, io, ssl, os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1EP_UrCS7rBBto2P8XGWxT67Qftjdc72YDqPNW0H5psY/export?format=csv&gid=0"

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
        embed.set_footer(text=f"Page {self.page + 1}/{len(self.pages)}")
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
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tournoi", help="Affiche la date et les decks (pris/libres)")
    async def tournoi(self, ctx):
        try:
            # 1. Date du tournoi
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data else "À venir"
            except:
                date_tournoi = "À venir"

            # 2. Charger le CSV
            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers("DEFAULT:@SECLEVEL=1")
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    csv_text = (await resp.read()).decode("utf-8")
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
            df["DIFFICULTÉ"] = df["DIFFICULTÉ"].fillna("—")
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")

            pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

            # 3. Embed decks libres
            difficulte_order = ["1/3", "2/3", "3/3"]
            libres["DIFFICULTÉ"] = pd.Categorical(libres["DIFFICULTÉ"], categories=difficulte_order, ordered=True)
            libres_sorted = libres.sort_values("DIFFICULTÉ")

            pages = []
            chunk_size = 15
            for i in range(0, len(libres_sorted), chunk_size):
                chunk = libres_sorted.iloc[i:i+chunk_size]
                description = "\n".join(f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})"
                                        for _, row in chunk.iterrows())
                embed = discord.Embed(description=description, color=discord.Color.green())
                pages.append(embed)

            titre = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"
            view = TournoiView(pages, titre)

            # 4. Embed decks pris
            pris_embed = None
            if not pris.empty:
                texte_pris = "\n".join(f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*" for _, row in pris.iterrows())
                pris_embed = discord.Embed(title="🔒 Decks déjà pris", description=texte_pris[:4000], color=discord.Color.red())

            # 5. Envoi des messages
            if pris_embed:
                await ctx.send(embed=pris_embed)
            await ctx.send(embed=pages[0], view=view)

        except Exception as e:
            await ctx.send("❌ Une erreur est survenue.")
            raise e  # Pour que tu vois les erreurs dans la console

async def setup(bot):
    await bot.add_cog(TournoiCommand(bot))
