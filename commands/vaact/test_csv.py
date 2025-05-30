# ────────────────────────────────────────────────────────────────────────────────
# 📁 test_csv.py — Commande !testcsv
# ────────────────────────────────────────────────────────────────────────────────
# Cette commande vérifie si le bot peut accéder à un fichier CSV public (Google Sheets).
# Utilise une URL définie dans les variables d'environnement (.env).
# Réservée aux administrateurs pour des raisons de sécurité.
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                                  # 🎨 Outils Discord (embeds, messages...)
from discord.ext import commands                # ⚙️ Système de commandes avec cogs
import aiohttp                                  # 🌐 Requêtes HTTP asynchrones
import os                                       # 📁 Accès aux variables d’environnement

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 COG : TestCSVCommand
# ────────────────────────────────────────────────────────────────────────────────
class TestCSVCommand(commands.Cog):
    """Commande d'administration pour tester l'accès à un fichier CSV distant."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot                                      # 🔌 Référence au bot
        self.sheet_url = os.getenv("SHEET_CSV_URL")         # 🔗 Récupère l'URL CSV depuis .env

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !testcsv
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="testcsv",
        help="🔍 Teste la connexion à un fichier CSV distant (Google Sheets)."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # 🧊 Limite d'utilisation
    @commands.has_permissions(administrator=True)                     # 🔐 Permission requise
    async def commande(self, ctx: commands.Context):
        """Vérifie si le lien CSV est accessible et affiche un extrait."""

        # 🚫 Vérifie si l'URL est bien définie
        if not self.sheet_url:
            await ctx.send("❌ URL du CSV introuvable dans les variables d'environnement.")
            return

        try:
            # 🌐 Session HTTP sécurisée
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sheet_url) as resp:
                    # 📡 Vérifie que le serveur répond correctement
                    if resp.status != 200:
                        await ctx.send(
                            f"🚨 Erreur HTTP : {resp.status}\n🔗 URL utilisée :\n{self.sheet_url}"
                        )
                        return

                    data = await resp.text()         # 📄 Récupère le contenu brut
                    preview = data[:500]             # 🔍 Affiche les 500 premiers caractères

            # ✅ Affiche l'extrait de CSV dans un bloc de code
            await ctx.send(
                f"✅ CSV récupéré avec succès !\n\n```csv\n{preview}\n```"
            )

        except Exception as e:
            # ⚠️ Capture toute erreur réseau/lecture
            await ctx.send(f"❌ Erreur pendant la récupération : `{e}`")

    # ────────────────────────────────────────────────────────────────────────────
    # 🏷️ CATÉGORISATION
    # ────────────────────────────────────────────────────────────────────────────
    def cog_load(self):
        """Définit la catégorie personnalisée pour la commande !help."""
        self.commande.category = "📁 VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 SETUP DU COG (Chargé automatiquement par le bot)
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """Fonction asynchrone pour enregistrer ce cog dans le bot."""
    await bot.add_cog(TestCSVCommand(bot))
    print("✅ Cog chargé : TestCSVCommand (catégorie = VAACT)")
