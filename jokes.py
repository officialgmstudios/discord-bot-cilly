import discord
from discord.ext import commands
import aiohttp
import random


class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.command()
    async def joke(self, ctx):
        """Fetches a random programming joke."""
        url = "https://official-joke-api.appspot.com/jokes/programming/ten"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Could not fetch a joke right now. Try again later!")
                    return
                jokes = await response.json()

        # Choose a random joke from the list
        joke = random.choice(jokes)
        setup = joke.get("setup", "Why did the function break?")
        punchline = joke.get(
            "punchline", "Because it couldn’t handle the arguments!")

        # Send it as an embed
        embed = discord.Embed(
            title="Programming Joke",
            description=f"**{setup}**\n\n*{punchline}*",
            color=discord.Color.random()
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Jokes(bot))
