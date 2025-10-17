import discord
from discord.ext import commands
import aiohttp
import random

class NewsAndQuotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.command()
    async def news(self, ctx):
        """Fetches a top news headline from NewsAPI (demo endpoint)."""
        url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Could not fetch news right now. Try again later!")
                    return
                data = await response.json()
        articles = data.get("articles", [])
        if not articles:
            await ctx.send("No news found.")
            return
        article = random.choice(articles)
        title = article.get("title", "No title")
        url = article.get("url", "")
        embed = discord.Embed(title="📰 News Headline", description=title, color=discord.Color.blue())
        if url:
            embed.add_field(name="Read more", value=url, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def quote(self, ctx):
        """Fetches a random inspirational quote from ZenQuotes API."""
        url = "https://zenquotes.io/api/random"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Could not fetch a quote right now. Try again later!")
                    return
                data = await response.json()
        if not data or not isinstance(data, list):
            await ctx.send("No quote found.")
            return
        quote = data[0].get("q", "Keep going!")
        author = data[0].get("a", "Unknown")
        embed = discord.Embed(title="💡 Inspirational Quote", description=f"{quote}\n\n— {author}", color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NewsAndQuotes(bot))
