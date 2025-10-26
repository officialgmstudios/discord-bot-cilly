import discord
from discord.ext import commands
import os
import asyncio
# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Bot ready even


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready!")

# Function to load all cogs automatically


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔹 Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

# Main startup sequence


async def main():
    async with bot:
        await load_extensions()
        with open("token.txt") as f:
            token = f.read().strip()
        await bot.start("token")

# Run the bot
asyncio.run(main())
