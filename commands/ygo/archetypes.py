# ──────────────────────────────────────────────────────────────
# 📁 archetypes.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !archetype
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os
import asyncio

# ──────────────────────────────────────────────────────────────
# 🔧 COG : ArchetypeCommand
# ──────────────────────────────────────────────────────────────
class ArchetypeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot
        self.data_file = "data/archetypes.json"
        self.archetypes = self.load_archetypes()

    # 📥 Chargement JSON
    def load_archetypes(self):
        if not os.path.exists(self.data_file):
            return {}
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !archetype
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="archetype",
        aliases=["archétype", "arch"],
        help="📚 Affiche la liste des archétypes ou détail d'un archétype."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Anti-spam
    async def archetype(self, ctx: commands.Context, *args):
        if not self.archetypes:
            return await ctx.send("⚠️ Aucun archétype chargé.")

        # 🔍 Recherche spécifique
        if args:
            query = " ".join(args).lower()
            found = None
            for name, info in self.archetypes.items():
                if query in name.lower():
                    found = (name, info)
                    break

            if found:
                embed = discord.Embed(
                    title=f"📘 Archétype : {found[0]}",
                    description=found[1]["description"],
                    color=discord.Color.blue()
                )
                return await ctx.send(embed=embed)
            else:
                return await ctx.send("❌ Archétype non trouvé.")

        # 📄 Liste paginée
        pages = []
        archetype_names = sorted(self.archetypes.keys())
        chunk_size = 5

        for i in range(0, len(archetype_names), chunk_size):
            chunk = archetype_names[i:i+chunk_size]
            desc = "\n".join([f"• **{name}**" for name in chunk])
            embed = discord.Embed(
                title=f"📚 Archétypes ({i + 1}-{min(i + chunk_size, len(archetype_names))} sur {len(archetype_names)})",
                description=desc,
                color=discord.Color.green()
            )
            pages.append(embed)

        current = 0
        message = await ctx.send(embed=pages[current])

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                await message.remove_reaction(reaction.emoji, user)

                if str(reaction.emoji) == "➡️" and current < len(pages) - 1:
                    current += 1
                    await message.edit(embed=pages[current])
                elif str(reaction.emoji) == "⬅️" and current > 0:
                    current -= 1
                    await message.edit(embed=pages[current])
            except asyncio.TimeoutError:
                break

    # 🏷️ Catégorisation pour !help
    def cog_load(self):
        self.archetype.category = "Stratégie & Archétypes"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ArchetypeCommand(bot))
    print("✅ Cog chargé : ArchetypeCommand (catégorie = 🃏 Yu-Gi-Oh!")")
