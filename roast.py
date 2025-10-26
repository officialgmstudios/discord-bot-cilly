import discord
from discord.ext import commands
import random


class Roast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    # Command: roast a user or yourself
    @commands.command()
    async def roast(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        roasts = [
            f"{target.mention}, even Stack Overflow can’t help you now",
            f"{target.mention}, your code runs slower than Internet Explorer",
            f"{target.mention}, you debug like it’s your first day… every day",
            f"{target.mention}, you must be written in Python — full of indentation errors!",
            f"{target.mention}, even ChatGPT needed extra context to understand your logic",
            f"{target.mention}, you must have a PhD in printing 'Hello World'"
        ]
        await ctx.send(random.choice(roasts))

    # Command: tell a random knock-knock joke
    @commands.command()
    async def knock(self, ctx):
        jokes = [
            ("Knock knock.", "Who’s there?", "Java.", "Java who?", "Java nice day!"),
            ("Knock knock.", "Who’s there?", "Git.",
             "Git who?", "Git ready for some bad puns"),
            ("Knock knock.", "Who’s there?", "AI.", "AI who?",
             "AI can’t believe you fell for this joke!"),
            ("Knock knock.", "Who’s there?", "Code.", "Code who?",
             "Code you please stop breaking my syntax?")
        ]

        setup, reply1, who1, reply2, punchline = random.choice(jokes)
        await ctx.send(setup)
        await ctx.send(reply1)
        await ctx.send(who1)
        await ctx.send(reply2)
        await ctx.send(punchline)

    # Command: tell a random short funny joke
    @commands.command()
    async def funjoke(self, ctx):
        jokes = [
            "Why do programmers hate nature? — It has too many bugs",
            "I told my computer I needed a break… it froze",
            "Why did the developer go broke? — Because he used up all his cache",
            "How many programmers does it take to change a light bulb? — None, it’s a hardware problem",
            "Why do Java developers wear glasses? — Because they don’t see sharp"
        ]
        await ctx.send(random.choice(jokes))


async def setup(bot):
    await bot.add_cog(Roast(bot))
