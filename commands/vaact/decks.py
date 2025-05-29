# ──────────────────────────────────────────────────────────────
# 🎴 decks.py — Commande !decks
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
import os

# 🔐 Récupération de l'URL depuis les variables d’environnement
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

# ──────────────────────────────────────────────────────────────
# 🔧 COG : DecksCommand
# ──────────────────────────────────────────────────────────────
class DecksCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !decks
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="decks",
        help="🎴 Affiche la liste des decks pris et disponibles."
    )
    async def decks(self, ctx: commands.Context):
        try:
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV n'est pas configurée.")
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Impossible de récupérer le fichier de données.")
                        return
                    data = await resp.read()

            df = pd.read_csv(io.BytesIO(data))

            # 🧼 Nettoyage
            df["PRIS ?"] = df["PRIS ?"].fillna("").str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["MECANIQUES"] = df.get("MECANIQUES", "—").fillna("—")
            df["DIFFICULTE"] = df.get("DIFFICULTE", "—").fillna("—")

            pris = df[df["PRIS ?"] == "✅"]
            libres = df[df["PRIS ?"] != "✅"]

            embed = discord.Embed(
                title="📘 État des decks",
                description="Voici la répartition actuelle des decks du tournoi.",
                color=discord.Color.blue()
            )
            embed.add_field(name="🎮 Decks disponibles", value=str(len(libres)), inline=True)
            embed.add_field(name="🔒 Decks pris", value=str(len(pris)), inline=True)
            embed.add_field(name="📋 Total", value=str(len(df)), inline=True)

            # 📃 Liste des decks libres
            lignes = []
            for _, row in libres.iterrows():
                ligne = f"• **{row['PERSONNAGE']}** — *{row['ARCHETYPE(S)']}*\n"
                ligne += f"    ⚙️ {row['MECANIQUES']} | 🎯 Difficulté {row['DIFFICULTE']}"
                lignes.append(ligne)

            texte = "\n".join(lignes)
            if len(texte) > 1024:
                texte = "\n".join(lignes[:15]) + "\n... *(liste coupée)*"

            embed.add_field(
                name="🆓 Liste des decks libres",
                value=texte if lignes else "Aucun deck disponible.",
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR DECKS] {e}")
            await ctx.send("🚨 Une erreur est survenue lors de la récupération des decks.")

    def cog_load(self):
        self.decks.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(DecksCommand(bot))
    print("✅ Cog chargé : DecksCommand (catégorie = VAACT)")
