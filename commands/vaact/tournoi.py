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

            # 🟢 Menu : decks libres
            options_libres = []
            for diff, df in libres_grouped.items():
                if isinstance(diff, str) and diff.strip():
                    label = diff.strip()
                    if len(df) > 0:
                        options_libres.append(
                            discord.SelectOption(
                                label=label[:100],
                                description=f"{len(df)} deck(s)"
                            )
                        )

            if not options_libres:
                options_libres.append(
                    discord.SelectOption(
                        label="Aucune difficulté disponible",
                        description="—",
                        value="none",
                        default=True
                    )
                )

            select_libres = discord.ui.Select(
                placeholder="Sélectionnez la difficulté des decks libres",
                options=options_libres,
                custom_id="select_libres",
                disabled=(len(options_libres) == 1 and options_libres[0].value == "none")
            )

            async def callback_libres(interaction: discord.Interaction):
                if options_libres[0].value == "none":
                    await interaction.response.send_message("❌ Aucun deck libre disponible.", ephemeral=True)
                    return
                diff = interaction.data["values"][0]
                decks = libres_grouped.get(diff)
                if decks is None:
                    await interaction.response.send_message("❌ Difficulté inconnue.", ephemeral=True)
                    return
                texte = f"**Decks libres — Difficulté {diff} :**\n"
                for _, row in decks.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                await interaction.response.send_message(texte, ephemeral=True)

            select_libres.callback = callback_libres
            view.add_item(select_libres)


            # 🔴 Menu : decks pris
            options_pris = []
            for diff, df in pris_grouped.items():
                if isinstance(diff, str) and diff.strip():
                    label = diff.strip()
                    if len(df) > 0:
                        options_pris.append(
                            discord.SelectOption(
                                label=label[:100],
                                description=f"{len(df)} deck(s)"
                            )
                        )

            if not options_pris:
                options_pris.append(
                    discord.SelectOption(
                        label="Aucune difficulté disponible",
                        description="—",
                        value="none",
                        default=True
                    )
                )

            select_pris = discord.ui.Select(
                placeholder="Sélectionnez la difficulté des decks pris",
                options=options_pris,
                custom_id="select_pris",
                disabled=(len(options_pris) == 1 and options_pris[0].value == "none")
            )

            async def callback_pris(interaction: discord.Interaction):
                if options_pris[0].value == "none":
                    await interaction.response.send_message("❌ Aucun deck pris disponible.", ephemeral=True)
                    return
                diff = interaction.data["values"][0]
                decks = pris_grouped.get(diff)
                if decks is None:
                    await interaction.response.send_message("❌ Difficulté inconnue.", ephemeral=True)
                    return
                texte = f"**Decks pris — Difficulté {diff} :**\n"
                for _, row in decks.iterrows():
                    texte += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
                await interaction.response.send_message(texte, ephemeral=True)

            select_pris.callback = callback_pris
            view.add_item(select_pris)


            # ✅ Envoi final
            if len(view.children) == 0:
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed, view=view)

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
