import discord
from discord.ext import commands
import asyncio
import os

# --- SETUP INTENTS ---
intents = discord.Intents.default()
intents.message_content = True

# --- COMMAND TREE (slash commands) ---
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="MatriX"))
    await bot.tree.sync()
    print("🌐 Slash commands synced successfully!")

# --- LOAD COGS ---
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")

# --- RUN THE BOT ---
async def main():
    async with bot:
        await load_cogs()
        await bot.start("BOT TOKEN HERE")  # ⬅️ Replace with your bot token

if __name__ == "__main__":
    asyncio.run(main())

