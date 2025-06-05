# ────────────────────────────────────────────────────────────────────────────────
# 📌 deckmaudit.py — Commande interactive !deckmaudit
# Objectif : Générer un deck "maudit" avec des vraies cartes YGODeckPro absurdes
# Catégorie : Yu-Gi-Oh
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import random

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class DeckMaudit(commands.Cog):
    """
    Commande !deckmaudit — Génère un deck maudit absurde et perdant à coup sûr.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_cards_by_popularity(self, view_threshold: int):
        """Récupère jusqu'à 300 cartes ayant un nombre de vues <= threshold."""
        url = f"https://ygodeckpro.fr/api/cards?limit=300&views[lte]={view_threshold}&random=true"
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print(f"[fetch_cards_by_popularity] HTTP Status {resp.status} pour seuil {view_threshold}")
                            return None
                        try:
                            data = await resp.json()
                            return data.get("data", [])
                        except Exception as e_json:
                            print(f"[fetch_cards_by_popularity] Erreur décodage JSON : {e_json}")
                            return None
                except Exception as e_req:
                    print(f"[fetch_cards_by_popularity] Erreur requête GET : {e_req}")
                    return None
        except Exception as e_sess:
            print(f"[fetch_cards_by_popularity] Erreur création session HTTP : {e_sess}")
            return None

    def is_card_maudite(self, c):
        """Détermine si une carte est 'maudite' (inutilisable, absurde)."""
        try:
            atk = c.get("atk", 0)
            defn = c.get("def", 0)
            card_type = c.get("type", "").lower()
            desc = c.get("desc", "").lower()

            faible_monstre = (card_type == "monster" and atk <= 500 and defn <= 500)
            piege_inutile = (card_type == "trap" and "annuler" not in desc and "contre" not in desc and "effet" not in desc)
            magie_nulle = (card_type == "spell" and "pioche" not in desc and "recuperer" not in desc and "search" not in desc)

            return faible_monstre or piege_inutile or magie_nulle
        except Exception as e:
            print(f"[is_card_maudite] Erreur analyse carte : {e}")
            return False

    def filtrer_cartes_maudites(self, cartes):
        try:
            return [c for c in cartes if self.is_card_maudite(c)]
        except Exception as e:
            print(f"[filtrer_cartes_maudites] Erreur filtrage cartes : {e}")
            return []

    def composer_deck(self, cartes):
        try:
            return random.sample(cartes, min(20, len(cartes)))
        except Exception as e:
            print(f"[composer_deck] Erreur composition deck : {e}")
            return []

    def generer_strategie(self, deck):
        try:
            nb_piege = sum(1 for c in deck if c.get("type", "").lower() == "trap")
            nb_monstre_faible = sum(1 for c in deck if c.get("type", "").lower() == "monster" and c.get("atk", 0) <= 500)

            texte = "🃏 **Stratégie du deck maudit** 🃏\n"
            if nb_piege > 5:
                texte += "- Cache-toi derrière tes pièges inutiles et espère que ton adversaire s'endorme !\n"
            if nb_monstre_faible > 5:
                texte += "- Envoie tes monstres faibles en première ligne, comme chair à canon.\n"
            if nb_piege <= 5 and nb_monstre_faible <= 5:
                texte += "- C’est un chaos total, mais avec style. Peut-être.\n"
            texte += "Joue lentement. Très lentement. L'abandon est ta victoire...\n"
            return texte
        except Exception as e:
            print(f"[generer_strategie] Erreur génération stratégie : {e}")
            return "Stratégie impossible à déterminer."

    @commands.command(
        name="deckmaudit",
        help="Génère un deck aléatoire avec des cartes réelles YGODeckPro absurdes.",
        description="Commande fun pour générer un deck Yu-Gi-Oh! injouable mais drôle."
    )
    async def deckmaudit(self, ctx: commands.Context):
        """Commande principale pour générer un deck maudit."""
        try:
            await ctx.trigger_typing()

            seuil_vues = 50
            max_vues = 1000
            deck = None
            cartes = None

            while seuil_vues <= max_vues:
                try:
                    cartes = await self.fetch_cards_by_popularity(seuil_vues)
                    if not cartes:
                        seuil_vues += 100
                        continue
                except Exception as e_fetch:
                    print(f"[deckmaudit] Erreur fetch cartes au seuil {seuil_vues} : {e_fetch}")
                    seuil_vues += 100
                    continue

                try:
                    maudites = self.filtrer_cartes_maudites(cartes)
                except Exception as e_filter:
                    print(f"[deckmaudit] Erreur filtrage cartes maudites : {e_filter}")
                    maudites = []

                if len(maudites) >= 10:
                    try:
                        deck = self.composer_deck(maudites)
                    except Exception as e_compose:
                        print(f"[deckmaudit] Erreur composition deck : {e_compose}")
                        deck = None
                    if deck:
                        break
                seuil_vues += 100

            if not deck:
                # Aucun deck maudit trouvé, on génère un deck aléatoire sans filtre sur la dernière fetch
                try:
                    if cartes:
                        deck = self.composer_deck(cartes)
                    else:
                        await ctx.send("❌ Impossible de récupérer des cartes pour générer un deck.")
                        return
                except Exception as e_compose_last:
                    print(f"[deckmaudit] Erreur composition deck fallback : {e_compose_last}")
                    await ctx.send("❌ Une erreur est survenue lors de la composition du deck.")
                    return

            try:
                embed = discord.Embed(
                    title="💀 Deck Maudit généré par Atem 💀",
                    description="Voici un deck tellement nul que même Exodia s'en moquerait.",
                    color=discord.Color.dark_red()
                )
            except Exception as e_embed:
                print(f"[deckmaudit] Erreur création embed : {e_embed}")
                await ctx.send("❌ Une erreur est survenue lors de la création de l'embed.")
                return

            for c in deck:
                try:
                    name = c.get("name", "???")
                    type_ = c.get("type", "Inconnu")
                    desc = c.get("desc", "")
                    atk = c.get("atk", "?")
                    defn = c.get("def", "?")
                    short_desc = (desc[:97] + "...") if len(desc) > 100 else desc

                    embed.add_field(
                        name=f"{name} [{type_}] (ATK:{atk} DEF:{defn})",
                        value=short_desc,
                        inline=False
                    )
                except Exception as e_field:
                    print(f"[deckmaudit] Erreur ajout champ embed pour carte {c.get('name', '???')} : {e_field}")

            try:
                embed.add_field(
                    name="Stratégie (très douteuse)",
                    value=self.generer_strategie(deck),
                    inline=False
                )
                embed.set_footer(text="Deck généré uniquement pour les duellistes suicidaires 🎲")
            except Exception as e_embed_field:
                print(f"[deckmaudit] Erreur ajout champ stratégie ou footer : {e_embed_field}")

            try:
                await ctx.send(embed=embed)
            except Exception as e_send:
                print(f"[deckmaudit] Erreur envoi message : {e_send}")
                await ctx.send("❌ Une erreur est survenue lors de l'envoi du message.")

        except Exception as e:
            print(f"[ERREUR deckmaudit] {e}")
            await ctx.send("❌ Une erreur est survenue lors de la génération du deck maudit.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = DeckMaudit(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
