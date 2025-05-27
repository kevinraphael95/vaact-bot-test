import discord
import json
from discord.ext import commands
from discord.ui import View, Select
from discord import SelectOption, Embed
from datetime import datetime
import pytz
from pathlib import Path
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

with open(Path("data/deck_data.json"), encoding="utf-8") as f:
    DECK_DATA = json.load(f)

class VAACT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deck", help="Choisis une saison puis un duelliste pour voir son deck.")
    async def deck(self, ctx):
        class SaisonSelect(Select):
            def __init__(self):
                options = [SelectOption(label=s, value=s) for s in DECK_DATA.keys()]
                super().__init__(placeholder="📅 Choisis une saison", options=options)

            async def callback(self, interaction):
                saison = self.values[0]
                duellistes = DECK_DATA[saison]

                class DuellisteSelect(Select):
                    def __init__(self):
                        options = [SelectOption(label=n, value=n) for n in duellistes]
                        super().__init__(placeholder=f"🎭 Duellistes de {saison}", options=options)

                    async def callback(self2, interaction2):
                        nom = self2.values[0]
                        description = duellistes[nom]
                        embed = Embed(title=f"🃏 Deck de {nom}", description=description, color=discord.Color.blue())
                        embed.set_footer(text=f"Saison sélectionnée : {saison}")
                        await interaction2.response.send_message(embed=embed, ephemeral=True)

                view = View()
                view.add_item(DuellisteSelect())
                await interaction.response.send_message(
                    content=f"🎴 Sélectionne un duelliste pour la saison **{saison}** :", view=view, ephemeral=True)

        view = View()
        view.add
