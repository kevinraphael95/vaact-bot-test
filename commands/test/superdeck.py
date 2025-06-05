# ────────────────────────────────────────────────────────────────────────────────
# 📌 superdeck.py — Commande interactive !deckmaudit
# Objectif : Générer un deck "maudit" avec des vraies cartes YGODeckPro, un peu absurdes,
#           et proposer une mini-stratégie amusante.
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import random

class superdeck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Limite de 300 cartes max pour économiser ressources
        self.api_base = "https://ygodeckpro.fr/api/cards?limit=300"

    async def fetch_some_cards(self):
        """
        Récupère jusqu'à 300 cartes disponibles via l'API YGODeckPro.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_base) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("data", [])

    def filter_maudit_cards(self, cards):
        maudit_cards = []
        for c in cards:
            atk = c.get("atk", 0)
            defn = c.get("def", 0)
            card_type = c.get("type", "").lower()
            desc = c.get("desc", "").lower()

            faible_monstre = (card_type == "monster" and atk <= 500 and defn <= 500)
            piege_inutile = (card_type == "trap" and ("contre" not in desc and "annuler" not in desc))
            magie_faible = (card_type == "spell" and ("pioche" not in desc and "recuperer" not in desc))

            if faible_monstre or piege_inutile or magie_faible:
                maudit_cards.append(c)
        return maudit_cards

    def compose_deck(self, maudit_cards):
        if len(maudit_cards) < 20:
            return random.sample(maudit_cards, len(maudit_cards))
        return random.sample(maudit_cards, 20)

    def build_strategy_text(self, deck):
        nb_piege = sum(1 for c in deck if c.get("type", "").lower() == "trap")
        nb_monstre_faible = sum(1 for c in deck if c.get("type", "").lower() == "monster" and c.get("atk", 0) <= 500)

        texte = "🃏 **Stratégie du deck maudit** 🃏\n"
        if nb_piege > 5:
            texte += "- Cache-toi derrière tes pièges inutiles et espère que ton adversaire s'ennuie !\n"
        if nb_monstre_faible > 5:
            texte += "- Envoie tes monstres faibles en première ligne, pour qu'ils fassent office de boucliers humains.\n"
        if nb_piege <= 5 and nb_monstre_faible <= 5:
            texte += "- Un peu de tout, mais surtout n'oublie pas de prier pour la chance.\n"

        texte += "Essaie de jouer lentement, ton adversaire pourrait abandonner par ennui...\n"
        return texte

    @commands.command(
        name="superdeck",
        help="Génère un deck aléatoire avec cartes réelles YGODeckPro.",
        description="Commande amusante pour générer un deck Yu-Gi-Oh! rigolo et absurde."
    )
    async def deckmaudit(self, ctx: commands.Context):
        try:
            await ctx.trigger_typing()
            all_cards = await self.fetch_some_cards()
            if all_cards is None:
                return await ctx.send("❌ Impossible de récupérer les cartes depuis YGODeckPro.")

            maudit_cards = self.filter_maudit_cards(all_cards)
            if not maudit_cards:
                return await ctx.send("❌ Aucun deck maudit trouvé... (impossible)")

            deck = self.compose_deck(maudit_cards)

            embed = discord.Embed(
                title="🃏 Deck Maudit généré par Atem 🃏",
                description="Voici un deck maudit bien absurde, prépare-toi à perdre... ou à t'amuser !",
                color=discord.Color.red()
            )

            for c in deck:
                name = c.get("name", "???")
                type_ = c.get("type", "Inconnu")
                desc = c.get("desc", "")
                atk = c.get("atk", "?")
                defn = c.get("def", "?")
                desc_short = (desc[:97] + "...") if len(desc) > 100 else desc

                embed.add_field(
                    name=f"{name} [{type_}] (ATK:{atk} DEF:{defn})",
                    value=desc_short,
                    inline=False
                )

            embed.add_field(name="Stratégie (très douteuse)", value=self.build_strategy_text(deck), inline=False)
            embed.set_footer(text="N'oublie pas, ce deck est maudit, joue-le à tes risques et périls ! 🎲")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR deckmaudit] {e}")
            await ctx.send("❌ Une erreur est survenue lors de la génération du deck maudit.")

async def setup(bot: commands.Bot):
    cog = superdeck(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
