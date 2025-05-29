# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Question.py — Commande !question
# Objectif : Faire deviner une carte Yu-Gi-Oh à partir de sa description parmi 4 propositions
# Les propositions partagent un archétype ou un type avec la vraie carte
# Bonus : suivi de série de bonnes réponses (streak) par utilisateur
# ────────────────────────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp  # Pour faire des requêtes HTTP asynchrones
import random   # Pour mélanger/sélectionner aléatoirement
import asyncio  # Pour gérer les délais et timeouts
import re       # Pour censurer le nom de la carte dans la description

from supabase_client import supabase  # Client Supabase pour stocker les streaks

# Réactions proposées pour les 4 réponses possibles
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ───────────────────────────────────────────────────────────────────────────────
# 📘 Classe principale du Cog de commande !question
# ───────────────────────────────────────────────────────────────────────────────
class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Référence au bot principal

    # ───────────────────────────────────────────────────────────────────────────
    # 🔄 Fonction utilitaire : Récupère un échantillon de cartes (aléatoire)
    # ───────────────────────────────────────────────────────────────────────────
    async def fetch_card_sample(self, limit=100):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []  # Si l'API échoue
                data = await resp.json()
                return random.sample(data.get("data", []), min(limit, len(data.get("data", []))))

    # ───────────────────────────────────────────────────────────────────────────
    # ✂️ Fonction utilitaire : Remplace le nom de la carte par █████ dans la description
    # ───────────────────────────────────────────────────────────────────────────
    def censor_card_name(self, desc: str, name: str) -> str:
        return re.sub(re.escape(name), "█" * len(name), desc, flags=re.IGNORECASE)

    # ───────────────────────────────────────────────────────────────────────────
    # 🔁 Met à jour la série de bonnes réponses (streak) de l'utilisateur
    # ───────────────────────────────────────────────────────────────────────────
    async def update_streak(self, user_id: str, correct: bool):
        # Récupération du streak actuel
        data = supabase.table("ygo_streaks").select("*").eq("user_id", user_id).execute()
        row = data.data[0] if data.data else None

        if row:
            current = row["current_streak"]
            best = row.get("best_streak", 0)
            new_streak = current + 1 if correct else 0
            update_data = {"current_streak": new_streak}

            # Met à jour le meilleur streak si nécessaire
            if correct and new_streak > best:
                update_data["best_streak"] = new_streak

            # Mise à jour Supabase
            supabase.table("ygo_streaks").update(update_data).eq("user_id", user_id).execute()
        else:
            # Création de l’entrée si nouvelle
            supabase.table("ygo_streaks").insert({
                "user_id": user_id,
                "current_streak": 1 if correct else 0,
                "best_streak": 1 if correct else 0
            }).execute()

    # ───────────────────────────────────────────────────────────────────────────
    # 🔮 Commande principale !question
    # ───────────────────────────────────────────────────────────────────────────
    @commands.command(name="Question", aliases=["q"], help="Devine le nom de la carte Yu-Gi-Oh parmi 4 choix.")
    @commands.cooldown(1, 8, commands.BucketType.user)  # Cooldown de 8s par utilisateur
    async def Question(self, ctx):
        try:
            # Étape 0 — On récupère un échantillon de cartes
            cards = await self.fetch_card_sample()
            random.shuffle(cards)

            # On cherche une carte principale avec un archétype, une description et un nom
            main_card = next((c for c in cards if c.get("archetype") and "desc" in c and "name" in c), None)
            if not main_card:
                await ctx.send("❌ Aucune carte valide trouvée.")
                return

            archetype = main_card["archetype"]
            main_type = main_card.get("type", "").lower()

            # Détermine le type global (monstre/magie/piège)
            type_keyword = "monstre" if "monstre" in main_type else ("magie" if "magie" in main_type else "piège")

            group = []  # Liste des cartes pour les mauvaises réponses

            # Étape 1 — Même archétype + type EXACT
            if archetype:
                url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?archetype={archetype}&language=fr"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            arch_cards = data.get("data", [])

                            group = [
                                c for c in arch_cards
                                if c.get("name") != main_card["name"]
                                and "desc" in c
                                and c.get("type", "").lower() == main_type
                            ]

                            # Étape 2 — Même archétype + type GLOBAL
                            if len(group) < 3:
                                group = [
                                    c for c in arch_cards
                                    if c.get("name") != main_card["name"]
                                    and "desc" in c
                                    and type_keyword in c.get("type", "").lower()
                                ]

            # Étape 3 — Même type GLOBAL dans l’échantillon de base
            if len(group) < 3:
                group = [
                    c for c in cards
                    if c.get("name") != main_card["name"]
                    and "desc" in c
                    and type_keyword in c.get("type", "").lower()
                ]

            # Étape 4 — Fallback : dans un set étendu de 300 cartes aléatoires
            if len(group) < 3:
                full_cards = await self.fetch_card_sample(limit=300)
                group = [
                    c for c in full_cards
                    if c.get("name") != main_card["name"]
                    and "desc" in c
                    and type_keyword in c.get("type", "").lower()
                ]

            # Si on n’a toujours pas 3 propositions : abandon
            if len(group) < 3:
                await ctx.send("❌ Pas assez de cartes similaires trouvées.")
                return

            # Préparation des propositions (1 vraie + 3 mauvaises)
            true_card = main_card
            wrong_choices = random.sample(group, 3)
            all_choices = [true_card["name"]] + [c["name"] for c in wrong_choices]
            random.shuffle(all_choices)

            # Masquage du nom dans la description
            desc = self.censor_card_name(true_card["desc"], true_card["name"])

            # Image miniature
            image_url = true_card.get("card_images", [{}])[0].get("image_url_cropped")

            # Création de l’embed Discord
            embed = discord.Embed(
                title="🧠 Quelle est cette carte ?",
                description=(
                    f"📘 **Type :** {true_card.get('type', '—')}\n"
                    f"🔍 **Description :**\n*{desc[:500]}{'...' if len(desc) > 300 else ''}*"
                ),
                color=discord.Color.purple()
            )

            embed.set_author(name="YGO Quiz", icon_url="https://cdn-icons-png.flaticon.com/512/361/361678.png")
            if image_url:
                embed.set_thumbnail(url=image_url)

            embed.add_field(name="🔹 Archétype", value=f"||{archetype}||", inline=False)

            # Stats visibles si c’est un monstre
            if main_type.startswith("monstre"):
                embed.add_field(name="💥 ATK", value=str(true_card.get("atk", "—")), inline=True)
                embed.add_field(name="🛡️ DEF", value=str(true_card.get("def", "—")), inline=True)
                embed.add_field(name="⭐ Niveau", value=str(true_card.get("level", "—")), inline=True)
                embed.add_field(name="🌪️ Attribut", value=true_card.get("attribute", "—"), inline=True)

            # Ajout des choix
            options = "\n".join(f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices))
            embed.add_field(name="❓ Choisis la bonne carte :", value=options, inline=False)
            embed.set_footer(text="Réagis ci-dessous avec la bonne réponse 👇")

            # Envoi de la question
            msg = await ctx.send(embed=embed)
            for emoji in REACTIONS[:4]:
                await msg.add_reaction(emoji)

            # Attente de la réponse de l'utilisateur
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in REACTIONS

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            selected_index = REACTIONS.index(str(reaction.emoji))
            correct_index = all_choices.index(true_card["name"])
            user_id = str(ctx.author.id)

            # Résultat final : succès ou échec
            if selected_index == correct_index:
                await self.update_streak(user_id, correct=True)
                await ctx.send(f"✅ Bonne réponse ! C’était bien **{true_card['name']}**.")
            else:
                await self.update_streak(user_id, correct=False)
                await ctx.send(f"❌ Mauvaise réponse. C’était **{true_card['name']}**.")

        except Exception as e:
            # En cas d'erreur non prévue
            print("[ERREUR Question]", e)
            await ctx.send("🚨 Une erreur est survenue.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Question(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"  # Organisation dans l’aide du bot
    await bot.add_cog(cog)
