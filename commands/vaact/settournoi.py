# ────────────────────────────────────────────────────────────────────────────────
# 📌 tournoi_admin.py — Commande !settournoi
# Objectif : Définir la prochaine date du tournoi dans Supabase
# Catégorie : 🧠 VAACT
# Accès : Administrateur uniquement
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
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
    """
    🔒 Commandes administratives liées aux tournois.
    ➕ Exclusivement réservées aux administrateurs Discord.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoi",
        help="📅 Définit la date du prochain tournoi.",
        description=(
            "Commande admin pour mettre à jour la date du tournoi dans Supabase.\n\n"
            "📌 Exemple : `!settournoi`\n"
            "🔐 Réservé aux administrateurs."
        )
    )
    @commands.has_permissions(administrator=True)
    async def settournoi(self, ctx: commands.Context):
        """
        🛠️ Met à jour la date du tournoi dans Supabase (ligne avec id=1).
        """
        view = DateSelectView(ctx)
        await ctx.send("📅 Sélectionne la date et l'heure du prochain tournoi :", view=view)
        await view.wait()

        if view.value is None:
            await ctx.send("⏰ Temps écoulé ou aucune sélection effectuée.")
            return

        try:
            result = supabase.table("tournoi_info").update({
                "prochaine_date": view.value
            }).eq("id", 1).execute()

            if result.status_code == 200:
                await ctx.send(f"✅ Nouvelle date enregistrée pour le tournoi : `{view.value}`")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")
        except Exception as e:
            print(f"[ERREUR SETTOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

    def cog_load(self):
        self.settournoi.category = "VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 📅 Vue interactive pour la sélection de la date
# ────────────────────────────────────────────────────────────────────────────────
class DateSelectView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.value = None

        jours = [discord.SelectOption(label=str(i)) for i in range(1, 32)]
        mois = [discord.SelectOption(label=str(i)) for i in range(1, 13)]
        annees = [discord.SelectOption(label=str(i)) for i in range(2025, 2031)]
        heures = [discord.SelectOption(label=str(i).zfill(2)) for i in range(0, 24)]
        minutes = [discord.SelectOption(label=str(i).zfill(2)) for i in (0, 15, 30, 45)]

        self.jour_select = discord.ui.Select(placeholder="Jour", options=jours, custom_id="jour")
        self.mois_select = discord.ui.Select(placeholder="Mois", options=mois, custom_id="mois")
        self.annee_select = discord.ui.Select(placeholder="Année", options=annees, custom_id="annee")
        self.heure_select = discord.ui.Select(placeholder="Heure", options=heures, custom_id="heure")
        self.minute_select = discord.ui.Select(placeholder="Minute", options=minutes, custom_id="minute")

        self.add_item(self.jour_select)
        self.add_item(self.mois_select)
        self.add_item(self.annee_select)
        self.add_item(self.heure_select)
        self.add_item(self.minute_select)

        self.add_item(ValiderButton(self))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

class ValiderButton(discord.ui.Button):
    def __init__(self, view: DateSelectView):
        super().__init__(label="Valider", style=discord.ButtonStyle.green)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        try:
            jour = int(self.view.jour_select.values[0])
            mois = int(self.view.mois_select.values[0])
            annee = int(self.view.annee_select.values[0])
            heure = int(self.view.heure_select.values[0])
            minute = int(self.view.minute_select.values[0])

            dt = datetime(annee, mois, jour, heure, minute, tzinfo=pytz.UTC)
            self.view.value = dt.isoformat()

            await interaction.response.send_message(
                f"✅ Date définie : **{dt.strftime('%d/%m/%Y à %Hh%M')} UTC**", ephemeral=True
            )
            self.view.stop()
        except Exception as e:
            print(f"[ERREUR DateSelectView] {e}")
            await interaction.response.send_message("❌ Erreur dans la sélection. Recommence.", ephemeral=True)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TournoiAdmin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiAdmin (catégorie = VAACT)")
