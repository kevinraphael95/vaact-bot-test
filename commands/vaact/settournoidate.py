# ────────────────────────────────────────────────────────────────────────────────
# 📌 settournoidate.py — Commande interactive !settournoidate
# Objectif : Permet aux admins de modifier la date du prochain tournoi via menus déroulants
# Catégorie : VAACT
# Accès : Modérateur (admin uniquement)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from discord.ui import View, Select
import aiohttp
import os
from datetime import datetime

# ────────────────────────────────────────────────────────────────────────────────
# 🔐 Configuration Supabase
# ────────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Menus déroulants pour sélectionner la date et l'heure
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.selected = {
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
            "minute": None
        }
        self.add_item(YearSelect(self))
        self.add_item(MonthSelect(self))
        self.add_item(DaySelect(self))
        self.add_item(HourSelect(self))
        self.add_item(MinuteSelect(self))

    async def update_date(self, interaction: discord.Interaction):
        if all(self.selected.values()):
            try:
                dt = datetime(
                    int(self.selected["year"]),
                    int(self.selected["month"]),
                    int(self.selected["day"]),
                    int(self.selected["hour"]),
                    int(self.selected["minute"])
                )
                if dt < datetime.now():
                    await interaction.response.send_message("❌ La date ne peut pas être dans le passé.", ephemeral=True)
                    return

                iso_date = dt.isoformat()

                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                }

                async with aiohttp.ClientSession() as session:
                    url = f"{SUPABASE_URL}/rest/v1/tournoi_info"
                    # Ici on suppose qu'on insert ou met à jour la date.
                    # Pour mettre à jour proprement il faudrait récupérer l'id de la ligne,
                    # mais on fait ici un simple insert, à adapter si nécessaire.
                    resp = await session.post(url, headers=headers, json={"prochaine_date": iso_date})
                    if resp.status not in (200, 201):
                        await interaction.response.send_message("❌ Erreur lors de l'enregistrement dans Supabase.", ephemeral=True)
                        return

                await interaction.response.edit_message(
                    content=f"✅ Nouvelle date enregistrée : **{dt.strftime('%d %B %Y à %Hh%M')}**",
                    view=None
                )
                self.stop()
            except Exception as e:
                print("[Erreur update_date]", e)
                await interaction.response.send_message("❌ Erreur lors de la validation de la date.", ephemeral=True)

class YearSelect(Select):
    def __init__(self, parent: DateSelectView):
        self.parent = parent
        current_year = datetime.now().year
        options = [discord.SelectOption(label=str(y), value=str(y)) for y in range(current_year, current_year + 3)]
        super().__init__(placeholder="Année", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected["year"] = self.values[0]
        await self.parent.update_date(interaction)

class MonthSelect(Select):
    def __init__(self, parent: DateSelectView):
        self.parent = parent
        options = [discord.SelectOption(label=f"{m:02}", value=str(m)) for m in range(1, 13)]
        super().__init__(placeholder="Mois", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected["month"] = self.values[0]
        await self.parent.update_date(interaction)

class DaySelect(Select):
    def __init__(self, parent: DateSelectView):
        self.parent = parent
        options = [discord.SelectOption(label=f"{d:02}", value=str(d)) for d in range(1, 32)]
        super().__init__(placeholder="Jour", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected["day"] = self.values[0]
        await self.parent.update_date(interaction)

class HourSelect(Select):
    def __init__(self, parent: DateSelectView):
        self.parent = parent
        options = [discord.SelectOption(label=f"{h:02}", value=str(h)) for h in range(0, 24)]
        super().__init__(placeholder="Heure", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected["hour"] = self.values[0]
        await self.parent.update_date(interaction)

class MinuteSelect(Select):
    def __init__(self, parent: DateSelectView):
        self.parent = parent
        # Intervalles de 5 minutes pour simplifier la sélection
        options = [discord.SelectOption(label=f"{m:02}", value=str(m)) for m in range(0, 60, 5)]
        super().__init__(placeholder="Minute", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected["minute"] = self.values[0]
        await self.parent.update_date(interaction)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SetTournoiDate(commands.Cog):
    """
    Commande !settournoidate — Permet aux admins de modifier la date du tournoi via menus déroulants.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoidate",
        help="🛠️ Modifie la date du prochain tournoi (admin uniquement).",
        description="Commande réservée aux administrateurs pour définir la date du tournoi."
    )
    @commands.has_permissions(administrator=True)
    async def settournoidate(self, ctx: commands.Context):
        """Commande principale !settournoidate."""
        view = DateSelectView(ctx)
        await ctx.send("🗓️ Choisis la nouvelle date du tournoi via les menus déroulants :", view=view)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = SetTournoiDate(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
