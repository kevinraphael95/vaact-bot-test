# ──────────────────────────────────────────────────────────────
# 📁 ILLUSTRATION
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ──────────────────────────────────────────────────────────────
# 🔧 COG : IllustrationCommand
# ──────────────────────────────────────────────────────────────
class IllustrationCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_all_cards(self):
        """Récupère toutes les cartes en français."""
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
        return data.get("data", [])

    async def get_similar_cards(self, all_cards, true_card):
        """Retourne jusqu'à 3 cartes similaires par archétype, ou sinon par type."""
        archetype = true_card.get("archetype")
        card_type = true_card.get("type", "")

        # 🔎 Filtrage par archétype
        if archetype:
            group = [card for card in all_cards if card.get("archetype") == archetype and card["name"] != true_card["name"]]
        else:
            # Sinon, filtrage par type (ex: Monstre, Magie, Piège)
            group = [card for card in all_cards if card.get("type") == card_type and card["name"] != true_card["name"]]

        return random.sample(group, k=min(3, len(group))) if group else []

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
            all_cards = await self.fetch_all_cards()
            if not all_cards:
                await ctx.send("🚨 Impossible de récupérer les cartes.")
                return

            # 🃏 Carte cible à deviner
            true_card = random.choice([card for card in all_cards if "image_url_cropped" in card.get("card_images", [{}])[0]])
            image_url = true_card["card_images"][0].get("image_url_cropped")
            if not image_url:
                await ctx.send("🚫 Cette carte n’a pas d’illustration croppée.")
                return

            # 🎯 Cartes similaires
            similar_cards = await self.get_similar_cards(all_cards, true_card)

            # ⛔ Si pas assez de propositions
            if len(similar_cards) < 3:
                await ctx.send("❌ Pas assez de cartes similaires pour créer des choix.")
                return

            # 🔀 Préparation des choix
            all_choices = [true_card["name"]] + [card["name"] for card in similar_cards]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # 🖼️ Création de l'embed
            embed = discord.Embed(
                title="🖼️ Devine la carte à partir de son illustration !",
                description="\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)]),
                color=discord.Color.purple()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"🔹 Archétype : ||{true_card.get('archetype', 'Aucun')}||")

            msg = await ctx.send(embed=embed)

            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            if selected_index == correct_index:
                await ctx.send(f"✅ Bonne réponse ! C’était **{true_card['name']}**.")
            else:
                await ctx.send(f"❌ Mauvaise réponse ! C’était **{true_card['name']}**.")

        except Exception as e:
            print("[ERREUR ILLUSTRATION]", e)
            await ctx.send("🚨 Une erreur est survenue pendant le quiz.")

    def cog_load(self):
        self.illustration.category = "🃏 Yu-Gi-Oh!"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(IllustrationCommand(bot))
    print("✅ Cog chargé : IllustrationCommand (catégorie = 🃏 Yu-Gi-Oh!)")
