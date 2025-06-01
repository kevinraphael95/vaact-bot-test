# ──────────────────────────────────────────────────
# 📁 tournoi
# ────────────────────────────────────────────────

# ────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ────────────────────────────────────────────────
import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector
from supabase import create_client, Client

# ────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    async def load_decks(self):
        sslcontext = ssl.create_default_context()
        sslcontext.set_ciphers('DEFAULT:@SECLEVEL=1')
        connector = TCPConnector(ssl=sslcontext)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(self.SHEET_CSV_URL) as resp:
                if resp.status != 200:
                    raise Exception("Erreur téléchargement CSV")
                text = (await resp.read()).decode("utf-8")

        df = pd.read_csv(io.StringIO(text), skiprows=1)
        df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
        df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
        df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
        df["DIFFICULTE"] = df.get("DIFFICULTE", "Inconnue").fillna("Inconnue")

        pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
        libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

        return {
            "libres": {k: v for k, v in libres.groupby("DIFFICULTE")},
            "pris": {k: v for k, v in pris.groupby("DIFFICULTE")}
        }

    async def get_date_tournoi(self):
        try:
            tournoi_data = self.supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
            if tournoi_data.data and "prochaine_date" in tournoi_data.data[0]:
                return tournoi_data.data[0]["prochaine_date"]
            else:
                return "🗓️ à venir !"
        except Exception as e:
            print(f"[ERREUR SUPABASE] {e}")
            return "🗓️ à venir !"

    class DecksSelect(discord.ui.Select):
        def __init__(self, decks_df, diff_label, is_libre=True):
            self.decks_df = decks_df
            self.diff_label = diff_label
            self.is_libre = is_libre

            options = [
                discord.SelectOption(
                    label=str(row["PERSONNAGE"])[:100],
                    description=str(row["ARCHETYPE(S)"])[:100],
                    value=str(i)
                )
                for i, (_, row) in enumerate(decks_df.iterrows())
            ]

            placeholder = f"Decks {'libres' if is_libre else 'pris'} — difficulté {diff_label}"

            super().__init__(
                placeholder=placeholder,
                options=options,
                custom_id=f"select_{'libres' if is_libre else 'pris'}_{diff_label}"
            )

        async def callback(self, interaction: discord.Interaction):
            texte = f"**Decks {'libres' if self.is_libre else 'pris'} — Difficulté {self.diff_label} :**\n"
            for _, row in self.decks_df.iterrows():
                texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
            await interaction.response.send_message(texte, ephemeral=True)

    @commands.command(
        name="tournoi",
        aliases=["decks", "tournoivaact"],
        help="📅 Affiche la date du tournoi et la liste des decks disponibles/pris avec menus déroulants."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def tournoi(self, ctx: commands.Context):
        try:
            data = await self.load_decks()
            libres_grouped = data["libres"]
            pris_grouped = data["pris"]
            date_tournoi = await self.get_date_tournoi()

            embed = discord.Embed(
                title="🎴 Prochain Tournoi Yu-Gi-Oh VAACT",
                description=f"📅 **{date_tournoi}**",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Decks fournis par l'organisation du tournoi.")

            view = discord.ui.View(timeout=180)

            total_decks_libres = 0
            for diff, df in libres_grouped.items():
                if df.empty:
                    continue
                total_decks_libres += len(df)
                view.add_item(self.DecksSelect(df, diff, is_libre=True))

            if total_decks_libres == 0:
                embed.add_field(name="Decks libres", value="❌ Là y'a vraiment rien à afficher.", inline=False)

            total_decks_pris = 0
            for diff, df in pris_grouped.items():
                if df.empty:
                    continue
                total_decks_pris += len(df)
                view.add_item(self.DecksSelect(df, diff, is_libre=False))

            if total_decks_pris == 0:
                embed.add_field(name="Decks pris", value="❌ Là y'a vraiment rien à afficher.", inline=False)

            if len(view.children) == 0:
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed, view=view)

        except Exception as e:
            print(f"[ERREUR GLOBALE] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    def cog_load(self):
        self.tournoi.category = "VAACT"

# ────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
