import discord
from discord.ext import commands
from discord.ui import View, Button
import pandas as pd
import aiohttp
import io
import os

class PaginationView(View):
    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.current = 0
        self.message = None
        self.update_buttons()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    def update_buttons(self):
        self.clear_items()
        self.add_item(Button(label="⏮️", style=discord.ButtonStyle.secondary, disabled=self.current == 0, custom_id="first"))
        self.add_item(Button(label="⬅️", style=discord.ButtonStyle.secondary, disabled=self.current == 0, custom_id="prev"))
        self.add_item(Button(label="➡️", style=discord.ButtonStyle.secondary, disabled=self.current == len(self.pages) - 1, custom_id="next"))
        self.add_item(Button(label="⏭️", style=discord.ButtonStyle.secondary, disabled=self.current == len(self.pages) - 1, custom_id="last"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # tu peux restreindre ici par utilisateur si tu veux

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="first")
    async def first(self, interaction: discord.Interaction, button: Button):
        self.current = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def prev(self, interaction: discord.Interaction, button: Button):
        if self.current > 0:
            self.current -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: Button):
        if self.current < len(self.pages) - 1:
            self.current += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="last")
    async def last(self, interaction: discord.Interaction, button: Button):
        self.current = len(self.pages) - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)


def noms_par_difficulte(df, pris_col, pris=False):
    return {
        "1/3": df[(df["DIFFICULTE"] == "1/3") & (df[pris_col] == pris)]["PERSONNAGE"].tolist(),
        "2/3": df[(df["DIFFICULTE"] == "2/3") & (df[pris_col] == pris)]["PERSONNAGE"].tolist(),
        "3/3": df[(df["DIFFICULTE"] == "3/3") & (df[pris_col] == pris)]["PERSONNAGE"].tolist(),
    }


def creer_pages(noms_dict, titre_base):
    pages = []
    for difficulte, noms in noms_dict.items():
        description = "\n".join(noms) if noms else "_Aucun deck_"
        embed = discord.Embed(
            title=f"{titre_base} – Difficulté {difficulte}",
            description=description,
            color=discord.Color.blue()
        )
        pages.append(embed)
    return pages


class Tournoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tournoi(self, ctx):
        url = os.getenv("SHEET_CSV_URL")  # le lien vers le CSV Render
        if not url:
            return await ctx.send("URL du CSV non définie.")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        df.columns = df.columns.str.strip()  # Nettoie les colonnes
        df.fillna("", inplace=True)

        pris_col = next((col for col in df.columns if col.lower().strip() == "pris ?"), None)
        if not pris_col:
            return await ctx.send("Colonne 'PRIS ?' introuvable.")

        df[pris_col] = df[pris_col].astype(str).str.lower().isin(["true", "✅"])

        libres = noms_par_difficulte(df, pris_col, pris=False)
        pris = noms_par_difficulte(df, pris_col, pris=True)

        pages = (
            creer_pages(libres, "Decks Libres") +
            creer_pages(pris, "Decks Pris")
        )

        view = PaginationView(pages)
        view.message = await ctx.send(embed=pages[0], view=view)

async def setup(bot):
    await bot.add_cog(Tournoi(bot))
