import discord
from discord.ext import commands
import random
from datetime import datetime


class PrefixCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.command()
    async def hello(self, ctx):
        greetings = [
            f"Hello there, {ctx.author.mention}!",
            f"Hey {ctx.author.mention}! Hope you’re doing great",
            f"Yo {ctx.author.mention}! What's up?",
            f"Hi {ctx.author.mention}! Nice to see you!"
        ]
        await ctx.send(random.choice(greetings))

    @commands.command()
    async def goodmorning(self, ctx):
        responses = [
            f"Good morning, {ctx.author.mention}!",
            f"Rise and shine, {ctx.author.mention}! Let's code something awesome today",
            f"Morning {ctx.author.mention}! Hope you have a productive day ahead"
        ]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def goodnight(self, ctx):
        responses = [
            f"Good night, {ctx.author.mention}!",
            f"Sleep tight, {ctx.author.mention}! Don’t let the syntax bugs bite",
            f"Nighty night, {ctx.author.mention}! Dream of clean code"
        ]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def howareyou(self, ctx):
        responses = [
            "I’m just a bunch of Python code, but I’m feeling great today!",
            "Running smoothly on zero bugs (for now)",
            "I’m alive and waiting for commands! What about you?",
            "Better than yesterday — no exceptions raised yet"
        ]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def bye(self, ctx):
        responses = [
            f"Goodbye, {ctx.author.mention}! 👋",
            f"See you later, {ctx.author.mention}! Take care",
            f"Bye bye, {ctx.author.mention}! Keep coding strong "
        ]
        await ctx.send(random.choice(responses))


async def setup(bot):
    await bot.add_cog(PrefixCommands(bot))
