import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_random_card(self):
        url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()

    @commands.command(name="question", help="Devine la carte Yu-Gi-Oh à partir de sa description.")
    async def question(self, ctx):
        try:
            # Obtenir la vraie carte
            true_card = await self.fetch_random_card()
            if not true_card or not all(k in true_card for k in ("name", "desc", "type")):
                await ctx.send("🚨 Impossible de récupérer une carte valide.")
                return

            # Obtenir 3 fausses cartes (en boucle)
            wrong_choices = []
            while len(wrong_choices) < 3:
                card = await self.fetch_random_card()
                if card and card["name"] != true_card["name"] and card["name"] not in [c["name"] for c in wrong_choices]:
                    wrong_choices.append(card)

            # Mélanger les choix
            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # Construire l'embed
            embed = discord.Embed(
                title="🔍 Devine la carte !",
                description=true_card["desc"][:300],
                color=discord.Color.dark_blue()
            )
            embed.add_field(name="Type", value=true_card.get("type", "—"), inline=True)
            embed.add_field(name="ATK", value=str(true_card.get("atk", "—")), inline=True)
            embed.add_field(name="DEF", value=str(true_card.get("def", "—")), inline=True)
            embed.add_field(name="Niveau", value=str(true_card.get("level", "—")), inline=True)
            embed.add_field(name="Attribut", value=true_card.get("attribute", "—"), inline=True)

            # Ajouter les options
            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            msg = await ctx.send(embed=embed)

            # Ajouter les réactions
            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return (
                    user == ctx.author and
                    reaction.message.id == msg.id and
                    str(reaction.emoji) in REACTIONS
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
            print("Erreur :", e)
            await ctx.send("🚨 Une erreur est survenue.")

