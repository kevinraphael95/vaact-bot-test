# ──────────────────────────────────────────────────────────────
# 📁 testquestion.py
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import re
from supabase_client import supabase

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TestQuestionCommand
# ──────────────────────────────────────────────────────────────
class TestQuestionCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !testquestion
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="testquestion",
        aliases=["tq"],
        help="🧠 Devine la carte Yu-Gi-Oh parmi 4 du même archétype."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def testquestion(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        channel_id = str(ctx.channel.id)

        # Vérifier s'il y a déjà un test en cours
        result = supabase.table("ygo_test_questions").select("*").eq("user_id", user_id).eq("status", "en_cours").execute()
        if result.data:
            await ctx.send("⚠️ Tu as déjà un test-question en cours ! Réponds d'abord à celui-ci.")
            return

        # Récupération des cartes
        cards = await self.fetch_card_sample()
        if not cards:
            await ctx.send("🚨 Erreur lors du chargement des cartes.")
            return

        # Trouver une carte avec archétype
        random.shuffle(cards)
        main_card = next((c for c in cards if c.get("archetype") and "desc" in c and "name" in c), None)
        if not main_card:
            await ctx.send("❌ Impossible de trouver une carte avec archétype.")
            return

        archetype = main_card["archetype"]

        # Récupérer d'autres cartes du même archétype
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?archetype={archetype}&language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Erreur de récupération des cartes d'archétype.")
                    return
                data = await resp.json()
                group = [c for c in data.get("data", []) if "name" in c and "desc" in c and c["name"] != main_card["name"]]

        if len(group) < 3:
            await ctx.send("❌ Pas assez de cartes pour générer un test.")
            return

        # Construction de la question
        true_card = main_card
        wrong_choices = random.sample(group, 3)
        all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
        random.shuffle(all_choices)
        correct_index = all_choices.index(true_card["name"])
        desc = self.censor_card_name(true_card["desc"], true_card["name"])
        image_url = true_card.get("card_images", [{}])[0].get("image_url")

        # Embed
        embed = discord.Embed(
            title=f"🧩 Archétype : {archetype}",
            description=f"🔍 *{desc[:300]}{'...' if len(desc) > 300 else ''}*",
            color=discord.Color.purple()
        )
        embed.set_author(name="YGO Quiz", icon_url="https://cdn-icons-png.flaticon.com/512/361/361678.png")
        if image_url:
            embed.set_thumbnail(url=image_url)

        embed.add_field(name="📘 Type", value=true_card.get("type", "—"), inline=True)
        if true_card.get("type", "").lower().startswith("monstre"):
            embed.add_field(name="💥 ATK", value=str(true_card.get("atk", "—")), inline=True)
            embed.add_field(name="🛡️ DEF", value=str(true_card.get("def", "—")), inline=True)
            embed.add_field(name="⭐ Niveau", value=str(true_card.get("level", "—")), inline=True)
            embed.add_field(name="🌪️ Attribut", value=true_card.get("attribute", "—"), inline=True)

        reactions = ["🇦", "🇧", "🇨", "🇩"]
        options = "\n".join([f"{reactions[i]} {name}" for i, name in enumerate(all_choices)])
        embed.add_field(name="❓ Quelle est cette carte ?", value=options, inline=False)
        embed.set_footer(text="Réagis ci-dessous pour répondre 👇")

        msg = await ctx.send(embed=embed)
        for emoji in reactions[:len(all_choices)]:
            await msg.add_reaction(emoji)

        # Enregistrement du test dans Supabase
        supabase.table("ygo_test_questions").insert({
            "user_id": user_id,
            "question": desc,
            "reponse": true_card["name"],
            "status": "en_cours",
            "message_id": str(msg.id),
            "channel_id": channel_id
        }).execute()

    def censor_card_name(self, description: str, card_name: str) -> str:
        escaped = re.escape(card_name)
        return re.sub(escaped, "█" * len(card_name), description, flags=re.IGNORECASE)

    async def fetch_card_sample(self, limit=150):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                all_cards = data.get("data", [])
                return random.sample(all_cards, min(limit, len(all_cards)))

    def cog_load(self):
        self.testquestion.category = "🃏 Yu-Gi-Oh!"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TestQuestionCommand(bot))
    print("✅ Cog chargé : TestQuestionCommand (catégorie = 🃏 Yu-Gi-Oh!)")
