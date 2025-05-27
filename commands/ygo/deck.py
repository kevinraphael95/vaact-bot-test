import discord
import json
from discord.ext import commands
from discord.ui import View, Select
from discord import SelectOption, Embed
from pathlib import Path

with open(Path("data/deck_data.json"), encoding="utf-8") as f:
    DECK_DATA = json.load(f)

class Deck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deck", help="Choisis une saison puis un duelliste pour voir son deck.")
    async def deck(self, ctx):
        class SaisonSelect(Select):
            def __init__(self):
                options = [SelectOption(label=saison, value=saison) for saison in DECK_DATA]
                super().__init__(placeholder="📅 Choisis une saison", options=options)

            async def callback(self, interaction: discord.Interaction):
                saison = self.values[0]
                duellistes = DECK_DATA[saison]

                class DuellisteSelect(Select):
                    def __init__(self):
                        options = [SelectOption(label=nom, value=nom) for nom in duellistes]
                        super().__init__(placeholder=f"🎭 Duellistes de {saison}", options=options)

                    async def callback(self2, interaction2: discord.Interaction):
                        nom = self2.values[0]
                        description = duellistes[nom]
                        embed = Embed(
                            title=f"🃏 Deck de {nom}",
                            description=description,
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text=f"Saison : {saison}")
                        await interaction2.response.send_message(embed=embed, ephemeral=True)

                view = View()
                view.add_item(DuellisteSelect())
                await interaction.response.send_message(
                    content=f"🎴 Sélectionne un duelliste pour la saison **{saison}** :",
                    view=view,
                    ephemeral=True
                )

        view = View()
        view.add_item(SaisonSelect())
        await ctx.send("📚 Sélectionne une saison du tournoi Yu-Gi-Oh VAACT :", view=view)

async def setup(bot):
    await bot.add_cog(Deck(bot))
