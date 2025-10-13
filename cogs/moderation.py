import discord
from discord.ext import commands
import asyncio
from collections import defaultdict

user_strikes = defaultdict(int)
user_messages = defaultdict(list)
swear_words = ["h", "badword2", "badword3"]  # Replace with real words


async def get_or_create_mute_role(guild):
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if mute_role is None:
        try:
            mute_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
            print("✅ Created 'Muted' role automatically.")
        except discord.Forbidden:
            return None
    return mute_role


def setup_events(bot):

    @bot.event
    
    async def on_message(message):
        if message.author.bot:
            return

        user_id = message.author.id
        guild = message.guild
        content_lower = message.content.lower()

        user_messages[user_id].append(content_lower)
        if len(user_messages[user_id]) > 10:
            user_messages[user_id].pop(0)

        swear_detected = any(word in content_lower for word in swear_words)
        repeated_detected = user_messages[user_id].count(content_lower) > 5

        if swear_detected or repeated_detected:
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

            # Strike system
            if strikes == 1:
                await message.author.add_roles(mute_role, reason="1st strike")
                await message.channel.send(f"{message.author.mention} muted for 10s (1st strike).")
                await asyncio.sleep(10)
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

        await bot.process_commands(message)




    bot.run('put string here')


            

