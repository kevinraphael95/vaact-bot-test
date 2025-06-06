# ────────────────────────────────────────────────────────────────
# 📌 illustration.py — Commande interactive !illustration
# Objectif : Jeu pour deviner une carte Yu-Gi-Oh! à partir de son image croppée.
# Catégorie : 🃏 Yu-Gi-Oh!
# Accès : Public
# ────────────────────────────────────────────────────────────────

# 📦 Imports nécessaires
import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import os
from supabase import create_client, Client

# 🔤 CONSTANTES
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🧠 Cog principal
class IllustrationCommand(commands.Cog):
    """
    Commande !illustration — Jeu où tout le monde peut répondre à un quiz d’image Yu-Gi-Oh!
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_all_cards(self):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                return (await resp.json()).get("data", [])

    async def get_similar_cards(self, all_cards, true_card):
        archetype = true_card.get("archetype")
        card_type = true_card.get("type", "")
        group = [c for c in all_cards if (c.get("archetype") == archetype or c.get("type") == card_type) and c["name"] != true_card["name"]]
        return random.sample(group, k=min(3, len(group))) if group else []

    @commands.command(
        name="illustration",
        aliases=["illu", "i"],
        help="🔼 Devine une carte Yu-Gi-Oh! à partir de son image croppée.",
        description="Affiche une image de carte Yu-Gi-Oh! croppée et propose un quiz interactif avec réactions."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def illustration(self, ctx: commands.Context):
        try:
            all_cards = await self.fetch_all_cards()
            candidates = [c for c in all_cards if "image_url_cropped" in c.get("card_images", [{}])[0]]
            true_card = random.choice(candidates)
            image_url = true_card["card_images"][0].get("image_url_cropped")
            similar_cards = await self.get_similar_cards(all_cards, true_card)

            if len(similar_cards) < 3:
                await ctx.send("❌ Pas assez de cartes similaires.")
                return

            all_choices = [true_card["name"]] + [c["name"] for c in similar_cards]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            countdown_msg = await ctx.send("⏳ Début dans 10 secondes...")
            for i in range(10, 0, -1):
                await countdown_msg.edit(content=f"⏳ Début dans {i} seconde{'s' if i > 1 else ''}...")
                await asyncio.sleep(1)

            embed = discord.Embed(
                title="🔼 Devine la carte à partir de son illustration !",
                description="\n".join(f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)),
                color=discord.Color.purple()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"🔹 Archétype : ||{true_card.get('archetype', 'Aucun')}||")
            await countdown_msg.edit(content=None, embed=embed)

            for emoji in REACTIONS[:len(all_choices)]:
                await countdown_msg.add_reaction(emoji)

            def check(reaction, user):
                return reaction.message.id == countdown_msg.id and str(reaction.emoji) in REACTIONS and not user.bot

            users_answers = {}
            try:
                start = asyncio.get_event_loop().time()
                while True:
                    timeout = 10 - (asyncio.get_event_loop().time() - start)
                    if timeout <= 0:
                        break
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=timeout, check=check)
                    if user.id not in users_answers:
                        users_answers[user.id] = REACTIONS.index(str(reaction.emoji))
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(1)
            await ctx.send(f"⏳ Temps écoulé ! La bonne réponse était **{true_card['name']}**.")

            for user_id, choice_index in users_answers.items():
                correct = (choice_index == correct_index)
                response = supabase.table("ygo_streaks").select("illu_streak,best_illustreak").eq("user_id", user_id).execute()
                data = response.data
                current_streak = data[0].get("illu_streak", 0) if data else 0
                best_streak = data[0].get("best_illustreak", 0) if data else 0

                if correct:
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)
                else:
                    current_streak = 0

                supabase.table("ygo_streaks").upsert({
                    "user_id": user_id,
                    "illu_streak": current_streak,
                    "best_illustreak": best_streak
                }).execute()

            winners = [self.bot.get_user(uid) for uid, idx in users_answers.items() if idx == correct_index]
            if winners:
                mentions = ", ".join(user.mention for user in winners if user)
                await ctx.send(f"🎉 Bravo à : {mentions} pour leur bonne réponse !")
            else:
                await ctx.send("😞 Personne n'a trouvé la bonne réponse cette fois.")

        except Exception as e:
            print("[ERREUR illustration]", e)
            await ctx.send("🚨 Une erreur est survenue pendant le quiz.")

# 🔌 Setup du Cog
async def setup(bot: commands.Bot):
    cog = IllustrationCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
