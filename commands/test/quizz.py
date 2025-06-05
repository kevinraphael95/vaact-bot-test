# ────────────────────────────────────────────────────────────────────────────────
# 📌 quizz.py — Commande interactive !quizz
# Objectif : Poser une question de quiz Yu-Gi-Oh! avec réactions pour répondre
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os
import random
import asyncio

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données JSON
# ────────────────────────────────────────────────────────────────────────────────
DATA_JSON_PATH = os.path.join("data", "quizz_questions.json")

def load_data():
    """Charge les questions du quiz depuis le fichier JSON."""
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Quizz(commands.Cog):
    """
    Commande !quizz — Pose une question de quiz avec 4 choix et réactions emoji.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.questions = load_data()  # Liste de dict : [{ "question": str, "choices": [str, str, str, str], "answer": int }, ...]

    @commands.command(
        name="quizz",
        help="Pose une question de quiz Yu-Gi-Oh! avec réactions.",
        description="Pose une question et attends ta réponse par réaction emoji 1️⃣ 2️⃣ 3️⃣ 4️⃣."
    )
    async def quizz(self, ctx: commands.Context):
        try:
            question_data = random.choice(self.questions)
            question = question_data["question"]
            choices = question_data["choices"]
            correct_index = question_data["answer"]  # Index 0..3

            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

            desc = ""
            for i, choice in enumerate(choices):
                desc += f"{emojis[i]} {choice}\n"

            embed = discord.Embed(
                title="🃏 Quiz Yu-Gi-Oh! 🃏",
                description=f"**{question}**\n\n{desc}\n*Réponds en cliquant sur l'emoji correspondant.*",
                color=discord.Color.blue()
            )

            quiz_message = await ctx.send(embed=embed)

            # Ajouter réactions
            for emoji in emojis:
                await quiz_message.add_reaction(emoji)

            def check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji) in emojis
                    and reaction.message.id == quiz_message.id
                )

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Temps écoulé, {ctx.author.mention} ! Tu n'as pas répondu à temps.")
                return

            user_answer = emojis.index(str(reaction.emoji))

            if user_answer == correct_index:
                await ctx.send(f"✅ Bravo {ctx.author.mention}, bonne réponse !")
            else:
                await ctx.send(f"❌ Désolé {ctx.author.mention}, mauvaise réponse. La bonne réponse était {emojis[correct_index]} {choices[correct_index]}.")

        except Exception as e:
            print(f"[ERREUR quizz] {e}")
            await ctx.send("❌ Une erreur est survenue lors du quiz.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Quizz(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
