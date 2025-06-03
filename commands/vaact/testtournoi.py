# ────────────────────────────────────────────────────────────────────────────────
# 📌 tournoi_admin.py — Commande !testtournoi
# Objectif : Définir la prochaine date du tournoi dans Supabase
# Catégorie : 🧠 VAACT
# Accès : Administrateur uniquement
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
from datetime import datetime
import pytz
from supabase_client import supabase

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class TournoiAdmin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="testtournoi",
        help="📅 Définit la date du prochain tournoi.",
        description="Commande admin pour mettre à jour la date du tournoi dans Supabase (heure fixée à 19h UTC)."
    )
    @commands.has_permissions(administrator=True)
    async def testtournoi(self, ctx: commands.Context):
        view = DateSelectView(ctx)
        await ctx.send("📅 Choisis la date du prochain tournoi (heure fixée à 19h UTC) :", view=view)
        await view.wait()

        if view.value is None:
            await ctx.send("⏰ Temps écoulé ou aucune sélection effectuée.")
            return

        try:
            result = supabase.table("tournoi_info").update({
                "prochaine_date": view.value
            }).eq("id", 1).execute()

            if result.status_code == 200:
                date_format = datetime.fromisoformat(view.value).strftime('%d/%m/%Y à 19h00 UTC')
                await ctx.send(f"✅ Nouvelle date enregistrée pour le tournoi : **{date_format}**")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")
        except Exception as e:
            print(f"[ERREUR testtournoi] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

    def cog_load(self):
        self.testtournoi.category = "VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 📅 Vue interactive pour la sélection de la date (jour, mois, année)
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.value = None

        self.jour = discord.ui.Select(
            placeholder="Jour", 
            options=[discord.SelectOption(label=str(i)) for i in range(1, 32)]
        )
        self.mois = discord.ui.Select(
            placeholder="Mois", 
            options=[discord.SelectOption(label=str(i)) for i in range(1, 13)]
        )
        self.annee = discord.ui.Select(
            placeholder="Année", 
            options=[discord.SelectOption(label=str(i)) for i in range(datetime.now().year, datetime.now().year + 6)]
        )

        self.jour.callback = self.on_select
        self.mois.callback = self.on_select
        self.annee.callback = self.on_select

        self.add_item(self.jour)
        self.add_item(self.mois)
        self.add_item(self.annee)
        self.add_item(ValiderButton(self))

    async def on_select(self, interaction: discord.Interaction):
        await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

class ValiderButton(discord.ui.Button):
    def __init__(self, view: DateSelectView):
        super().__init__(label="Valider", style=discord.ButtonStyle.green)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        try:
            jour = int(self.view.jour.values[0])
            mois = int(self.view.mois.values[0])
            annee = int(self.view.annee.values[0])

            # Heure fixée à 19h UTC
            dt = datetime(annee, mois, jour, 19, 0, tzinfo=pytz.UTC)
            self.view.value = dt.isoformat()

            await interaction.response.send_message(
                f"✅ Date définie : **{dt.strftime('%d/%m/%Y à 19h00')} UTC**", ephemeral=True
            )
            self.view.stop()

        except Exception as e:
            print(f"[ERREUR DateSelectView] {e}")
            await interaction.response.send_message("❌ Erreur dans la sélection. Recommence.", ephemeral=True)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TestTournoiAdmin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiAdmin (catégorie = VAACT)")
