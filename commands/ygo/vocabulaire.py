# ──────────────────────────────────────────────────────────────
# 📁 vocabulaire.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !vocabulaire
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os

# ──────────────────────────────────────────────────────────────
# 🔧 COG : VocabulaireCommand
# ──────────────────────────────────────────────────────────────
class VocabulaireCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot
        self.vocab_path = os.path.join("data", "vocabulaire.json")  # 📂 Chemin du fichier

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !vocabulaire / !voc
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="vocabulaire",
        aliases=["voc"],  # 🔁 Alias
        help="📘 Affiche la définition des termes du jeu, par mot-clé ou catégorie."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Anti-spam
    async def vocabulaire(self, ctx: commands.Context, *, mot_cle: str = None):
        # 📥 Chargement des données
        try:
            with open(self.vocab_path, "r", encoding="utf-8") as f:
                vocabulaire = json.load(f)
        except Exception as e:
            return await ctx.send(f"❌ Erreur lors du chargement du vocabulaire : {e}")

        # 📚 Compilation des définitions
        definitions = []
        for categorie, termes in vocabulaire.items():
            for terme, data in termes.items():
                if isinstance(data, dict):
                    definition = data.get("definition", "❌ Pas de définition.")
                    synonymes = data.get("synonymes", [])
                else:
                    definition = data
                    synonymes = []

                ensemble_termes = [terme] + synonymes

                if mot_cle:
                    for alias in ensemble_termes:
                        if mot_cle.lower() in alias.lower() or mot_cle.lower() in definition.lower():
                            definitions.append((categorie, terme, definition))
                            break  # ✅ Un seul ajout par terme
                else:
                    definitions.append((categorie, terme, definition))

        if not definitions:
            return await ctx.send("❌ Aucun terme trouvé correspondant à ta recherche.")

        # 📄 Pagination
        definitions.sort(key=lambda x: x[1].lower())  # 🔤 Tri alphabétique
        pages = []
        max_par_page = 5  # 📌 Nombre de définitions par page
        for i in range(0, len(definitions), max_par_page):
            chunk = definitions[i:i + max_par_page]
            embed = discord.Embed(
                title="📘 Lexique des termes",
                color=discord.Color.dark_blue()
            )
            for cat, terme, defi in chunk:
                embed.add_field(name=f"🔹 {terme} ({cat})", value=defi, inline=False)
            embed.set_footer(text=f"📄 Page {len(pages)+1}/{(len(definitions)-1)//max_par_page+1}")
            pages.append(embed)

        # ▶️ Navigation par réactions
        message = await ctx.send(embed=pages[0])
        if len(pages) <= 1:
            return

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["◀️", "▶️"]
                and reaction.message.id == message.id
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
                break

    # 🏷️ Catégorisation personnalisée pour !help
    def cog_load(self):
        self.vocabulaire.category = "📖 Vocabulaire"

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    On ajoute aussi manuellement une catégorie "📖 Vocabulaire" pour l’affichage dans !help.
    """
    cog = VocabulaireCommand(bot)

    # 🗂️ Définir la catégorie pour toutes les commandes de ce cog
    for command in cog.get_commands():
        command.category = "📖 Vocabulaire"

    await bot.add_cog(cog)
