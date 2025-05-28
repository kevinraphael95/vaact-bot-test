from discord.ext import commands

class TournoiAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="settournoi")
    @commands.has_permissions(administrator=True)
    async def settournoi(self, ctx, *, date_text: str):
        try:
            # 🔄 Met à jour la date dans Supabase (ligne avec id=1)
            result = supabase.table("tournoi_info").update({
                "prochaine_date": date_text
            }).eq("id", 1).execute()

            if result.status_code == 200:
                await ctx.send(f"📅 Nouvelle date enregistrée pour le tournoi : **{date_text}**")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")

        except Exception as e:
            print(f"[ERREUR SETTOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

# ────────────────────────────────────────────────────────────────
# 🔧 Chargement du Cog
# On définit dynamiquement la catégorie pour les systèmes de help personnalisés.
# ────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = settournoi(bot)

    # 🏷️ Attribution de la catégorie
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
