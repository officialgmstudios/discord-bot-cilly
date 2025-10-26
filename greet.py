import discord
from discord.ext import commands

class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"Welcome to the server, {member.mention}! 👋")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"Goodbye {member.name}! We'll miss you! 👋")

async def setup(bot):
    await bot.add_cog(Greet(bot))
