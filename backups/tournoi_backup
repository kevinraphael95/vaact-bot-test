# ────────────────────────────────────────────────────────────────────────────────
# 📌 tournoi.py — Commande interactive !tournoi
# Objectif : Affiche la date du prochain tournoi à partir de Supabase + système de rappel
# Catégorie : 🧠 VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# 📦 Imports nécessaires
import discord
from discord.ext import commands
import aiohttp
import os

# 🔐 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 📦 Emoji de rappel
EMOJI_RAPPEL = "🛎️"

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    """Commande !tournoi — Affiche la date du prochain tournoi + gestion des rappels."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi.",
        description="Récupère et affiche la date du prochain tournoi depuis Supabase."
    )
    async def tournoi(self, ctx: commands.Context):
        """Commande principale !tournoi."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            await ctx.send("❌ Configuration manquante (SUPABASE_URL ou SUPABASE_KEY).")
            return

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{SUPABASE_URL}/rest/v1/tournoi_info?select=prochaine_date&order=id.desc&limit=1"
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("❌ Erreur lors de la récupération des données Supabase.")
                        return
                    data = await response.json()
        except Exception as e:
            print(f"[ERREUR tournoi] {e}")
            await ctx.send("❌ Erreur de connexion à Supabase.")
            return

        if not data or not data[0].get("prochaine_date"):
            await ctx.send("📭 Aucun tournoi prévu pour le moment.")
            return

        prochaine_date = data[0]["prochaine_date"]

        embed = discord.Embed(
            title="📅 Prochain tournoi",
            description=f"Le prochain tournoi aura lieu le **{prochaine_date}**.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Réagis à ce message avec {EMOJI_RAPPEL} pour recevoir un rappel 3 jours avant.")

        message = await ctx.send(embed=embed)
        await message.add_reaction(EMOJI_RAPPEL)

        def check(reaction, user):
            return (
                reaction.message.id == message.id
                and str(reaction.emoji) == EMOJI_RAPPEL
                and not user.bot
            )

        # Écoute d'une réaction pendant 15 minutes
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=900.0, check=check)

                # Vérifie si déjà inscrit dans Supabase
                async with aiohttp.ClientSession() as session:
                    url = f"{SUPABASE_URL}/rest/v1/rappels_tournoi?user_id=eq.{user.id}"
                    headers["Prefer"] = "resolution=merge-duplicates"
                    async with session.get(url, headers=headers) as r:
                        exists = await r.json()

                    if exists:
                        try:
                            await user.send("🛎️ Yooo toi tu m'as déjà demandé de te prévenir 3 jours avant, je m'en rappelais tkt pas.")
                        except discord.Forbidden:
                            await ctx.send(f"{user.mention}, je peux pas t’envoyer de MP ! Active-les.")
                        continue

                    # Sinon : on ajoute l'entrée
                    async with session.post(
                        f"{SUPABASE_URL}/rest/v1/rappels_tournoi",
                        headers={**headers, "Content-Type": "application/json"},
                        json={"user_id": str(user.id)}
                    ) as insert_resp:
                        if insert_resp.status in [200, 201]:
                            try:
                                await user.send("✅ Je t’enverrai un rappel 3 jours avant le tournoi !")
                            except discord.Forbidden:
                                await ctx.send(f"{user.mention}, je peux pas t’envoyer de MP ! Active-les.")
                        else:
                            print("[SUPABASE INSERT ERROR]", await insert_resp.text())

            except Exception as e:
                print("[REACTION TIMEOUT OU ERREUR]", e)
                break

    def cog_load(self):
        self.tournoi.category = "VAACT"

# 🔌 Setup du Cog
async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
                                           
