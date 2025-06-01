import discord
from discord.ext import commands
import pandas as pd
import math

class TournoiView(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.page = 0

    async def update_message(self, interaction):
        for child in self.children:
            child.disabled = False

        if self.page == 0:
            self.previous_button.disabled = True
        if self.page == len(self.pages) - 1:
            self.next_button.disabled = True

        await interaction.response.edit_message(embed=self.pages[self.page], view=self)

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        await self.update_message(interaction)

@commands.command()
async def tournoi(ctx, statut="libres"):
    url = "https://docs.google.com/spreadsheets/d/1EP_UrCS7rBBto2P8XGWxT67Qftjdc72YDqPNW0H5psY/export?format=csv&gid=0"
    df = pd.read_csv(url)

    df["Statut"] = df["Statut"].fillna("")
    is_libre = statut.lower() == "libres"
    df = df[df["Statut"].str.lower() == "libre"] if is_libre else df[df["Statut"].str.lower() != "libre"]

    df["Difficulté"] = df["Difficulté"].fillna("3/3")
    df = df.sort_values(by="Difficulté")

    decks = [f'**{row["Nom"]}** ({row["Difficulté"]}) - {row["Statut"]}' for _, row in df.iterrows()]
    decks_per_page = 10
    total_pages = math.ceil(len(decks) / decks_per_page)

    pages = []
    for i in range(total_pages):
        chunk = decks[i * decks_per_page : (i + 1) * decks_per_page]
        embed = discord.Embed(
            title="Tournoi à venir",
            description="\n".join(chunk),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {i+1}/{total_pages}")
        pages.append(embed)

    view = TournoiView(pages)
    await ctx.send(embed=pages[0], view=view)

# Ajoutez cette commande à votre bot :
# bot.add_command(tournoi)
