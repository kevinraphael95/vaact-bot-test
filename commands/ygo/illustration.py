# ──────────────────────────────────────────────────────────────
# 📁 ILLUSTRATION
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

# Émojis pour les choix de réponses
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ──────────────────────────────────────────────────────────────
# 🔧 COG : IllustrationCommand
# ──────────────────────────────────────────────────────────────
class IllustrationCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_random_card(self):
        """Récupère une carte aléatoire depuis l'API YGOProDeck."""
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        return random.choice(data.get("data", [])) if data.get("data") else None

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !illustration
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="illustration",
        aliases=["illu"],
        help="🖼️ Devine une carte Yu-Gi-Oh à partir de son image croppée."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def illustration(self, ctx: commands.Context):
        try:
            # 🃏 Carte réelle
            true_card = await self.fetch_random_card()
            if not true_card or not true_card.get("name"):
                await ctx.send("🚨 Impossible de récupérer une carte valide.")
                return

            image_url = true_card.get("card_images", [{}])[0].get("image_url_cropped", None)
            if not image_url:
                await ctx.send("🚫 Cette carte n’a pas d’illustration croppée.")
                return

            # ❌ Fausses propositions
            wrong_choices = []
            while len(wrong_choices) < 3:
                card = await self.fetch_random_card()
                if card and card["name"] != true_card["name"] and card["name"] not in [c["name"] for c in wrong_choices]:
                    wrong_choices.append(card)

            # 🔀 Mélange des réponses
            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # 📤 Embed
            embed = discord.Embed(
                title="🖼️ Devine la carte à partir de son illustration !",
                description="\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)]),
                color=discord.Color.purple()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text="Réagis avec l’emoji correspondant à ta réponse.")

            msg = await ctx.send(embed=embed)

            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            # ✅ Vérification réaction utilisateur
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            if selected_index == correct_index:
                await ctx.send(f"✅ Bien joué ! C’était **{true_card['name']}**.")
            else:
                await ctx.send(f"❌ Mauvaise réponse ! La bonne carte était **{true_card['name']}**.")

        except Exception as e:
            print("[ERREUR ILLUSTRATION]", e)
            await ctx.send("🚨 Une erreur est survenue pendant le quiz.")

    # 🏷️ Catégorisation
    def cog_load(self):
        self.illustration.category = "🃏 Yu-Gi-Oh!"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(IllustrationCommand(bot))
    print("✅ Cog chargé : IllustrationCommand (catégorie = 🃏 Yu-Gi-Oh!)")
