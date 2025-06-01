# ──────────────────────────────────────────────────────────────
# 📁 tournoi.py
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io, ssl, os, traceback
from aiohttp import TCPConnector
from supabase import create_client, Client

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 🧩 Charge les données CSV
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

    # 📅 Récupère la date du tournoi
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

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
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

            if not libres_grouped:
                embed.add_field(name="Decks libres", value="Aucun deck libre.", inline=False)
            if not pris_grouped:
                embed.add_field(name="Decks pris", value="Aucun deck pris.", inline=False)

            embed.set_footer(text="Decks fournis par l'organisation du tournoi.")
            view = discord.ui.View(timeout=180)
						
###

            # ▶️ Traitement des decks libres
            total_decks_libres = 0
            for diff, df in libres_grouped.items():
                if len(df) == 0:
                    continue

                total_decks_libres += len(df)

                select_libres = discord.ui.Select(
                    placeholder=f"Decks libres — difficulté {diff}",
                    options=[
                        discord.SelectOption(
                            label=row["PERSONNAGE"][:100],
                            description=row["ARCHETYPE(S)"][:100],
                            value=str(i)
                        ) for i, (_, row) in enumerate(df.iterrows())
                    ],
                    custom_id=f"select_libres_{diff}"
                )

                async def make_callback_libres(diff):
                    async def callback(interaction: discord.Interaction):
                        decks = libres_grouped.get(diff)
                        if not decks or decks.empty:
                            await interaction.response.send_message("❌ Aucun deck trouvé.", ephemeral=True)
                            return
                        texte = f"**Decks libres — Difficulté {diff} :**\n"
                        for _, row in decks.iterrows():
                            texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                        await interaction.response.send_message(texte, ephemeral=True)
                    return callback

                select_libres.callback = await make_callback_libres(diff)
                view.add_item(select_libres)

            if total_decks_libres == 0:
                embed.add_field(name="Decks libres", value="❌ Là y'a vraiment rien à afficher.", inline=False)

            # 🔴 Traitement des decks pris
            total_decks_pris = 0
            for diff, df in pris_grouped.items():
                if len(df) == 0:
                    continue

                total_decks_pris += len(df)

                select_pris = discord.ui.Select(
                    placeholder=f"Decks pris — difficulté {diff}",
                    options=[
                        discord.SelectOption(
                            label=row["PERSONNAGE"][:100],
                            description=row["ARCHETYPE(S)"][:100],
                            value=str(i)
                        ) for i, (_, row) in enumerate(df.iterrows())
                    ],
                    custom_id=f"select_pris_{diff}"
                )

                async def make_callback_pris(diff):
                    async def callback(interaction: discord.Interaction):
                        decks = pris_grouped.get(diff)
                        if not decks or decks.empty:
                            await interaction.response.send_message("❌ Aucun deck trouvé.", ephemeral=True)
                            return
                        texte = f"**Decks pris — Difficulté {diff} :**\n"
                        for _, row in decks.iterrows():
                            texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                        await interaction.response.send_message(texte, ephemeral=True)
                    return callback

                select_pris.callback = await make_callback_pris(diff)
                view.add_item(select_pris)

            if total_decks_pris == 0:
                embed.add_field(name="Decks pris", value="❌ Là y'a vraiment rien à afficher.", inline=False)

            # ✅ Envoi final
            if len(view.children) == 0:
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed, view=view)

	    
	    ####


        except Exception as e:
            print(f"[ERREUR GLOBALE] {e}")
            traceback.print_exc()
            await ctx.send("🚨 Une erreur inattendue est survenue.")

    # 🏷️ Catégorisation pour affichage personnalisé dans !help
    def cog_load(self):
        self.tournoi.category = "VAACT"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TournoiCommand(bot))
    print("✅ Cog chargé : TournoiCommand (catégorie = VAACT)")
