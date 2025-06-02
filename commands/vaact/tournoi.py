# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi (pagination des decks par difficulté et statut)
# ───────────────────────────────────────────────────────────────────────────────
import os
import math
import discord
from discord.ext import commands
from discord.ui import View, Button
import pandas as pd

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class PaginationView(View):
    def __init__(self, pages, initial_page=0):
        super().__init__(timeout=180)
        self.pages = pages
        self.current_page = initial_page

        self.prev_button = Button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="➡️ Suivant", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.update_buttons()

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        embed = self.pages[self.current_page]
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot
        self.SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

    @commands.command(
        name="tournoi",
        aliases=["tourney", "tournois"],
        help="📅 Affiche la date du tournoi et liste paginée des decks libres et pris par difficulté."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # anti-spam
    async def tournoi(self, ctx: commands.Context):
        print("Commande !tournoi appelée")
        if not self.SHEET_CSV_URL:
            await ctx.send("❌ L'URL du CSV des decks n'est pas configurée.")
            print("Erreur : SHEET_CSV_URL non défini")
            return

        try:
            df = pd.read_csv(self.SHEET_CSV_URL)
            print(f"CSV chargé, shape={df.shape}")

            expected_cols = {"DateTournoi", "Deck", "Status", "Difficulté"}
            if not expected_cols.issubset(df.columns):
                await ctx.send(f"❌ Colonnes manquantes dans le CSV. Attendu : {expected_cols}")
                print(f"Colonnes dans CSV : {df.columns}")
                return

            date_tournoi = df["DateTournoi"].iloc[0] if not df["DateTournoi"].isna().all() else "Date inconnue"

            pages = []
            decks_per_page = 10

            for diff in sorted(df["Difficulté"].dropna().unique()):
                libres = df[(df["Status"] == "Libre") & (df["Difficulté"] == diff)]["Deck"].tolist()
                pris = df[(df["Status"] == "Pris") & (df["Difficulté"] == diff)]["Deck"].tolist()

                # Pages decks libres
                for i in range(math.ceil(len(libres) / decks_per_page)):
                    chunk = libres[i*decks_per_page:(i+1)*decks_per_page]
                    embed = discord.Embed(
                        title=f"Tournoi du {date_tournoi} — Decks Libres (Difficulté {diff})",
                        description="\n".join(f"• {deck}" for deck in chunk),
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Page {i+1} / {math.ceil(len(libres) / decks_per_page)}")
                    pages.append(embed)

                # Pages decks pris
                for i in range(math.ceil(len(pris) / decks_per_page)):
                    chunk = pris[i*decks_per_page:(i+1)*decks_per_page]
                    embed = discord.Embed(
                        title=f"Tournoi du {date_tournoi} — Decks Pris (Difficulté {diff})",
                        description="\n".join(f"• {deck}" for deck in chunk),
                        color=discord.Color.red()
                    )
                    embed.set_footer(text=f"Page {i+1} / {math.ceil(len(pris) / decks_per_page)}")
                    pages.append(embed)

            if not pages:
                await ctx.send("⚠️ Aucun deck trouvé dans le CSV.")
                return

            view = PaginationView(pages)
            await ctx.send(embed=pages[0], view=view)
            print("Message envoyé avec pagination.")

        except Exception as e:
            print("[ERREUR TOURNOI]", e)
            await ctx.send("❌ Une erreur est survenue lors de la récupération des données du tournoi.")

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.tournoi.category = "Tournois"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = Tournois)")
