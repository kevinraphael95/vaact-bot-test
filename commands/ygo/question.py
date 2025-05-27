import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

# Emojis pour les choix de réponse
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="question")
    async def question(self, ctx):
        # Affiche dans la console quand la commande est déclenchée
        print("✅ Commande !question appelée")

        try:
            # Ouverture d'une session HTTP pour accéder à l'API
            async with aiohttp.ClientSession() as session:
                # Récupère une carte aléatoire (qui sera la bonne réponse)
                async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                    true_card = await r.json()

                # Liste des choix, la bonne réponse d'abord
                choices = [true_card["name"]]

                # Ajoute 3 autres cartes aléatoires (différentes)
                while len(choices) < 4:
                    async with session.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr") as r:
                        card = await r.json()
                        if card["name"] not in choices:
                            choices.append(card["name"])

            # Mélange les choix pour ne pas savoir où est la bonne réponse
            random.shuffle(choices)
            # Trouve l'index de la bonne réponse dans la liste mélangée
            correct_index = choices.index(true_card["name"])

            # Création de l'embed Discord qui affichera la question
            embed = discord.Embed(
                title="🔎 Devine la carte !",
                color=discord.Color.blue()
            )

            # Ajoute des infos sur la carte, avec gestion des champs manquants
            embed.add_field(name="Type", value=true_card.get("type", "Inconnu"), inline=True)
            embed.add_field(name="ATK", value=str(true_card.get("atk", "—")), inline=True)
            embed.add_field(name="DEF", value=str(true_card.get("def", "—")), inline=True)
            embed.add_field(name="Niveau", value=str(true_card.get("level", "—")), inline=True)
            embed.add_field(name="Attribut", value=true_card.get("attribute", "—"), inline=True)
            embed.add_field(
                name="Description",
                value=true_card.get("desc", "—")[:300],  # Coupe à 300 caractères
                inline=False
            )

            # Ajoute les choix sous forme de texte avec emoji
            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            # Envoie l'embed sur Discord
            msg = await ctx.send(embed=embed)

            # Ajoute les réactions (🇦 à 🇩) pour voter
            for emoji in REACTIONS:
                await msg.add_reaction(emoji)

            # Fonction pour vérifier que la réaction vient de la bonne personne
            def check(reaction, user):
                return (
                    user == ctx.author and
                    str(reaction.emoji) in REACTIONS and
                    reaction.message.id == msg.id
                )

            try:
                # Attend une réaction pendant 30 secondes max
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                # Si personne ne répond, envoie un message d’expiration
                await ctx.send("⏰ Temps écoulé !")
                return

            # Vérifie si l’emoji choisi est le bon index
            selected_index = REACTIONS.index(str(reaction.emoji))
            if selected_index == correct_index:
                await ctx.send(f"✅ Bonne réponse ! C'était bien **{true_card['name']}**.")
            else:
                await ctx.send(f"❌ Mauvaise réponse ! C'était **{true_card['name']}**.")

        except Exception as e:
            # Si une erreur inattendue se produit, elle est affichée
            print(f"❌ Erreur pendant l'exécution : {e}")
            await ctx.send("🚨 Une erreur est survenue lors de la génération de la question.")

# Fonction pour enregistrer le cog auprès du bot
async def setup(bot):
    await bot.add_cog(Question(bot))
