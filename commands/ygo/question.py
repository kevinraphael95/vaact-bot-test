import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import traceback

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("📦 Cog 'Question' initialisée.")

    @commands.command(name="question")
    async def question(self, ctx):
        print(f"✅ Commande !question appelée par {ctx.author}")

        try:
            async with aiohttp.ClientSession() as session:
                print("🔁 Requête pour la carte correcte...")
                async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                    if r.status != 200:
                        raise Exception(f"Échec API principale: {r.status}")
                    true_card = await r.json()

                print(f"🃏 Carte sélectionnée : {true_card.get('name', '[Aucune]')}")
                choices = [true_card["name"]]

                while len(choices) < 4:
                    async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                        if r.status != 200:
                            print(f"⚠️ Carte aléatoire rejetée: code {r.status}")
                            continue
                        card = await r.json()
                        name = card.get("name")
                        if name and name not in choices:
                            choices.append(name)

                print(f"🎲 Choix générés (avant mélange) : {choices}")
                random.shuffle(choices)
                correct_index = choices.index(true_card["name"])

                embed = discord.Embed(
                    title="🔎 Devine la carte !",
                    color=discord.Color.blurple()
                )

                # Affiche les attributs importants
                for attr in ["type", "atk", "def", "level", "attribute", "desc"]:
                    print(f"📄 {attr}: {true_card.get(attr)}")

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
                print("📤 Embed envoyé avec succès.")

                for emoji in REACTIONS:
                    await msg.add_reaction(emoji)
                print("👍 Réactions ajoutées.")

                def check(reaction, user):
                    return (
                        user == ctx.author and
                        str(reaction.emoji) in REACTIONS and
                        reaction.message.id == msg.id
                    )

                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                    print(f"📬 Réaction reçue : {reaction.emoji}")
                except asyncio.TimeoutError:
                    await ctx.send("⏰ Temps écoulé !")
                    print("⌛ Timeout sur la réaction.")
                    return

                selected_index = REACTIONS.index(str(reaction.emoji))
                if selected_index == correct_index:
                    await ctx.send(f"✅ Bonne réponse ! C'était bien **{true_card['name']}**.")
                else:
                    await ctx.send(f"❌ Mauvaise réponse ! C'était **{true_card['name']}**.")

        except Exception as e:
            print("💥 Exception attrapée dans la commande !question")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur est survenue lors de la génération de la question.")

# Setup pour le loader dynamique
async def setup(bot):
    await bot.add_cog(Question(bot))
    print("✅ Cog Question chargé avec succès.")
