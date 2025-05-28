from discord.ext import commands
import discord
from supabase_client import supabase

class YuGiOh(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="streak", aliases = ["qs"], help="📊 Affiche ta série de bonnes réponses consécutives.")
    async def streak(self, ctx):
        user_id = str(ctx.author.id)

        try:
            result = supabase.table("ygo_streaks").select("current_streak").eq("user_id", user_id).execute()

            streak = 0
            if result.data and isinstance(result.data, list) and len(result.data) > 0:
                streak = result.data[0].get("current_streak", 0)

            embed = discord.Embed(
                title="🔥 Ton Yu-Gi-Oh! Streak",
                description=f"Tu as actuellement une série de **{streak}** bonnes réponses consécutives !",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Réponds correctement pour faire grimper ta série 🧠")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("❌ Une erreur est survenue en récupérant ton streak.")
            print(f"[Erreur Supabase - streak] {e}")

async def setup(bot):
    await bot.add_cog(YuGiOh(bot))

