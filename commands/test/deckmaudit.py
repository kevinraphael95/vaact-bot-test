# ────────────────────────────────────────────────────────────────────────────────
# 📌 deckmaudit.py — Commande interactive !deckmaudit
# Objectif : Générer un deck "maudit" avec des vraies cartes YGODeckPro absurdes
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random

class DeckMaudit(commands.Cog):
    """
    Commande !deckmaudit — Génère un deck maudit absurde et perdant à coup sûr.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_cards_by_popularity(self, view_threshold: int):
        """Récupère jusqu'à 300 cartes ayant un nombre de vues <= threshold."""
        url = f"https://ygodeckpro.fr/api/cards?limit=300&views[lte]={view_threshold}&random=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("data", [])

    def is_card_maudite(self, c):
        """Détermine si une carte est 'maudite' (inutilisable, absurde)."""
        atk = c.get("atk", 0)
        defn = c.get("def", 0)
        card_type = c.get("type", "").lower()
        desc = c.get("desc", "").lower()

        faible_monstre = (card_type == "monster" and atk <= 500 and defn <= 500)
        piege_inutile = (card_type == "trap" and "annuler" not in desc and "contre" not in desc and "effet" not in desc)
        magie_nulle = (card_type == "spell" and "pioche" not in desc and "recuperer" not in desc and "search" not in desc)

        return faible_monstre or piege_inutile or magie_nulle

    def filtrer_cartes_maudites(self, cartes):
        return [c for c in cartes if self.is_card_maudite(c)]

    def composer_deck(self, maudites):
        return random.sample(maudites, min(20, len(maudites)))

    def generer_strategie(self, deck):
        nb_piege = sum(1 for c in deck if c.get("type", "").lower() == "trap")
        nb_monstre_faible = sum(1 for c in deck if c.get("type", "").lower() == "monster" and c.get("atk", 0) <= 500)

        texte = "🃏 **Stratégie du deck maudit** 🃏\n"
        if nb_piege > 5:
            texte += "- Cache-toi derrière tes pièges inutiles et espère que ton adversaire s'endorme !\n"
        if nb_monstre_faible > 5:
            texte += "- Envoie tes monstres faibles en première ligne, comme chair à canon.\n"
        if nb_piege <= 5 and nb_monstre_faible <= 5:
            texte += "- C’est un chaos total, mais avec style. Peut-être.\n"
        texte += "Joue lentement. Très lentement. L'abandon est ta victoire...\n"
        return texte

    @commands.command(
        name="deckmaudit",
        help="Génère un deck aléatoire avec des cartes réelles YGODeckPro absurdes.",
        description="Commande fun pour générer un deck Yu-Gi-Oh! injouable mais drôle."
    )
    async def deckmaudit(self, ctx: commands.Context):
        """Commande principale pour générer un deck maudit."""
        try:
            await ctx.trigger_typing()

            seuil_vues = 50
            max_vues = 1000
            deck = None

            while seuil_vues <= max_vues:
                cartes = await self.fetch_cards_by_popularity(seuil_vues)
                if not cartes:
                    seuil_vues += 100
                    continue

                maudites = self.filtrer_cartes_maudites(cartes)
                if len(maudites) >= 10:
                    deck = self.composer_deck(maudites)
                    break
                seuil_vues += 100

            if not deck:
                return await ctx.send("❌ Impossible de générer un deck maudit avec les cartes disponibles.")

            embed = discord.Embed(
                title="💀 Deck Maudit généré par Atem 💀",
                description="Voici un deck tellement nul que même Exodia s'en moquerait.",
                color=discord.Color.dark_red()
            )

            for c in deck:
                name = c.get("name", "???")
                type_ = c.get("type", "Inconnu")
                desc = c.get("desc", "")
                atk = c.get("atk", "?")
                defn = c.get("def", "?")
                short_desc = (desc[:97] + "...") if len(desc) > 100 else desc

                embed.add_field(
                    name=f"{name} [{type_}] (ATK:{atk} DEF:{defn})",
                    value=short_desc,
                    inline=False
                )

            embed.add_field(
                name="Stratégie (très douteuse)",
                value=self.generer_strategie(deck),
                inline=False
            )
            embed.set_footer(text="Deck généré uniquement pour les duellistes suicidaires 🎲")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR deckmaudit] {e}")
            await ctx.send("❌ Une erreur est survenue lors de la génération du deck maudit.")

# 🔌 Setup du Cog
async def setup(bot: commands.Bot):
    cog = DeckMaudit(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
