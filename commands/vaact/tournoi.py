import discord
from discord.ext import commands
import pandas as pd
import aiohttp
import io
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class TournoiView(discord.ui.View):
    def __init__(self, pages, titre, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page = 0
        self.titre = titre

    async def update_embed(self, interaction):
        embed = self.pages[self.page]
        embed.title = self.titre
        embed.set_footer(text=f"Page {self.page + 1}/{len(self.pages)} • Decks triés par difficulté")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction, button):
        self.page = (self.page - 1) % len(self.pages)
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        self.page = (self.page + 1) % len(self.pages)
        await self.update_embed(interaction)

class TournoiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tournoi")
    async def tournoi(self, ctx):
        if not SHEET_CSV_URL:
            await ctx.send("❌ URL CSV manquante")
            return

        # Télécharger CSV
        async with aiohttp.ClientSession() as session:
            async with session.get(SHEET_CSV_URL) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Erreur téléchargement CSV")
                    return
                text = await resp.text()

        df = pd.read_csv(io.StringIO(text), skiprows=1)
        df["PRIS ?"] = df["PRIS ?"].fillna("").astype(str).str.strip()
        df["PERSONNAGE"] = df["PERSONNAGE"].fillna("Inconnu")
        df["ARCHETYPE(S)"] = df.get("ARCHETYPE(S)", "—").fillna("—")
        df["DIFFICULTÉ"] = df.get("DIFFICULTÉ", "—").fillna("—")

        # Récup date tournoi Supabase
        tournoi_data = supabase.table("tournoi_info").select("prochaine_date").eq("id", 1).execute()
        date_tournoi = tournoi_data.data[0]["prochaine_date"] if tournoi_data.data else "🗓️ à venir !"
        titre_embed = f"🎴 Prochain Tournoi Yu-Gi-Oh VAACT\n📅 **{date_tournoi}**"

        # Séparer pris/libres
        pris = df[df["PRIS ?"].str.lower().isin(["true", "✅"])]
        libres = df[~df["PRIS ?"].str.lower().isin(["true", "✅"])]

        # Trier libres par difficulté
        ordre_diff = ["1/3", "2/3", "3/3"]
        libres["DIFFICULTÉ"] = pd.Categorical(libres["DIFFICULTÉ"], categories=ordre_diff, ordered=True)
        libres = libres.sort_values("DIFFICULTÉ")

        # Découper en pages (15 par page)
        pages = []
        for i in range(0, len(libres), 15):
            chunk = libres.iloc[i:i+15]
            desc = ""
            for _, row in chunk.iterrows():
                desc += f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}* ({row['DIFFICULTÉ']})\n"
            embed = discord.Embed(description=desc, color=discord.Color.green())
            pages.append(embed)

        if not pages:
            pages = [discord.Embed(description="Aucun deck libre trouvé.", color=discord.Color.red())]

        # Afficher decks pris dans un embed séparé, limité à 1000 caractères
        desc_pris = ""
        for _, row in pris.iterrows():
            ligne = f"• {row['PERSONNAGE']} — *{row['ARCHETYPE(S)']}*\n"
            if len(desc_pris) + len(ligne) < 1000:
                desc_pris += ligne
            else:
                desc_pris += "\n... *(liste coupée)*"
                break
        if desc_pris:
            embed_pris = discord.Embed(title="🔒 Decks déjà pris", description=desc_pris, color=discord.Color.red())
            await ctx.send(embed=embed_pris)

        view = TournoiView(pages, titre_embed)
        await ctx.send(embed=pages[0], view=view)

async def setup(bot):
    await bot.add_cog(TournoiCommand(bot))
