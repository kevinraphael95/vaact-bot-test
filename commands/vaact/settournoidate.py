# ────────────────────────────────────────────────────────────────────────────────
# 📌 settournoidate.py — Commande interactive !settournoidate
# Objectif : Permet à un admin de définir la date du tournoi avec menus déroulants
# Catégorie : VAACT
# Accès : Modérateur (admin)
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from datetime import datetime

class DatePickerView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.selection = {
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
        }

        now = datetime.utcnow()

        years = [str(y) for y in range(now.year, now.year + 3)]
        months = [str(m) for m in range(1, 13)]
        days = [str(d) for d in range(1, 32)]
        hours = [str(h) for h in range(0, 24)]

        self.year_select = Select(
            placeholder="Année",
            options=[discord.SelectOption(label=y, value=y) for y in years],
            row=0
        )
        self.month_select = Select(
            placeholder="Mois",
            options=[discord.SelectOption(label=m, value=m) for m in months],
            row=1
        )
        self.day_select = Select(
            placeholder="Jour",
            options=[discord.SelectOption(label=d, value=d) for d in days],
            row=2
        )
        self.hour_select = Select(
            placeholder="Heure (0-23)",
            options=[discord.SelectOption(label=h, value=h) for h in hours],
            row=3
        )

        self.confirm_button = Button(label="Confirmer", style=discord.ButtonStyle.green, disabled=True, row=4)

        self.year_select.callback = self.on_year_select
        self.month_select.callback = self.on_month_select
        self.day_select.callback = self.on_day_select
        self.hour_select.callback = self.on_hour_select
        self.confirm_button.callback = self.on_confirm

        self.add_item(self.year_select)
        self.add_item(self.month_select)
        self.add_item(self.day_select)
        self.add_item(self.hour_select)
        self.add_item(self.confirm_button)

    def is_date_valid(self):
        y = self.selection["year"]
        m = self.selection["month"]
        d = self.selection["day"]
        h = self.selection["hour"]
        if None in (y,m,d,h):
            return False
        try:
            datetime(int(y), int(m), int(d), int(h))
            return True
        except ValueError:
            return False

    def get_date_str(self):
        y,m,d,h = self.selection["year"], self.selection["month"], self.selection["day"], self.selection["hour"]
        if None in (y,m,d,h):
            return "Date incomplète"
        try:
            dt = datetime(int(y), int(m), int(d), int(h))
            return dt.strftime("%d/%m/%Y %Hh")
        except ValueError:
            return "Date invalide"

    async def update_message(self, interaction):
        valid = self.is_date_valid()
        self.confirm_button.disabled = not valid
        content = f"Date sélectionnée : **{self.get_date_str()}**"
        await interaction.response.edit_message(content=content, view=self)

    async def on_year_select(self, interaction: discord.Interaction):
        self.selection["year"] = self.year_select.values[0]
        await self.update_message(interaction)

    async def on_month_select(self, interaction: discord.Interaction):
        self.selection["month"] = self.month_select.values[0]
        await self.update_message(interaction)

    async def on_day_select(self, interaction: discord.Interaction):
        self.selection["day"] = self.day_select.values[0]
        await self.update_message(interaction)

    async def on_hour_select(self, interaction: discord.Interaction):
        self.selection["hour"] = self.hour_select.values[0]
        await self.update_message(interaction)

    async def on_confirm(self, interaction: discord.Interaction):
        if not self.is_date_valid():
            await interaction.response.send_message("Date invalide ou incomplète.", ephemeral=True)
            return

        y,m,d,h = map(int, [self.selection["year"], self.selection["month"], self.selection["day"], self.selection["hour"]])
        dt = datetime(y, m, d, h)
        iso_str = dt.isoformat() + "Z"  # ISO 8601 UTC format

        # Ici tu peux faire ce que tu veux avec iso_str, par exemple enregistrer en base

        await interaction.response.edit_message(
            content=f"✅ Date du tournoi définie : `{iso_str}`",
            view=None
        )
        self.stop()

class SetTournoiDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="settournoidate")
    @commands.has_permissions(administrator=True)
    async def settournoidate(self, ctx: commands.Context):
        """Commande admin pour choisir la date du tournoi via menus déroulants."""
        view = DatePickerView()
        await ctx.send("🗓️ Sélectionne la date et l'heure du tournoi :", view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetTournoiDate(bot))
