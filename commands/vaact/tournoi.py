import os
import discord
from discord.ext import commands
from discord.ui import View, Button
import pandas as pd
import math

SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

class PaginationView(View):
    def __init__(self, pages, initial_page=0):
        super().__init__(timeout=180)
        self.pages = pages
        self.current_page = initial_page

        self.prev_button = Button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="➡️ Suivant", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.update_buttons()

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_message(interaction)

    async def update_message(self, interaction):
        embed = self.pages[self.current_page]
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

class Tournoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tournoi")
    async def tournoi(self, ctx):
        try:
            df = pd.read_csv(SHEET_CSV_URL)

            # Supposons que la date du tournoi est dans la colonne DateTournoi au format "YYYY-MM-DD"
            if "DateTournoi" in df.columns:
                date_tournoi = df["DateTournoi"].iloc[0]
            else:
                date_tournoi = "Date inconnue"

            # Trier les decks par difficulté (1, 2, 3)
            pages = []
            decks_per_page = 10  # nombre de decks par page pour ne pas saturer

            for diff in sorted(df["Difficulté"].unique()):
                # Filtrer decks libres par difficulté
                libres = df[(df["Status"] == "Libre") & (df["Difficulté"] == diff)]["Deck"].tolist()
                # Découpage en pages
                for i in range(math.ceil(len(libres) / decks_per_page)):
                    chunk = libres[i*decks_per_page:(i+1)*decks_per_page]
                    embed = discord.Embed(
                        title=f"Tournoi du {date_tournoi} — Decks Libres (Difficulté {diff})",
                        description="\n".join(f"• {deck}" for deck in chunk),
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Page {i+1} / {math.ceil(len(libres) / decks_per_page)}")
                    pages.append(embed)

                # Même chose pour les decks pris
                pris = df[(df["Status"] == "Pris") & (df["Difficulté"] == diff)]["Deck"].tolist()
                for i in range(math.ceil(len(pris) / decks_per_page)):
                    chunk = pris[i*decks_per_page:(i+1)*decks_per_page]
                    embed = discord.Embed(
                        title=f"Tournoi du {date_tournoi} — Decks Pris (Difficulté {diff})",
                        description="\n".join(f"• {deck}" for deck in chunk),
                        color=discord.Color.red()
                    )
                    embed.set_footer(text=f"Page {i+1} / {math.ceil(len(pris) / decks_per_page)}")
                    pages.append(embed)

            if not pages:
                await ctx.send("Aucun deck trouvé dans le CSV.")
                return

            view = PaginationView(pages)
            await ctx.send(embed=pages[0], view=view)

        except Exception as e:
            print("[ERREUR TOURNOI]", e)
            await ctx.send("❌ Une erreur est survenue lors de la récupération des données du tournoi.")

async def setup(bot):
    await bot.add_cog(Tournoi(bot))
