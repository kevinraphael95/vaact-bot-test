# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
import ssl
import os
import traceback
from aiohttp import TCPConnector, ClientConnectionError
from supabase import create_client, Client

# 🔐 Variables d'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

# 🔌 Connexion Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="tournoi",
        aliases=["decks", "tournoivaact"],
        help="📅 Affiche la date du tournoi et les decks disponibles/pris."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            if not SHEET_CSV_URL:
                await ctx.send("🚨 L'URL du fichier CSV est manquante.")
                return

            sslcontext = ssl.create_default_context()
            sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
            connector = TCPConnector(ssl=sslcontext)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(SHEET_CSV_URL) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erreur lors du téléchargement du fichier CSV.")
                        return
                    text = (await resp.read()).decode("utf-8")

            df = pd.read_csv(io.StringIO(text), skiprows=1)
            df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
            df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
            df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
            df["DIFFICULTÉ"] = df.get("DIFFICULTÉ", "—").fillna("—")

            pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
            libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

            # Récupérer la date du tournoi depuis supabase
            try:
                tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
                date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data and "prochaine_date" in tournoi_data.data[0] else "🗓️ à venir !"
            except Exception:
                date_tournoi = "🗓️ à venir !"

            difficulte_order = ["1/3", "2/3", "3/3"]

            def format_decks(df_slice):
                texte = ""
                for _, row in df_slice.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
                return texte if texte else "Aucun deck."

            groupes = []
            for statut, label_statut, color in [
                (libres, "Decks Libres", discord.Color.green()),
                (pris, "Decks Pris", discord.Color.red())
            ]:
                for diff in difficulte_order:
                    df_part = statut[statut["DIFFICULTÉ"] == diff]
                    groupes.append({
                        "label": f"{label_statut} — Difficulté {diff}",
                        "color": color,
                        "decks": df_part
                    })

            pages = []
            for groupe in groupes:
                decks_df = groupe["decks"]
                chunks = [decks_df.iloc[i:i+15] for i in range(0, len(decks_df), 15)] or [decks_df]

                for chunk in chunks:
                    embed = discord.Embed(
                        title=f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT — {groupe['label']}",
                        description=format_decks(chunk),
                        color=groupe["color"]
                    )
                    embed.set_footer(text=f"📅 {date_tournoi}")
                    pages.append(embed)

            if not pages:
                await ctx.send("📭 Aucun deck trouvé pour ce tournoi.")
                return

            class TournoiView(discord.ui.View):
                def __init__(self, pages):
                    super().__init__(timeout=180)
                    self.pages = pages
                    self.index = 0

                async def update(self, interaction):
                    embed = self.pages[self.index]
                    await interaction.response.edit_message(embed=embed, view=self)

                @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
                async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.index = (self.index - 1) % len(self.pages)
                    await self.update(interaction)

                @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
                async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.index = (self.index + 1) % len(self.pages)
                    await self.update(interaction)

            view = TournoiView(pages)
            await ctx.send(embed=pages[0], view=view)

        except Exception:
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    def cog_load(self):
        self.tournoi.category = "VAACT"


# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
