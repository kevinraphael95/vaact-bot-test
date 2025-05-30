# ────────────────────────────────────────────────────────────────────────────────
# 📁 illustration.py — Commande !illustration
# ────────────────────────────────────────────────────────────────────────────────
# Ce module permet aux utilisateurs de deviner une carte Yu-Gi-Oh! à partir
# de son image croppée, avec un quiz interactif basé sur les réactions.
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                            # Pour créer des embeds
from discord.ext import commands          # Pour les commandes et les cogs
import aiohttp                            # Pour envoyer des requêtes HTTP asynchrones
import random                             # Pour choisir des cartes et mélanger les choix
import asyncio                            # Pour gérer le temps d’attente des réponses

# ────────────────────────────────────────────────────────────────────────────────
# 🔤 CONSTANTES
# ────────────────────────────────────────────────────────────────────────────────
REACTIONS = ["🇦", "🇧", "🇨", "🇩"]         # Réactions possibles pour le quiz

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 COG : IllustrationCommand
# ────────────────────────────────────────────────────────────────────────────────
class IllustrationCommand(commands.Cog):
    """
    🎮 Ce cog contient un jeu où les utilisateurs doivent deviner une carte
    Yu-Gi-Oh! à partir de son image partielle (croppée).
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 On stocke l'instance du bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔄 FONCTION : fetch_all_cards
    # ────────────────────────────────────────────────────────────────────────────
    async def fetch_all_cards(self):
        """📥 Récupère toutes les cartes Yu-Gi-Oh! en langue française."""
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []  # 🚫 Erreur lors de la récupération
                data = await resp.json()

        return data.get("data", [])  # ✅ Retourne la liste de cartes

    # ────────────────────────────────────────────────────────────────────────────
    # 🧩 FONCTION : get_similar_cards
    # ────────────────────────────────────────────────────────────────────────────
    async def get_similar_cards(self, all_cards, true_card):
        """
        🔄 Trouve jusqu’à 3 cartes similaires à celle à deviner :
        - Par archétype (priorité)
        - Sinon, par type
        """
        archetype = true_card.get("archetype")
        card_type = true_card.get("type", "")

        # 🎯 Filtrage par archétype si disponible
        if archetype:
            group = [
                card for card in all_cards
                if card.get("archetype") == archetype and card["name"] != true_card["name"]
            ]
        else:
            # 🪪 Sinon, filtrage par type général
            group = [
                card for card in all_cards
                if card.get("type") == card_type and card["name"] != true_card["name"]
            ]

        # 🎲 Sélection aléatoire de 3 cartes au maximum
        return random.sample(group, k=min(3, len(group))) if group else []

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !illustration
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="illustration",
        aliases=["illu"],
        help="🖼️ Devine une carte Yu-Gi-Oh à partir de son image croppée."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def illustration(self, ctx: commands.Context):
        """
        🎮 Lance un mini-jeu où l’utilisateur doit reconnaître une carte à partir
        d’une image croppée. Il a 4 propositions.
        """

        try:
            # 📥 Récupération des cartes depuis l’API
            all_cards = await self.fetch_all_cards()
            if not all_cards:
                await ctx.send("🚨 Impossible de récupérer les cartes depuis l’API.")
                return

            # 🃏 Sélection d’une carte avec une image croppée
            true_card = random.choice([
                card for card in all_cards
                if "image_url_cropped" in card.get("card_images", [{}])[0]
            ])
            image_url = true_card["card_images"][0].get("image_url_cropped")

            if not image_url:
                await ctx.send("🚫 Cette carte ne possède pas d’image croppée.")
                return

            # 🧩 Récupération de cartes similaires
            similar_cards = await self.get_similar_cards(all_cards, true_card)

            if len(similar_cards) < 3:
                await ctx.send("❌ Pas assez de cartes similaires pour générer des choix.")
                return

            # 🪄 Création des propositions aléatoires
            all_choices = [true_card["name"]] + [card["name"] for card in similar_cards]
            random.shuffle(all_choices)
            correct_index = all_choices.index(true_card["name"])

            # 🖼️ Construction de l’embed du quiz
            embed = discord.Embed(
                title="🖼️ Devine la carte à partir de son illustration !",
                description="\n".join(
                    f"{REACTIONS[i]} {name}" for i, name in enumerate(all_choices)
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url=image_url)  # 🖼️ Ajoute l’image croppée
            embed.set_footer(text=f"🔹 Archétype : ||{true_card.get('archetype', 'Aucun')}||")

            # 📤 Envoi de l'embed
            msg = await ctx.send(embed=embed)

            # 🟡 Ajout des réactions pour les choix
            for emoji in REACTIONS[:len(all_choices)]:
                await msg.add_reaction(emoji)

            # ✅ Vérifie que la réaction vient bien de l’auteur du message
            def check(reaction, user):
                return (
                    user == ctx.author and
                    reaction.message.id == msg.id and
                    str(reaction.emoji) in REACTIONS
                )

            try:
                # ⏳ Attend la réaction de l’utilisateur
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return

            # 🧠 Analyse de la réponse
            selected_index = REACTIONS.index(str(reaction.emoji))

            if selected_index == correct_index:
                await ctx.send(f"✅ Bonne réponse ! C’était **{true_card['name']}**.")
            else:
                await ctx.send(f"❌ Mauvaise réponse ! C’était **{true_card['name']}**.")

        except Exception as e:
            print("[ERREUR ILLUSTRATION]", e)
            await ctx.send("🚨 Une erreur est survenue pendant le quiz.")

    # ────────────────────────────────────────────────────────────────────────────
    # 🏷️ Catégorie personnalisée pour la commande dans !help
    # ────────────────────────────────────────────────────────────────────────────
    def cog_load(self):
        self.illustration.category = "🃏 Yu-Gi-Oh!"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    📦 Fonction exécutée au chargement du cog pour l’ajouter au bot.
    """
    await bot.add_cog(IllustrationCommand(bot))
    print("✅ Cog chargé : IllustrationCommand (catégorie = 🃏 Yu-Gi-Oh!)")
