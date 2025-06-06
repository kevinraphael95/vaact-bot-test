import discord
from discord.ext import commands
from discord.ui import View, Button
import requests

class TestView(View):
    @discord.ui.button(label="Carte aléatoire", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        try:
            r = requests.get("https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr")
            data = r.json()
            name = data.get("name", "Inconnu")
            desc = data.get("desc", "Pas d'effet")
            img_url = data.get("card_images", [{}])[0].get("image_url", "")

            embed = discord.Embed(title=name, description=desc, color=discord.Color.blue())
            if img_url:
                embed.set_image(url=img_url)

            await interaction.edit_original_response(content=None, embed=embed, view=None)
        except Exception as e:
            await interaction.edit_original_response(content=f"Erreur: {e}", embed=None, view=None)

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="testfusion", description="Test bouton carte aléatoire")
    async def testfusion(self, ctx: discord.ApplicationContext):
        view = TestView()
        await ctx.respond("Clique pour une carte aléatoire", view=view)

async def setup(bot):
    await bot.add_cog(TestCog(bot))
