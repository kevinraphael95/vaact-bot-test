# ────────────────────────────────────────────────────────────────────────────────
# 📌 deckmaudit.py — Commande interactive !deckmaudit
# Objectif : Générer un deck Yu-Gi-Oh absurde complet, sans archétype et avec vieilles cartes
# Catégorie : Yu-Gi-Oh
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
# 🎛️ Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class DeckMaudit(commands.Cog):
    """
    Commande !deckmaudit — Génère un deck absurde complet,
    vieilles cartes, pas d'archétype, avec Extra Deck aléatoire.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_cards(self):
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return data.get("data", [])

    def extract_year(self, card):
        sets = card.get("card_sets")
        if not sets:
            return 9999
        years = []
        for s in sets:
            name = s.get("set_name", "")
            m = re.search(r"(19|20)\d{2}", name)
            if m:
                years.append(int(m.group()))
        return min(years) if years else 9999

    def is_ancient(self, card):
        return self.extract_year(card) <= 2008

    def no_archetype(self, card):
        return card.get("archetype") is None

    def has_low_rarity(self, card):
        blacklist = ["Ultimate Rare", "Secret Rare", "Ghost Rare", "Gold Rare"]
        sets = card.get("card_sets") or []
        for s in sets:
            if s.get("set_rarity") in blacklist:
                return False
        return True

    def is_main_deck_card(self, card):
        typ = card.get("type", "").lower()
        # Monstre, sort ou piège mais pas Extra Deck
        return any(t in typ for t in ["monster", "spell", "trap"]) and not any(x in typ for x in ["fusion", "synchro", "xyz", "link"])

    def is_extra_deck_card(self, card):
        typ = card.get("type", "").lower()
        return any(x in typ for x in ["fusion", "synchro", "xyz", "link"])

    def pick_deck(self, pool, size):
        deck = []
        counts = {}
        tries = 0
        max_tries = size * 20
        while len(deck) < size and tries < max_tries:
            tries += 1
            c = random.choice(pool)
            name = c.get("name")
            if counts.get(name, 0) < 3:
                deck.append(c)
                counts[name] = counts.get(name, 0) + 1
        while len(deck) < size:
            deck.append(random.choice(pool))
        return deck

    @commands.command(
        name="deckmaudit",
        help="Génère un deck absurde complet, vieilles cartes, sans archétype.",
        description="Crée un deck principal de 40 cartes et un extra deck de 15 cartes absurdes."
    )
    async def deckmaudit(self, ctx: commands.Context):
        await ctx.trigger_typing()
        cards = await self.fetch_cards()
        if not cards:
            await ctx.send("❌ Impossible de récupérer les cartes.")
            return

        main_pool = [c for c in cards if self.is_main_deck_card(c) and self.no_archetype(c) and self.is_ancient(c) and self.has_low_rarity(c)]
        if len(main_pool) < 40:
            main_pool = [c for c in cards if self.is_main_deck_card(c)]  # fallback

        extra_pool = [c for c in cards if self.is_extra_deck_card(c)]
        if len(extra_pool) < 15:
            extra_pool = [c for c in cards if self.is_extra_deck_card(c)]  # fallback

        deck_main = self.pick_deck(main_pool, 40)
        deck_extra = self.pick_deck(extra_pool, 15)

        embed = discord.Embed(
            title="💀 Deck Maudit généré par Atem",
            description="Deck absurde avec vieilles cartes, pas d'archétype et Extra Deck aléatoire.",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Deck Principal (40 cartes)", value="\n".join(f"• {c.get('name', '???')}" for c in deck_main), inline=False)
        embed.add_field(name="Extra Deck (15 cartes)", value="\n".join(f"• {c.get('name', '???')}" for c in deck_extra), inline=False)

        await ctx.send(embed=embed)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = DeckMaudit(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
