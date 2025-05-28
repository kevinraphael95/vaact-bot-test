# ────────────────────────────────────────────────────────────────────────────────
# ❓ testquestion.py — Commande !testquestion
# Devine une carte Yu-Gi-Oh à partir de sa description parmi 4 cartes du MÊME archétype.
# Version optimisée pour consommation mémoire et temps de chargement.
# Intègre également un système de streak via Supabase.
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
import re
from supabase_client import supabase  # ⚠️ Ton client Supabase préconfiguré

# ────────────────────────────────────────────────────────────────────────────────
# 🔠 Réactions associées aux choix
# ────────────────────────────────────────────────────────────────────────────────
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 Classe principale du Cog
# ────────────────────────────────────────────────────────────────────────────────
class TestQuestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────────
    # 📦 Récupération d’un échantillon de cartes (limité pour ne pas surcharger)
    # ────────────────────────────────────────────────────────────────────────────────
    async def fetch_card_sample(self, limit=150):
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr&num={limit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return data.get("data", [])

    # ────────────────────────────────────────────────────────────────────────────────
    # 🛡️ Masque le nom de la carte dans sa description
    # ────────────────────────────────────────────────────────────────────────────────
    def censor_card_name(self, description: str, card_name: str) -> str:
        escaped = re.escape(card_name)
        return re.sub(escaped, "█" * len(card_name), description, flags=re.IGNORECASE)

    # ────────────────────────────────────────────────────────────────────────────────
    # 📈 Met à jour le streak utilisateur dans la base de données Supabase
    # ────────────────────────────────────────────────────────────────────────────────
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

    # ────────────────────────────────────────────────────────────────────────────────
    # ❓ Commande principale : !testquestion
    # ────────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="testquestion",
        aliases=["tq"],
        help="Devine la carte Yu-Gi-Oh parmi 4 du même archétype."
    )
    async def testquestion(self, ctx):
        try:
            # 🔄 Chargement d’un échantillon de cartes
            cards = await self.fetch_card_sample()
            if not cards:
                await ctx.send("🚨 Erreur lors du chargement des cartes.")
                return

            # 🧠 Sélection intelligente : carte avec archétype + au moins 4 dans le groupe
            group = None
            for _ in range(10):  # Tentatives limitées pour performance
                candidate = random.choice(cards)
                archetype = candidate.get("archetype")
                if not archetype:
                    continue
                same_type_cards = [
                    c for c in cards if c.get("archetype") == archetype and "desc" in c and "name" in c
                ]
                if len(same_type_cards) >= 4:
                    group = same_type_cards
                    break

            if not group:
                await ctx.send("❌ Pas assez de cartes du même archétype. Réessaie plus tard.")
                return

            # 🎯 Choix de la bonne réponse et des fausses
            true_card = random.choice(group)
            wrong_choices = random.sample(
                [c for c in group if c["name"] != true_card["name"]], 3
            )

            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # 📄 Description avec nom masqué
            desc = self.censor_card_name(true_card["desc"], true_card["name"])

            # 🎨 Construction de l'embed
            embed = discord.Embed(
                title=f"🧩 Archétype : {true_card.get('archetype', 'Inconnu')}",
                description=desc[:300] + ("..." if len(desc) > 300 else ""),
                color=discord.Color.teal()
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

            # 🗳️ Ajout des réactions de vote
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
            user_id = str(ctx.author.id)

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
# 🔌 Chargement du Cog
# Attribution de la catégorie "YGO" pour aide personnalisée
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot):
    cog = TestQuestion(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "YGO"
    await bot.add_cog(cog)
test
