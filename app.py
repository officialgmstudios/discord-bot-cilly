import discord
from discord.ext import commands
import os
import asyncio

# Create the bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready!")


# Function to load all extensions (no cogs folder)
async def load_extensions():
    for filename in os.listdir("."):
        if filename.endswith(".py") and filename != "app.py":
            try:
                await bot.load_extension(filename[:-3])
                print(f"Loaded module: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")


async def main():
    async with bot:
        await load_extensions()
        # Read token from token.txt
        with open("token.txt", "r") as f:
            token = f.read().strip()
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
