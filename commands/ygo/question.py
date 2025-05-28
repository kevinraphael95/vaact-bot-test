import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_valid_card(self, session):
        url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"
        for _ in range(10):  # max 10 tentatives
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if all(k in data for k in ("name", "desc", "type")) and "token" not in data.get("type", "").lower():
                        return data
        return None

    @commands.command(name="question", help="Devine le nom de la carte YuGiOh à partir de sa description.")
    async def question(self, ctx):
        print("✅ Commande !question appelée")

        try:
            async with aiohttp.ClientSession() as session:
                true_card = await self.get_valid_card(session)
                if not true_card:
                    await ctx.send("🚨 Impossible de récupérer une carte valide.")
                    return

                choices = [true_card["name"]]
                while len(choices) < 4:
                    card = await self.get_valid_card(session)
                    if card and card["name"] not in choices:
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
            embed.add_field(
                name="Description",
                value=true_card.get("desc", "—")[:300],
                inline=False
            )

            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            msg = await ctx.send(embed=embed)

            for emoji in REACTIONS:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return (
                    user == ctx.author and
                    str(reaction.emoji) in REACTIONS and
                    reaction.message.id == msg.id
                )

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

        except Exception as e:
            import traceback
            traceback.print_exc()
            await ctx.send("🚨 Une erreur est survenue lors de la génération de la question.")
