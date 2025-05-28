# ────────────────────────────────────────────────────────────────────────────────
# 🧠 testquestion.py — Commande !testquestion
# But : Deviner une carte Yu-Gi-Oh à partir de sa description parmi 4 du même archétype
# Fonctionnalités :
#   - Masquage du nom dans la description
#   - Cartes prises dans le même archétype
#   - Support des stats (ATK/DEF/etc)
#   - Suivi du streak utilisateur via Supabase
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import re

from supabase_client import supabase  # ⚠️ Assure-toi que ce client est bien configuré

# ────────────────────────────────────────────────────────────────────────────────
# 🔠 Réactions associées aux choix (A, B, C, D)
# ────────────────────────────────────────────────────────────────────────────────
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 Classe du Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class TestQuestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────
    # 📦 Récupération d’un échantillon de cartes Yu-Gi-Oh
    # Utilise l’API officielle YGOPRODeck (cartes en français)
    # ────────────────────────────────────────────────────────────────────────────
    async def fetch_card_sample(self, limit=150):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                all_cards = data.get("data", [])
                return random.sample(all_cards, min(limit, len(all_cards)))

    # ────────────────────────────────────────────────────────────────────────────
    # 🛡️ Remplace toutes les occurrences du nom de la carte dans sa description
    # ────────────────────────────────────────────────────────────────────────────
    def censor_card_name(self, description: str, card_name: str) -> str:
        escaped = re.escape(card_name)
        return re.sub(escaped, "█" * len(card_name), description, flags=re.IGNORECASE)

    # ────────────────────────────────────────────────────────────────────────────
    # 📈 Met à jour le streak d’un utilisateur dans Supabase
    # ────────────────────────────────────────────────────────────────────────────
    async def update_streak(self, user_id: str, correct: bool):
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
            supabase.table("ygo_streaks").insert({
                "user_id": user_id,
                "current_streak": 1 if correct else 0,
                "best_streak": 1 if correct else 0
            }).execute()

    # ────────────────────────────────────────────────────────────────────────────
    # ❓ Commande principale : !testquestion
    # Devine une carte Yu-Gi-Oh à partir de sa description parmi 4
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="testquestion",
        aliases=["tq"],
        help="Devine la carte Yu-Gi-Oh parmi 4 du même archétype."
    )
    async def testquestion(self, ctx):
        try:
            # 🔄 Récupération initiale
            cards = await self.fetch_card_sample()
            if not cards:
                await ctx.send("🚨 Erreur lors du chargement des cartes.")
                return

            # 🔍 Trouver une carte avec un archétype
            random.shuffle(cards)
            main_card = next((c for c in cards if c.get("archetype") and "desc" in c and "name" in c), None)

            if not main_card:
                await ctx.send("❌ Impossible de trouver une carte avec archétype.")
                return

            archetype = main_card["archetype"]

            # 🔗 Récupération des autres cartes du même archétype
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?archetype={archetype}&language=fr"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erreur lors de la récupération des cartes de l'archétype.")
                        return
                    data = await resp.json()
                    group = [c for c in data.get("data", []) if "name" in c and "desc" in c and c["name"] != main_card["name"]]

            if len(group) < 3:
                await ctx.send("❌ Pas assez de cartes pour générer des propositions.")
                return

            # ✅ Préparation des choix
            true_card = main_card
            wrong_choices = random.sample(group, 3)
            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])
            desc = self.censor_card_name(true_card["desc"], true_card["name"])
            image_url = true_card.get("card_images", [{}])[0].get("image_url", None)

            # 🖼️ Embed visuel
            embed = discord.Embed(
                title=f"🧩 Archétype : {archetype}",
                description=f"🔍 **Indice :**\n*{desc[:300]}{'...' if len(desc) > 300 else ''}*",
                color=discord.Color.purple()
            )
            embed.set_author(name="YGO Quiz", icon_url="https://cdn-icons-png.flaticon.com/512/361/361678.png")
            if image_url:
                embed.set_thumbnail(url=image_url)

            embed.add_field(name="📘 Type", value=true_card.get("type", "—"), inline=True)

            # 📊 Stats supplémentaires (pour les monstres uniquement)
            if true_card.get("type", "").lower().startswith("monstre"):
                embed.add_field(name="💥 ATK", value=str(true_card.get("atk", "—")), inline=True)
                embed.add_field(name="🛡️ DEF", value=str(true_card.get("def", "—")), inline=True)
                embed.add_field(name="⭐ Niveau", value=str(true_card.get("level", "—")), inline=True)
                embed.add_field(name="🌪️ Attribut", value=true_card.get("attribute", "—"), inline=True)

            # 🗳️ Propositions
            options = "\n".join([f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)])
            embed.add_field(name="❓ Quelle est cette carte ?", value=options, inline=False)
            embed.set_footer(text="Clique sur la bonne réaction ci-dessous 👇")

            msg = await ctx.send(embed=embed)

            # 🧷 Ajout des réactions
            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            # ✅ Attente réponse utilisateur
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            user_id = str(ctx.author.id)

            # 🏁 Résultat
            if selected_index == correct_index:
                await self.update_streak(user_id, correct=True)
                await ctx.send(f"✅ Bonne réponse ! C’était bien **{true_card['name']}**.")
            else:
                await self.update_streak(user_id, correct=False)
                await ctx.send(f"❌ Mauvaise réponse ! C’était **{true_card['name']}**. Série réinitialisée.")

        except Exception as e:
            print("[ERREUR TESTQUESTION]", e)
            await ctx.send("🚨 Une erreur est survenue.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog (avec attribution catégorie)
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TestQuestion(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
