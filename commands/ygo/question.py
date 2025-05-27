import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="question")
    async def question(self, ctx):
        print("✅ Commande !question appelée")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                true_card = await r.json()

            choices = [true_card["name"]]
            while len(choices) < 4:
                async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                    card = await r.json()
                    if card["name"] not in choices:
                        choices.append(card["name"])

            random.shuffle(choices)
            correct_index = choices.index(true_card["name"])

            embed = discord.Embed(
                title="🔎 Devine la carte !",
                color=discord.Color.blue()
            )
            embed.add_field(name="Type", value=true_card.get("type", "Inconnu"), inline=True)
            embed.add_field(name="ATK", value=str(true_card.get("atk", "—")), inline=True)
            embed.add_field(name="DEF", value=str(true_card.get("def", "—")), inline=True)
            embed.add_field(name="Niveau", value=str(true_card.get("level", "—")), inline=True)
            embed.add_field(name="Attribut", value=true_card.get("attribute", "—"), inline=True)
            embed.add_field(name="Description", value=true_card.get("desc", "—")[:300], inline=False)

            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            msg = await ctx.send(embed=embed)

            for emoji in REACTIONS:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in REACTIONS and reaction.message.id == msg.id

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            if selected_index == correct_index:
                await ctx.send(f"✅ Bonne réponse ! C'était bien **{true_card['name']}**.")
            else:
                await ctx.send(f"❌ Mauvaise réponse ! C'était **{true_card['name']}**.")

async def setup(bot):
    await bot.add_cog(Question(bot))
