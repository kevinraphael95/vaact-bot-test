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

        try:
            async with aiohttp.ClientSession() as session:
                # ➤ Étape 1 : récupérer une carte avec un 'name'
                print("🔁 Récupération de la carte correcte...")
                true_card = await self.get_valid_card(session)
                if not true_card:
                    await ctx.send("🚨 Impossible de récupérer une carte valide.")
                    return

                print(f"🃏 Carte sélectionnée : {true_card.get('name', 'inconnue')}")

                # ➤ Étape 2 : récupérer d'autres cartes avec nom unique
                choices = [true_card["name"]]
                print("📦 Génération des autres choix...")

                while len(choices) < 4:
                    card = await self.get_valid_card(session)
                    if card:
                        name = card.get("name")
                        if name not in choices:
                            choices.append(name)

                print(f"🎲 Choix finaux : {choices}")

            random.shuffle(choices)
            correct_index = choices.index(true_card["name"])

            embed = discord.Embed(
                title="🔎 Devine la carte !",
                color=discord.Color.blue()
            )

            print("🛠️ Vérification des champs de la carte...")
            for key in ["type", "atk", "def", "level", "attribute", "desc"]:
                print(f"  - {key}: {true_card.get(key)}")

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
            print(f"❌ ERREUR: {e}")

    async def get_valid_card(self, session, max_retries=5):
        url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"
        for _ in range(max_retries):
            async with session.get(url) as r:
                if r.status == 200:
                    data = await r.json()
                    if "name" in data:
                        return data
                    else:
                        print("❗ Carte invalide (pas de 'name'), on réessaie...")
        return None
