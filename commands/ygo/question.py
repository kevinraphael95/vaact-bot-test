import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cards_cache = []  # on garde les cartes ici

    async def fetch_all_cards(self):
        if self.cards_cache:
            return self.cards_cache

        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()

        self.cards_cache = [
            c for c in data["data"]
            if all(k in c for k in ("name", "desc", "type")) and "token" not in c.get("type", "").lower()
        ]
        return self.cards_cache

    @commands.command(name="question", help="Devine le nom de la carte YuGiOh à partir de sa description.")
    async def question(self, ctx):
        print("✅ Commande !question appelée")

        try:
            all_cards = await self.fetch_all_cards()

            if not all_cards:
                await ctx.send("🚨 Impossible de récupérer les cartes.")
                return

            true_card = random.choice(all_cards)
            wrong_choices = random.sample([c for c in all_cards if c["name"] != true_card["name"]], 3)
            choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
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
