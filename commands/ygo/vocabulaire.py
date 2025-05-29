# ──────────────────────────────────────────────────────────────
# 📁 vocabulaire
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !vocabulaire / !voc
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os
import asyncio

# 📂 Chemin du fichier JSON
VOCAB_PATH = os.path.join("data", "vocabulaire.json")

# 📚 Fonction utilitaire pour charger le vocabulaire
def load_vocabulaire():
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 🔧 Paramètres de pagination
ENTRIES_PAR_PAGE = 6

# ──────────────────────────────────────────────────────────────
# 🔧 COG : VocabulaireCommand
# ──────────────────────────────────────────────────────────────
class VocabulaireCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !vocabulaire | !voc
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="vocabulaire",
        aliases=["voc"],
        help="📖 Affiche les définitions des termes de jeu par catégorie ou mot-clé."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def vocabulaire(self, ctx: commands.Context, *, mot_cle=None):
        vocabulaire = load_vocabulaire()
        definitions = []

        # 🔍 Si recherche par mot-clé
        if mot_cle:
            mot_cle = mot_cle.lower()
            for categorie, termes in vocabulaire.items():
                for terme, definition in termes.items():
                    if mot_cle in terme.lower() or mot_cle in definition.lower():
                        definitions.append((categorie, terme, definition))
            if not definitions:
                await ctx.send("❌ Aucun terme trouvé avec ce mot-clé.")
                return
        else:
            # 📋 Liste complète triée
            for categorie, termes in vocabulaire.items():
                for terme, definition in termes.items():
                    definitions.append((categorie, terme, definition))

        # 📊 Tri alphabétique
        definitions.sort(key=lambda x: x[1].lower())

        # 📄 Pagination
        pages = [definitions[i:i + ENTRIES_PAR_PAGE] for i in range(0, len(definitions), ENTRIES_PAR_PAGE)]
        total_pages = len(pages)

        # 📤 Fonction pour créer un embed à une page donnée
        def get_embed(page_index):
            embed = discord.Embed(
                title="📘 Vocabulaire du jeu",
                description=f"Page {page_index + 1}/{total_pages}",
                color=discord.Color.dark_blue()
            )
            for cat, terme, defi in pages[page_index]:
                embed.add_field(name=f"🟦 {terme} ({cat})", value=defi, inline=False)
            return embed

        current_page = 0
        message = await ctx.send(embed=get_embed(current_page))

        # ➕ Réactions
        if total_pages > 1:
            await message.add_reaction("⏮️")
            await message.add_reaction("⏭️")

            def check(reaction, user):
                return (
                    user == ctx.author and str(reaction.emoji) in ["⏮️", "⏭️"] and reaction.message.id == message.id
                )

            while True:
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                    if str(reaction.emoji) == "⏮️":
                        current_page = (current_page - 1) % total_pages
                    elif str(reaction.emoji) == "⏭️":
                        current_page = (current_page + 1) % total_pages
                    await message.edit(embed=get_embed(current_page))
                    await message.remove_reaction(reaction, ctx.author)
                except asyncio.TimeoutError:
                    break

    # 🏷️ Catégorisation pour !help
    def cog_load(self):
        self.vocabulaire.category = "Outils"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(VocabulaireCommand(bot))
    print("✅ Cog chargé : VocabulaireCommand (catégorie = Outils)")
