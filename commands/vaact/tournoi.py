import discord
from discord.ext import commands
from discord.ui import View, Button
import pandas as pd
import os
import aiohttp

class PaginatorView(View):
    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0
        self.message = None

        self.prev_button = Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="➡️", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def prev_page(self, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)


class Tournoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tournoi(self, ctx):
        url = os.getenv("SHEET_CSV_URL")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = await resp.read()

        df = pd.read_csv(pd.compat.StringIO(content.decode("utf-8")))

        # Nettoyage des colonnes
        df.columns = df.columns.str.strip().str.replace('\xa0', ' ', regex=False).str.upper()
        pris_col = [col for col in df.columns if "PRIS" in col][0]

        df[pris_col] = df[pris_col].fillna("").astype(str).str.lower()
        df["DIFFICULTE"] = df["DIFFICULTE"].astype(str).str.strip()

        # Séparer les decks libres et pris
        libres = df[df[pris_col].isin(["false", "", "non", "❌"])]
        pris = df[df[pris_col].isin(["true", "oui", "✅"])]

        # Fonction pour grouper les personnages par difficulté
        def decks_par_difficulte(dataframe):
            groupes = {}
            for niveau in ["1/3", "2/3", "3/3"]:
                persos = dataframe[dataframe["DIFFICULTE"] == niveau]["PERSONNAGE"].dropna().tolist()
                groupes[niveau] = persos
            return groupes

        pages = []

        # Pages pour decks libres
        libres_groupes = decks_par_difficulte(libres)
        for niveau in ["1/3", "2/3", "3/3"]:
            description = "\n".join(libres_groupes[niveau]) or "Aucun"
            embed = discord.Embed(title=f"Decks disponibles - Difficulté {niveau}", description=description, color=0x00ff00)
            pages.append(embed)

        # Pages pour decks pris
        pris_groupes = decks_par_difficulte(pris)
        for niveau in ["1/3", "2/3", "3/3"]:
            description = "\n".join(pris_groupes[niveau]) or "Aucun"
            embed = discord.Embed(title=f"Decks pris - Difficulté {niveau}", description=description, color=0xff0000)
            pages.append(embed)

        view = PaginatorView(pages)
        message = await ctx.send(embed=pages[0], view=view)
        view.message = message


async def setup(bot):
    await bot.add_cog(Tournoi(bot))
