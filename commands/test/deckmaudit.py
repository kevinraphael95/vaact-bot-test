# ────────────────────────────────────────────────────────────────────────────────
# 📌 deckmaudit.py — Commande interactive !deckmaudit
# Objectif : Générer un deck Yu-Gi-Oh! absurde, privilégiant vieilles cartes, avec Extra Deck
# Catégorie : teest
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import random
import re

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class DeckMaudit(commands.Cog):
    """
    Commande !deckmaudit — Génère un deck Yu-Gi-Oh absurde avec vieilles cartes et Extra Deck.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_cards_sample(self):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                cards = data.get("data", [])
                random.shuffle(cards)
                sample = cards[:300]
                return sample

    def extract_year(self, card):
        # Tente d'extraire l'année la plus ancienne dans les sets de la carte
        sets = card.get("card_sets")
        if not sets:
            return None
        years = []
        for s in sets:
            set_name = s.get("set_name", "")
            m = re.search(r"(19|20)\d{2}", set_name)
            if m:
                years.append(int(m.group()))
        if years:
            return min(years)
        return None

    def poids_carte(self, card):
        # Double poids si carte sortie avant 2005
        year = self.extract_year(card)
        if year and year < 2005:
            return 2
        return 1

    def filtrer_cartes_monstres_sorts_pièges(self, cards):
        filtered = []
        for c in cards:
            typ = c.get("type", "").lower()
            if any(t in typ for t in ["monster", "spell", "trap"]):
                filtered.append(c)
        return filtered

    def filtrer_extra_deck(self, cards, archetype=None):
        extra_types = ["fusion", "synchro", "xyz", "link"]
        filtered = []
        for c in cards:
            typ = c.get("type", "").lower()
            if any(x in typ for x in extra_types):
                if archetype:
                    if c.get("archetype") == archetype:
                        filtered.append(c)
                else:
                    filtered.append(c)
        return filtered

    def composer_deck(self, cards, taille=40):
        # Compose un deck de taille fixe en respectant max 3 exemplaires par carte,
        # fallback pour garantir toujours la taille demandée
        weighted_pool = []
        for c in cards:
            w = self.poids_carte(c)
            weighted_pool.extend([c] * w)
        if not weighted_pool:
            return []

        deck = []
        counts = {}
        tries = 0
        max_tries = taille * 10  # Pour éviter boucle infinie
        while len(deck) < taille and tries < max_tries:
            tries += 1
            c = random.choice(weighted_pool)
            name = c.get("name")
            if counts.get(name, 0) >= 3:
                continue
            deck.append(c)
            counts[name] = counts.get(name, 0) + 1

        # Si pas assez, complète avec n'importe quoi au pif
        while len(deck) < taille:
            c = random.choice(cards)
            name = c.get("name")
            deck.append(c)
            counts[name] = counts.get(name, 0) + 1

        return deck

    def trouver_archetype_majoritaire(self, deck):
        counts = {}
        for c in deck:
            arch = c.get("archetype")
            if arch:
                counts[arch] = counts.get(arch, 0) + 1
        if not counts:
            return None
        return max(counts, key=counts.get)

    @commands.command(
        name="deckmaudit",
        help="Génère un deck Yu-Gi-Oh! maudit avec Extra Deck.",
        description="Génère un deck absurde avec des vieilles cartes privilégiées et un Extra Deck cohérent."
    )
    async def deckmaudit(self, ctx: commands.Context):
        await ctx.trigger_typing()
        try:
            sample_cards = await self.fetch_cards_sample()
            if not sample_cards:
                await ctx.send("❌ Impossible de récupérer les cartes.")
                return

            # Filtrer cartes pour le deck principal (monstres, sorts, pièges)
            main_pool = self.filtrer_cartes_monstres_sorts_pièges(sample_cards)
            deck_main = self.composer_deck(main_pool, taille=40)

            archetype = self.trouver_archetype_majoritaire(deck_main)

            # Filtrer cartes Extra Deck selon archetype
            extra_pool = self.filtrer_extra_deck(sample_cards, archetype)
            if len(extra_pool) < 15:
                # fallback au pif dans tout l'extra deck
                extra_pool = self.filtrer_extra_deck(sample_cards)

            deck_extra = self.composer_deck(extra_pool, taille=15)

            # Préparer embed
            embed = discord.Embed(
                title="💀 Deck Maudit par Atem 💀",
                description=(
                    f"Archétype majoritaire détecté : **{archetype or 'Aucun'}**\n"
                    f"Deck principal : {len(deck_main)} cartes\n"
                    f"Extra Deck : {len(deck_extra)} cartes"
                ),
                color=discord.Color.dark_red()
            )

            def format_carte(c):
                name = c.get("name", "???")
                typ = c.get("type", "Inconnu")
                atk = c.get("atk", "?")
                defe = c.get("def", "?")
                desc = c.get("desc", "")
                short_desc = (desc[:90] + "...") if len(desc) > 100 else desc
                return f"**{name}** [{typ}] (ATK:{atk} DEF:{defe})\n{short_desc}"

            # Pour éviter un embed trop lourd, on affiche juste les noms des cartes
            main_names = "\n".join(f"• {c.get('name', '???')}" for c in deck_main)
            extra_names = "\n".join(f"• {c.get('name', '???')}" for c in deck_extra)

            embed.add_field(name="Deck Principal (40 cartes)", value=main_names, inline=False)
            embed.add_field(name="Extra Deck (15 cartes)", value=extra_names, inline=False)

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
