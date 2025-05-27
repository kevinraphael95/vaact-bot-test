import discord
from discord.ext import commands
import random
import aiohttp
from supabase_client import supabase

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="question")
    async def question(self, ctx):
        async with aiohttp.ClientSession() as session:
            # Obtenir 4 cartes aléatoires
            async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php") as r:
                true_card = await r.json()

            choices = [true_card["name"]]
            while len(choices) < 4:
                async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php") as r:
                    c = await r.json()
                    if c["name"] not in choices:
                        choices.append(c["name"])

            random.shuffle(choices)
            correct_index = choices.index(true_card["name"])

            # Embed sans le nom de la carte
            embed = discord.Embed(title="🔎 Devine la carte !", color=discord.Color.blue())
            embed.add_field(name="Type", value=true_card.get("type", "Inconnu"), inline=True)
            embed.add_field(name="ATK", value=str(true_card.get("atk", "—")), inline=True)
            embed.add_field(name="DEF", value=str(true_card.get("def", "—")), inline=True)
            embed.add_field(name="Niveau", value=str(true_card.get("level", "—")), inline=True)
            embed.add_field(name="Attribut", value=true_card.get("attribute", "—"), inline=True)
            embed.add_field(name="Description", value=true_card.get("desc", "—")[:500], inline=False)

            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            question_msg = await ctx.send(embed=embed)

            for emoji in REACTIONS:
                await question_msg.add_reaction(emoji)

            def check(reaction, user):
                return (
                    user == ctx.author and
                    str(reaction.emoji) in REACTIONS and
                    reaction.message.id == question_msg.id
                )

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Temps écoulé !")

            selected = REACTIONS.index(str(reaction.emoji))

            if selected == correct_index:
                await self.update_streak(ctx.author.id, True)
                streak = self.get_streak(ctx.author.id)
                await ctx.send(f"✅ Bonne réponse ! Série actuelle : `{streak}` 🔥")
            else:
                await self.update_streak(ctx.author.id, False)
                await ctx.send(f"❌ Mauvaise réponse ! La bonne réponse était **{true_card['name']}**.")

    def get_streak(self, user_id):
        result = supabase.table("ygo_streaks").select("current_streak").eq("user_id", str(user_id)).execute()
        if result.data and isinstance(result.data, list) and result.data[0].get("current_streak") is not None:
            return result.data[0]["current_streak"]
        return 0

    def update_streak(self, user_id, success):
        current = self.get_streak(user_id)
        new_streak = current + 1 if success else 0
        supabase.table("ygo_streaks").upsert({
            "user_id": str(user_id),
            "current_streak": new_streak
        }).execute()

async def setup(bot):
    await bot.add_cog(Question(bot))
