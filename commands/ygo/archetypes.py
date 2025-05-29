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
    # 🔹 COMMANDE : !archetype / !archétype / !arch
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="archetype",
        aliases=["archétype", "arch"],
        help="📚 Affiche la liste des archétypes ou le détail d’un archétype spécifique."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Anti-spam
    async def archetype(self, ctx: commands.Context, *args):
        if not self.archetypes:
            return await ctx.send("⚠️ Aucun archétype chargé.")

        # 🔍 Recherche d’un archétype spécifique
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
                    description=found[1].get("description", "Aucune description disponible."),
                    color=discord.Color.blue()
                )
                return await ctx.send(embed=embed)
            else:
                return await ctx.send("❌ Archétype non trouvé.")

        # 📄 Liste paginée de tous les archétypes
        pages = []
        archetype_names = sorted(self.archetypes.keys())
        chunk_size = 5

        for i in range(0, len(archetype_names), chunk_size):
            chunk = archetype_names[i:i + chunk_size]
            desc = "\n".join([f"• **{name}**" for name in chunk])
            embed = discord.Embed(
                title=f"📚 Archétypes ({i + 1}-{min(i + chunk_size, len(archetype_names))} sur {len(archetype_names)})",
                description=desc,
                color=discord.Color.green()
            )
            pages.append(embed)

        current = 0
        message = await ctx.send(embed=pages[current])

        if len(pages) <= 1:
            return

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction.emoji, user)

                if str(reaction.emoji) == "➡️" and current < len(pages) - 1:
                    current += 1
                    await message.edit(embed=pages[current])
                elif str(reaction.emoji) == "⬅️" and current > 0:
                    current -= 1
                    await message.edit(embed=pages[current])
            except asyncio.TimeoutError:
                break

    # 🏷️ Catégorisation personnalisée pour !help
    def cog_load(self):
        self.archetype.category = "🃏 Yu-Gi-Oh!"

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    On ajoute aussi manuellement une catégorie "🃏 Yu-Gi-Oh!" pour l’affichage dans !help.
    """
    cog = ArchetypeCommand(bot)

    # 🗂️ Définir la catégorie "🃏 Yu-Gi-Oh!" pour toutes les commandes du cog
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
