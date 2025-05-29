# ───────────────────────────────────────────────────────────────────────────────
# ❓ question.py — Commande !question
# Permet aux utilisateurs de deviner une carte Yu-Gi-Oh à partir de sa description.
# Inclut un système de "streak" enregistré via Supabase.
# ───────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import re
from supabase_client import supabase  # Ton module contenant un client Supabase connecté

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]  # Emojis pour les choix multiples

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !question
# ───────────────────────────────────────────────────────────────────────────────

class Question(commands.Cog):
    def __init__(self, bot):
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

    def censor_card_name(self, description: str, card_name: str) -> str:
        """Masque le nom de la carte dans la description (avec des █)."""
        escaped = re.escape(card_name)
        return re.sub(escaped, "█" * len(card_name), description, flags=re.IGNORECASE)

    async def update_streak(self, user_id: str, correct: bool):
        """Met à jour la série (streak) de bonnes réponses de l'utilisateur."""
        data = supabase.table("ygo_streaks").select("*").eq("user_id", user_id).execute()

        if data.data:
            row = data.data[0]
            current = row["current_streak"]
            best = row.get("best_streak", 0)

            if correct:
                new_streak = current + 1
                update_data = {"current_streak": new_streak}
                if new_streak > best:
                    update_data["best_streak"] = new_streak
                supabase.table("ygo_streaks").update(update_data).eq("user_id", user_id).execute()
            else:
                supabase.table("ygo_streaks").update({"current_streak": 0}).eq("user_id", user_id).execute()
        else:
            # Première participation de l'utilisateur
            supabase.table("ygo_streaks").insert({
                "user_id": user_id,
                "current_streak": 1 if correct else 0,
                "best_streak": 1 if correct else 0
            }).execute()

    @commands.command(
        name="question",
        aliases=["q"],
        help="Devine la carte Yu-Gi-Oh à partir de sa description."
    )
    async def question(self, ctx):
        try:
            # 🃏 Sélection de la vraie carte
            true_card = await self.fetch_random_card()
            if not true_card or not all(k in true_card for k in ("name", "desc", "type")):
                await ctx.send("🚨 Impossible de récupérer une carte valide.")
                return

            # ❌ Génération de 3 fausses réponses
            wrong_choices = []
            while len(wrong_choices) < 3:
                card = await self.fetch_random_card()
                if card and card["name"] != true_card["name"] and card["name"] not in [c["name"] for c in wrong_choices]:
                    wrong_choices.append(card)

            # 🎯 Mélange des choix
            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # 🕵️‍♂️ Masquage du nom dans la description
            censored_desc = self.censor_card_name(true_card["desc"], true_card["name"])

            # 🖼️ Création de l'embed
            embed = discord.Embed(
                title="🔍 Devine la carte !",
                description=censored_desc[:300] + ("..." if len(censored_desc) > 300 else ""),
                color=discord.Color.purple()
            )
            embed.add_field(name="Type", value=true_card.get("type", "—"), inline=True)

            if true_card.get("type", "").lower().startswith("monstre"):
                embed.add_field(name="ATK", value=str(true_card.get("atk", "—")), inline=True)
                embed.add_field(name="DEF", value=str(true_card.get("def", "—")), inline=True)
                embed.add_field(name="Niveau", value=str(true_card.get("level", "—")), inline=True)
                embed.add_field(name="Attribut", value=true_card.get("attribute", "—"), inline=True)

            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)])
            embed.add_field(name="Quel est le nom de cette carte ?", value=options, inline=False)

            msg = await ctx.send(embed=embed)

            # 🗳️ Ajout des réactions pour voter
            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            # 🔎 Vérifie que l'utilisateur réagit bien
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            user_id = str(ctx.author.id)

            if selected_index == correct_index:
                await self.update_streak(user_id, correct=True)
                await ctx.send(f"✅ Bonne réponse ! C'était bien **{true_card['name']}**.")
            else:
                await self.update_streak(user_id, correct=False)
                await ctx.send(f"❌ Mauvaise réponse ! C'était **{true_card['name']}**. Ta série est réinitialisée.")

        except Exception as e:
            print("[ERREUR QUESTION]", e)
            await ctx.send("🚨 Une erreur est survenue.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog
# Attribution de la catégorie "VAACT" pour les systèmes de help personnalisés
# ───────────────────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = Question(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
