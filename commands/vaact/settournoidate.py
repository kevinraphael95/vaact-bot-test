# ────────────────────────────────────────────────────────────────────────────────
# 📌 settournoidate.py — Commande interactive !settournoidate
# Objectif : Modifier la date du tournoi enregistrée sur Supabase via menus déroulants
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
import os
from supabase import create_client, Client  # pip install supabase

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Configuration Supabase
# ────────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Vue interactive pour sélectionner la date
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(View):
    """Vue pour sélectionner année, mois, jour et heure via menus déroulants."""

    def __init__(self, bot, ctx):
        super().__init__(timeout=180)
        self.bot = bot
        self.ctx = ctx
        self.selected = {"year": None, "month": None, "day": None, "hour": None}

        now = datetime.now()
        years = [str(y) for y in range(now.year, now.year + 3)]
        months = [str(m) for m in range(1, 13)]
        days = [str(d) for d in range(1, 32)]
        hours = [str(h) for h in range(0, 24)]

        self.year_select = Select(
            placeholder="Année",
            options=[discord.SelectOption(label=y, value=y) for y in years],
            custom_id="year"
        )
        self.month_select = Select(
            placeholder="Mois",
            options=[discord.SelectOption(label=m, value=m) for m in months],
            custom_id="month"
        )
        self.day_select = Select(
            placeholder="Jour",
            options=[discord.SelectOption(label=d, value=d) for d in days],
            custom_id="day"
        )
        self.hour_select = Select(
            placeholder="Heure (24h)",
            options=[discord.SelectOption(label=h, value=h) for h in hours],
            custom_id="hour"
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
        y, m, d, h = (self.selected[k] for k in ("year", "month", "day", "hour"))

        if None in (y, m, d, h):
            await interaction.response.edit_message(
                content=f"Date sélectionnée partiellement : {y or '?'}-{m or '?'}-{d or '?'} {h or '?'}h",
                view=self
            )
            return

        # Validation de la date
        try:
            dt = datetime(y, m, d, h)
        except ValueError:
            await interaction.response.edit_message(
                content="❌ Date invalide, merci de corriger la sélection.",
                view=self
            )
            return

        # Mise à jour dans Supabase (id = 1 pour le tournoi unique)
        try:
            response = supabase.table("tournoi_info").update({"prochaine_date": dt.isoformat()}).eq("id", 1).execute()
            # response est un dict, pas un objet HTTP
            if response.get("status_code") in (200, 204):
                await interaction.response.edit_message(
                    content=f"✅ Date du tournoi mise à jour avec succès : {dt.strftime('%d/%m/%Y %Hh')}",
                    view=None
                )
            else:
                await interaction.response.edit_message(
                    content=f"❌ Erreur lors de la mise à jour en base (code {response.get('status_code')})",
                    view=self
                )
        except Exception as e:
            print(f"[ERREUR supabase update] {e}")
            await interaction.response.edit_message(
                content="❌ Une erreur est survenue lors de la mise à jour en base.",
                view=self
            )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SetTournoiDate(commands.Cog):
    """
    Commande !settournoidate — Permet à un modérateur de définir la date du tournoi via menus déroulants
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoidate",
        help="Définir la date du tournoi (admin).",
        description="Affiche un menu interactif pour choisir la date du prochain tournoi."
    )
    @commands.has_permissions(administrator=True)
    async def settournoidate(self, ctx: commands.Context):
        """Commande principale avec menus déroulants pour la date."""
        try:
            view = DateSelectView(self.bot, ctx)
            await ctx.send("🗓️ Choisis la date du prochain tournoi :", view=view)
        except Exception as e:
            print(f"[ERREUR settournoidate] {e}")
            await ctx.send(f"❌ Une erreur est survenue : `{e}`")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = SetTournoiDate(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
