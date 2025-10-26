import discord
from discord.ext import commands
from random import choice
import asyncpraw as praw


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(
            client_id="bAD_4h-VUJ-egoH8B6qOrQ",
            client_secret="t3lFUnMpzCAS7-4hSitv5EqYat75gQ",
            user_agent="script:ProgMemeGen:v1.0 (by u/Full-Measurement9670)"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.command()
    async def meme(self, ctx: commands.Context):
        # ✅ List of programming meme subreddits
        subreddits = [
            "ProgrammerHumor",
            "codinghumor",
            "ProgrammerHumorMemes",
            "learnprogrammingmemes",
            "programmingmemes",
            "techhumor"
        ]

        subreddit_name = choice(subreddits)
        subreddit = await self.reddit.subreddit(subreddit_name)
        posts_list = []

        async for post in subreddit.hot(limit=40):
            if (
                not post.over_18
                and post.author is not None
                and any(post.url.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"])
            ):
                posts_list.append((post.url, post.author.name, subreddit_name))
            elif post.author is None:
                posts_list.append((post.url, "N/A", subreddit_name))

        if posts_list:
            random_post = choice(posts_list)

            meme_embed = discord.Embed(
                title="💻 Programming Meme",
                description=f"From r/{random_post[2]}",
                color=discord.Color.random()
            )
            meme_embed.set_author(
                name=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            meme_embed.set_image(url=random_post[0])
            meme_embed.set_footer(text=f"Posted by u/{random_post[1]}")

            await ctx.send(embed=meme_embed)
        else:
            await ctx.send("⚠️ Couldn't fetch programming memes right now, try again later!")

    def cog_unload(self):
        self.bot.loop.create_task(self.reddit.close())


async def setup(bot):
    await bot.add_cog(Reddit(bot))
