# ────────────────────────────────────────────────────────────────────────────────
# 📌 deckmaudit.py — Commande interactive !deckmaudit
# Objectif : Générer un deck maudit absurde avec des cartes anciennes et inutiles
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import requests
import random

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class DeckMaudit(commands.Cog):
    """
    Commande !deckmaudit — Génère un deck absurde et injouable.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def est_maudite(self, carte):
        nom = carte.get("name", "").lower()
        desc = carte.get("desc", "").lower()

        absurdité = any(m in desc for m in [
            "lancez un dé", "pile ou face", "perdez", "infligez", "sacrifiez", "détruisez", "piochez"
        ])
        drôle = any(m in nom for m in [
            "crapaud", "bataille", "magicien fou", "panda", "boulet", "peste", "poubelle", "chat", "bacon", "grenouille"
        ])
        ancien = carte["id"] < 10000000
        commun = all(set_code.get("rarity", "") in ["Common", ""] for set_code in carte.get("card_sets", []) or [])
        return (absurdité or drôle) and ancien and commun

    @commands.command(
        name="deckmaudit",
        help="Génère un deck absurde et injouable (Main + Extra Deck).",
        description="Génère un deck absurde et injouable à base de cartes anciennes et étranges."
    )
    async def deckmaudit(self, ctx: commands.Context):
        """Commande principale !deckmaudit"""

        await ctx.typing()

        try:
            response = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?format=tcg&language=fr")
            cartes = response.json()["data"]

            main_deck = []
            extra_deck = []

            for carte in cartes:
                if not self.est_maudite(carte):
                    continue
                if carte["type"] in ["Fusion Monster", "Synchro Monster", "Xyz Monster", "Link Monster"]:
                    extra_deck.append(carte)
                else:
                    main_deck.append(carte)

            deck_final = random.sample(main_deck, min(40, len(main_deck)))
            extra_final = random.sample(extra_deck, min(10, len(extra_deck)))

            # Création de l'embed
            embed = discord.Embed(
                title="☠️ Deck Maudit Aléatoire",
                description="Voici un deck complètement injouable composé de cartes étranges, absurdes, et très vieilles !",
                color=discord.Color.dark_purple()
            )
            embed.add_field(
                name=f"🃏 Main Deck ({len(deck_final)} cartes)",
                value="\n".join(f"• {c['name']}" for c in deck_final),
                inline=False
            )
            embed.add_field(
                name=f"💀 Extra Deck ({len(extra_final)} cartes)",
                value="\n".join(f"• {c['name']}" for c in extra_final) if extra_final else "Aucune carte absurde trouvée !",
                inline=False
            )
            embed.set_footer(text="Deck totalement injouable. À ne pas utiliser sérieusement 😈")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR deckmaudit] {e}")
            await ctx.send("❌ Une erreur est survenue lors de la génération du deck maudit.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = DeckMaudit(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
