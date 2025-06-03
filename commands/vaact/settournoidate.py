# ────────────────────────────────────────────────────────────────────────────────
# 📌 settournoidate.py — Commande interactive !settournoidate
# Objectif : Permet à un admin de définir la date du tournoi avec menus déroulants
# Catégorie : VAACT
# Accès : Modérateur
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from discord.ui import View, Select
from datetime import datetime

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Vue interactive pour choisir la date du tournoi
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.selected = {
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
        }

        years = [str(y) for y in range(datetime.now().year, datetime.now().year + 3)]
        months = [str(m) for m in range(1, 13)]
        days = [str(d) for d in range(1, 32)]
        hours = [str(h) for h in range(0, 24)]

        self.year_select = Select(
            placeholder="Année",
            options=[discord.SelectOption(label=y, value=y) for y in years],
            custom_id="year_select"
        )
        self.month_select = Select(
            placeholder="Mois",
            options=[discord.SelectOption(label=m, value=m) for m in months],
            custom_id="month_select"
        )
        self.day_select = Select(
            placeholder="Jour",
            options=[discord.SelectOption(label=d, value=d) for d in days],
            custom_id="day_select"
        )
        self.hour_select = Select(
            placeholder="Heure (24h)",
            options=[discord.SelectOption(label=h, value=h) for h in hours],
            custom_id="hour_select"
        )

        self.year_select.callback = self.select_year
        self.month_select.callback = self.select_month
        self.day_select.callback = self.select_day
        self.hour_select.callback = self.select_hour

        self.add_item(self.year_select)
        self.add_item(self.month_select)
        self.add_item(self.day_select)
        self.add_item(self.hour_select)

    async def select_year(self, interaction: discord.Interaction):
        self.selected["year"] = int(self.year_select.values[0])
        await self.update_message(interaction)

    async def select_month(self, interaction: discord.Interaction):
        self.selected["month"] = int(self.month_select.values[0])
        await self.update_message(interaction)

    async def select_day(self, interaction: discord.Interaction):
        self.selected["day"] = int(self.day_select.values[0])
        await self.update_message(interaction)

    async def select_hour(self, interaction: discord.Interaction):
        self.selected["hour"] = int(self.hour_select.values[0])
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        y = self.selected["year"]
        m = self.selected["month"]
        d = self.selected["day"]
        h = self.selected["hour"]

        if None in (y, m, d, h):
            content = f"Date sélectionnée partiellement : {y or '?'}-{m or '?'}-{d or '?'} {h or '?'}h"
        else:
            try:
                dt = datetime(y, m, d, h)
                content = f"Date sélectionnée complète : {dt.strftime('%d/%m/%Y %Hh')}"
                # Ici tu peux enregistrer la date en base ou fichier si besoin
            except ValueError:
                content = "Date invalide, merci de corriger."

        await interaction.response.edit_message(content=content, view=self)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SetTournoiDate(commands.Cog):
    """
    Commande !settournoidate — Permet à un admin de définir la date du tournoi
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoidate",
        help="Permet à un admin de définir la date du tournoi.",
        description="Affiche un menu interactif pour choisir la date du prochain tournoi."
    )
    @commands.has_permissions(administrator=True)
    async def settournoidate(self, ctx: commands.Context):
        """Commande principale avec menus déroulants pour la date."""
        try:
            view = DateSelectView(self.bot)
            await ctx.send("🗓️ Choisis la date du prochain tournoi :", view=view)
        except Exception as e:
            print(f"[ERREUR settournoidate] {e}")
            await ctx.send("❌ Une erreur est survenue.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = SetTournoiDate(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
