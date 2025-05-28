import discord
from discord.ext import commands
from supabase_client import supabase

class Streak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────
    # 🔥 Commande !streak — Affiche la série de bonnes réponses
    # ──────────────────────────────────────────────────────────────
    @commands.command(name="streak", aliases=["qs"], help="Affiche ta série de bonnes réponses.")
    async def streak(self, ctx):
        user_id = str(ctx.author.id)

        try:
            # Récupère la série de l'utilisateur depuis Supabase
            response = supabase.table("ygo_streaks") \
                .select("current_streak", "best_streak") \
                .eq("user_id", user_id) \
                .execute()

            if response.data:
                # Données trouvées pour l'utilisateur
                streak = response.data[0]
                current = streak.get("current_streak", 0)
                best = streak.get("best_streak", 0)

                await ctx.send(
                    f"🔥 **{ctx.author.display_name}**, ta série actuelle est de **{current}** 🔁\n"
                    f"🏆 Ton record absolu est de **{best}** bonnes réponses consécutives !"
                )
            else:
                # Aucun historique de série trouvé
                await ctx.send("📉 Tu n'as pas encore commencé de série. Lance une question avec `!question` pour commencer !")

        except Exception as e:
            print(f"❌ Erreur dans la commande streak : {e}")
            await ctx.send("🚨 Une erreur est survenue en récupérant ta série.")

# ──────────────────────────────────────────────────────────────
# 🔌 Fonction d'enregistrement du Cog
# ──────────────────────────────────────────────────────────────
async def setup(bot):
    await bot.add_cog(Streak(bot))
