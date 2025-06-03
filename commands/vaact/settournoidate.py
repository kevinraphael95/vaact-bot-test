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
from discord.ui import View, Select, Button
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
# 🎛️ UI — Vue interactive pour modifier uniquement l’heure
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=180)
        self.bot = bot
        self.ctx = ctx
        self.selected_hour = None

        hours = [str(h) for h in range(24)]
        self.hour_select = Select(
            placeholder="Heure (24h)",
            options=[discord.SelectOption(label=h, value=h) for h in hours],
            custom_id="hour"
        )
        self.hour_select.callback = self.select_hour
        self.add_item(self.hour_select)

        self.validate_button = Button(label="Valider", style=discord.ButtonStyle.green, disabled=True)
        self.validate_button.callback = self.validate
        self.add_item(self.validate_button)

        self.clear_button = Button(label="Tout supprimer", style=discord.ButtonStyle.red)
        self.clear_button.callback = self.clear
        self.add_item(self.clear_button)

    async def select_hour(self, interaction: discord.Interaction):
        self.selected_hour = int(self.hour_select.values[0])
        self.validate_button.disabled = False  # Active le bouton valider dès qu’on choisit une heure
        await interaction.response.edit_message(view=self)

    async def validate(self, interaction: discord.Interaction):
        if self.selected_hour is None:
            await interaction.response.send_message("❌ Aucune heure sélectionnée.", ephemeral=True)
            return

        # Récupérer la date actuelle pour garder jour, mois, année inchangés
        now = datetime.now()
        new_date = datetime(now.year, now.month, now.day, self.selected_hour)

        try:
            response = supabase.table("tournoi_info").update({"prochaine_date": new_date.isoformat()}).eq("id", 1).execute()
            if response.get("status_code") in (200, 204):
                await interaction.response.edit_message(
                    content=f"✅ Heure du tournoi mise à jour avec succès : {self.selected_hour}h",
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

    async def clear(self, interaction: discord.Interaction):
        self.selected_hour = None
        self.hour_select.values.clear()
        self.validate_button.disabled = True
        await interaction.response.edit_message(
            content="Sélection réinitialisée.",
            view=self
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SetTournoiDate(commands.Cog):
    """
    Commande !settournoidate — Permet à un modérateur de définir l'heure du tournoi via menu déroulant
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoidate",
        help="Définir l'heure du tournoi (admin).",
        description="Affiche un menu interactif pour choisir l'heure du prochain tournoi."
    )
    @commands.has_permissions(administrator=True)
    async def settournoidate(self, ctx: commands.Context):
        try:
            view = DateSelectView(self.bot, ctx)
            await ctx.send("🕒 Choisis l'heure du prochain tournoi :", view=view)
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
