import discord
from discord.ext import commands
import aiohttp
import random
import re

class DeckMaudit(commands.Cog):
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
        # Tente d'extraire année la plus ancienne (par nom set)
        sets = card.get("card_sets")
        if not sets:
            return 9999  # Très récente si aucune info
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
        # On évite "Ultimate Rare", "Secret Rare", etc.
        rare_blacklist = ["Ultimate Rare", "Secret Rare", "Ghost Rare", "Gold Rare"]
        sets = card.get("card_sets") or []
        for s in sets:
            rarity = s.get("set_rarity", "")
            if rarity in rare_blacklist:
                return False
        return True

    def is_main_deck_card(self, card):
        # Carte monstres, sorts ou pièges (exclut Extra Deck)
        typ = card.get("type", "").lower()
        return any(t in typ for t in ["monster", "spell", "trap"]) and not any(x in typ for x in ["fusion", "synchro", "xyz", "link"])

    def is_extra_deck_card(self, card):
        typ = card.get("type", "").lower()
        return any(x in typ for x in ["fusion", "synchro", "xyz", "link"])

    def filter_main_cards(self, cards):
        return [c for c in cards if self.is_main_deck_card(c) and self.no_archetype(c) and self.is_ancient(c) and self.has_low_rarity(c)]

    def filter_extra_cards(self, cards):
        return [c for c in cards if self.is_extra_deck_card(c)]

    def pick_deck(self, pool, size):
        # Prend size cartes aléatoires, max 3 exemplaires par carte
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
        # Remplir si pas assez
        while len(deck) < size:
            c = random.choice(pool)
            deck.append(c)
        return deck

    @commands.command(name="deckmaudit", help="Génère un deck absurde complet, vieilles cartes, pas d'archétype.")
    async def deckmaudit(self, ctx):
        await ctx.trigger_typing()
        cards = await self.fetch_cards()
        if not cards:
            await ctx.send("❌ Impossible de récupérer les cartes.")
            return

        main_pool = self.filter_main_cards(cards)
        if len(main_pool) < 40:
            main_pool = [c for c in cards if self.is_main_deck_card(c)]  # fallback

        extra_pool = self.filter_extra_cards(cards)
        if len(extra_pool) < 15:
            extra_pool = [c for c in cards if self.is_extra_deck_card(c)]  # fallback

        deck_main = self.pick_deck(main_pool, 40)
        deck_extra = self.pick_deck(extra_pool, 15)

        embed = discord.Embed(
            title="💀 Deck Maudit par Atem 💀",
            description="Deck absurde avec vieilles cartes, pas d'archétype et Extra Deck au hasard.",
            color=discord.Color.dark_red()
        )

        main_names = "\n".join(f"• {c.get('name', '???')}" for c in deck_main[:40])
        extra_names = "\n".join(f"• {c.get('name', '???')}" for c in deck_extra[:15])

        embed.add_field(name="Deck Principal (40 cartes)", value=main_names, inline=False)
        embed.add_field(name="Extra Deck (15 cartes)", value=extra_names, inline=False)

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
