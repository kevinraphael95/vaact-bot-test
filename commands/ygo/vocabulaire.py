# ────────────────────────────────────────────────────────────────────────────────
# 📘 vocabulaire.py — Commande interactive !vocabulaire
# Objectif : Affiche les définitions des termes du jeu depuis un fichier JSON
# Catégorie : 🃏 Yu-Gi-Oh!
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données JSON
# ────────────────────────────────────────────────────────────────────────────────
VOCAB_PATH = os.path.join("data", "vocabulaire.json")

def load_vocab():
    """Charge le vocabulaire depuis le fichier JSON."""
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class VocabulaireCommand(commands.Cog):
    """
    📘 Commande !vocabulaire : affiche les définitions des termes liés au jeu.
    Peut être utilisée avec un mot-clé ou sans pour afficher tout le lexique.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="vocabulaire",
        aliases=["voc"],
        help="📘 Affiche la définition des termes du jeu, par mot-clé ou catégorie.",
        description="Affiche les définitions des termes du lexique, avec ou sans filtre par mot-clé."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def vocabulaire(self, ctx: commands.Context, *, mot_cle: str = None):
        """Commande principale !vocabulaire avec système de pagination par réactions."""
        try:
            vocabulaire = load_vocab()
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du chargement du fichier : {e}")
            return

        definitions = []
            for terme, data in vocabulaire.items():
                definition = data.get("definition") if isinstance(data, dict) else data
                synonymes = data.get("synonymes", []) if isinstance(data, dict) else []
                noms_possibles = [terme] + synonymes

                if mot_cle:
                    if any(mot_cle.lower() in mot.lower() for mot in noms_possibles) or mot_cle.lower() in definition.lower():
                        definitions.append((terme, definition))
                else:
                    definitions.append((terme, definition))


        if not definitions:
            await ctx.send("❌ Aucun terme trouvé correspondant à ta recherche.")
            return

        # Pagination
        definitions.sort(key=lambda x: x[1].lower())
        pages = []
        max_par_page = 5

        for i in range(0, len(definitions), max_par_page):
            embed = discord.Embed(
                title="📘 Lexique des termes",
                color=discord.Color.dark_blue()
            )

            for terme, defi in definitions[i:i + max_par_page]:
                embed.add_field(
                    name=f"🔹 {terme}",
                    value=defi,
                    inline=False
                )

            embed.set_footer(text=f"📄 Page {len(pages) + 1}/{(len(definitions) - 1) // max_par_page + 1}")
            pages.append(embed)

        message = await ctx.send(embed=pages[0])
        if len(pages) <= 1:
            return

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == message.id and
                str(reaction.emoji) in ["◀️", "▶️"]
            )

        index = 0
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction, user)

                if str(reaction.emoji) == "▶️":
                    index = (index + 1) % len(pages)
                elif str(reaction.emoji) == "◀️":
                    index = (index - 1) % len(pages)

                await message.edit(embed=pages[index])

            except:
                break  # Timeout

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = VocabulaireCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
