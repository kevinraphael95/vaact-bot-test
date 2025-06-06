# ────────────────────────────────────────────────────────────────────────────────
# 📌 illustration.py — Commande interactive !illustration
# Objectif : Devine une carte Yu-Gi-Oh! à partir de son image croppée
# Catégorie : 🃏 Yu-Gi-Oh!
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# 📦 Imports nécessaires
import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import os
from supabase import create_client, Client

# 🔐 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📊 Constantes
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]
MAITRE_ROLE_NAME = "Maître des cartes"

# 🧠 Cog principal
class Illustration(commands.Cog):
    """
    Commande !illustration — Devine une carte à partir de son illustration
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

    async def update_maitre_role(self, guild: discord.Guild):
        try:
            data = supabase.table("ygo_streaks").select("user_id, best_illustreak").order("best_illustreak", desc=True).limit(1).execute().data
            if not data:
                return

            top_user_id = int(data[0]["user_id"])
            role = discord.utils.get(guild.roles, name=MAITRE_ROLE_NAME)
            if not role:
                role = await guild.create_role(name=MAITRE_ROLE_NAME, reason="Top joueur du quiz illustration")

            for member in guild.members:
                if role in member.roles and member.id != top_user_id:
                    await member.remove_roles(role)
                if member.id == top_user_id and role not in member.roles:
                    await member.add_roles(role)
        except Exception as e:
            print("[ERREUR rôle maître]", e)

    @commands.command(
        name="illustration",
        aliases=["illu", "i"],
        help="🔼 Devine une carte Yu-Gi-Oh! à partir de son image croppée.",
        description="Quiz interactif avec image croppée de carte Yu-Gi-Oh! et réactions."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def illustration(self, ctx: commands.Context):
        try:
            all_cards = await self.fetch_all_cards()
            candidates = [c for c in all_cards if "image_url_cropped" in c.get("card_images", [{}])[0]]
            true_card = random.choice(candidates)
            image_url = true_card["card_images"][0]["image_url_cropped"]
            similar_cards = await self.get_similar_cards(all_cards, true_card)

            if len(similar_cards) < 3:
                return await ctx.send("❌ Pas assez de cartes similaires pour ce tour.")

            all_choices = [true_card["name"]] + [c["name"] for c in similar_cards]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            msg = await ctx.send("⏳ Préparation du quiz...")
            for i in range(10, 0, -1):
                await msg.edit(content=f"⏳ Début dans {i} seconde{'s' if i > 1 else ''}...")
                await asyncio.sleep(1)

            embed = discord.Embed(
                title="🔼 Devine la carte à partir de son illustration !",
                description="\n".join(f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)),
                color=discord.Color.purple()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"🔹 Archétype : ||{true_card.get('archetype', 'Aucun')}||")
            await msg.edit(content=None, embed=embed)

            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS and not user.bot

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

            await ctx.send(f"⏳ Temps écoulé ! La bonne réponse était **{true_card['name']}**.")

            winners = []
            for user_id, idx in users_answers.items():
                correct = (idx == correct_index)
                response = supabase.table("ygo_streaks").select("illu_streak, best_illustreak").eq("user_id", user_id).execute()
                data = response.data
                current = data[0]["illu_streak"] if data else 0
                best = data[0]["best_illustreak"] if data else 0

                if correct:
                    current += 1
                    best = max(best, current)
                    winners.append(user_id)
                else:
                    current = 0

                supabase.table("ygo_streaks").upsert({
                    "user_id": user_id,
                    "illu_streak": current,
                    "best_illustreak": best
                }).execute()

            await self.update_maitre_role(ctx.guild)

            if winners:
                mentions = ", ".join(self.bot.get_user(uid).mention for uid in winners if self.bot.get_user(uid))
                await ctx.send(f"🎉 Bravo à {mentions} !")
            else:
                await ctx.send("😞 Personne n'a trouvé la bonne réponse.")

            # Afficher les scores
            score_lines = []
            for user_id in users_answers:
                user = self.bot.get_user(user_id)
                if not user:
                    continue
                record = supabase.table("ygo_streaks").select("illu_streak, best_illustreak").eq("user_id", user_id).execute().data
                if record:
                    streak = record[0]["illu_streak"]
                    best = record[0]["best_illustreak"]
                    score_lines.append(f"🏅 {user.mention} — Série actuelle : {streak} | Meilleure série : {best}")
            if score_lines:
                await ctx.send("\n".join(score_lines))

        except Exception as e:
            print("[ERREUR illustration]", e)
            await ctx.send("🚨 Une erreur est survenue pendant le quiz.")

# 🔌 Setup du Cog
async def setup(bot: commands.Bot):
    cog = Illustration(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
