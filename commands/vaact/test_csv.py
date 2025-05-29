# ──────────────────────────────────────────────────────────────
# 📁 test_csv.py
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import aiohttp
import os

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TestCSVCommand
# ──────────────────────────────────────────────────────────────
class TestCSVCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot
        self.sheet_url = os.getenv("SHEET_CSV_URL")

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !testcsv
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="testcsv",
        help="🔍 Teste la connexion au fichier CSV Google Sheets."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Anti-spam (optionnel)
    @commands.has_permissions(administrator=True)  # 🔐 Permission requise (optionnel)
    async def commande(self, ctx: commands.Context):
        if not self.sheet_url:
            await ctx.send("❌ URL du CSV introuvable dans les variables d'environnement.")
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sheet_url) as resp:
                    if resp.status != 200:
                        await ctx.send(f"🚨 Erreur HTTP : {resp.status}\n🔗 URL utilisée :\n{self.sheet_url}")
                        return

                    data = await resp.text()
                    preview = data[:500]  # 🔍 Affiche un extrait du fichier

            await ctx.send(
                f"✅ CSV récupéré avec succès !\n\n```csv\n{preview}\n```"
            )

        except Exception as e:
            await ctx.send(f"❌ Erreur pendant la récupération : `{e}`")

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.commande.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TestCSVCommand(bot))
    print("✅ Cog chargé : TestCSVCommand (catégorie = VAACT)")
