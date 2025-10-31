import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Flip a coin — double your bet if you win!")
    @app_commands.describe(bet="The amount you want to bet (>0)", side="Choose heads or tails")
    @app_commands.choices(side=[
        app_commands.Choice(name="Heads 🪙", value="heads"),
        app_commands.Choice(name="Tails 💰", value="tails")
    ])
    async def coinflip(self, interaction: discord.Interaction, bet: int, side: app_commands.Choice[str]):
        if bet <= 0:
            await interaction.response.send_message("💸 Bet must be greater than 0.", ephemeral=True)
            return

        user = interaction.user
        chosen = side.value
        await interaction.response.send_message(embed=discord.Embed(
            title="🪙 Coin Flip",
            description=f"{user.mention} bets **{bet} coins** on **{side.name}**!",
            color=discord.Color.teal()
        ))

        msg = await interaction.followup.send("🌀 Flipping the coin...")
        await asyncio.sleep(1.2)

        outcome = random.choice(["heads", "tails"])
        emoji = "🪙" if outcome == "heads" else "💰"

        if outcome == chosen:
            win = bet * 2
            title = "🎉 You Win!"
            desc = f"Coin landed on **{outcome.capitalize()} {emoji}**!\nYou won **{win} coins!** 🪙"
            color = discord.Color.gold()
        else:
            title = "💀 You Lose!"
            desc = f"Coin landed on **{outcome.capitalize()} {emoji}**.\nYou lost **{bet} coins.**"
            color = discord.Color.red()

        result = discord.Embed(title=title, description=desc, color=color)
        await msg.edit(content=None, embed=result)


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
