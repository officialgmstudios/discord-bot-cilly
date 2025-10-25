import discord
from discord.ext import commands
import asyncio
from collections import defaultdict

user_strikes = defaultdict(int)
# user_messages = defaultdict(list)
swear_words = ["bc", "mc", "gandu", "madarchod", "bhosdike"]  # Replace with real words


async def get_or_create_mute_role(guild):
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if mute_role is None:
        try:
            mute_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
            print("Created 'Muted' role automatically.")
        except discord.Forbidden:
            return None
    return mute_role


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog is ready!")

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return

     
        content_lower = message.content.lower()


        if any(word in content_lower for word in swear_words):
            user_id = message.author.id
            guild = message.guild
            user_strikes[user_id] += 1
            strikes = user_strikes[user_id]

            mute_role = await get_or_create_mute_role(guild)
            if not mute_role:
                await message.channel.send("Couldn't get or create 'Muted' role.")
                return

            bot_member = guild.me
            if bot_member.top_role <= mute_role:
                await message.channel.send("Move my role above 'Muted' to assign it.")
                return

            # Strike System
            if strikes == 1:
                await message.author.add_roles(mute_role, reason="1st strike")
                await message.channel.send(f"{message.author.mention} muted for 1h (1st strike).")
                await asyncio.sleep(3600)
                await message.author.remove_roles(mute_role)
                await message.channel.send(f"{message.author.mention} unmuted.")
            elif strikes == 2:
                if guild.me.guild_permissions.kick_members:
                    await guild.kick(message.author, reason="2nd strike")
                    await message.channel.send(f"{message.author.mention} kicked for repeated offenses.")
                else:
                    await message.channel.send("I lack permission to kick members.")
            elif strikes >= 3:
                if guild.me.guild_permissions.ban_members:
                    await guild.ban(message.author, reason="3rd strike")
                    await message.channel.send(f"{message.author.mention} banned for repeated offenses.")
                else:
                    await message.channel.send("I lack permission to ban members.")

        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(Moderation(bot))