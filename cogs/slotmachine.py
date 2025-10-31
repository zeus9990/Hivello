import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

EMOJIS = ["🍒", "🍋", "🍉", "💎", "7️⃣", "⭐"]
SPIN_ANIM = ["🎰 | 🎲 | 🎯", "🎲 | 🎯 | 🎰", "🎯 | 🎰 | 🎲"]

class SlotMachine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slotmachine", description="Spin the Lucky 7 slot machine and test your luck!")
    @app_commands.describe(bet="The amount to bet (>0)")
    async def slotmachine(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("💸 Bet must be greater than 0.", ephemeral=True)
            return

        await interaction.response.send_message(embed=discord.Embed(
            title="🎰 Slot Machine",
            description=f"Spinning the reels for **{interaction.user.mention}**...\nBet: **{bet} coins**",
            color=discord.Color.purple()
        ))

        msg = await interaction.followup.send("🎲 Spinning...")
        for frame in SPIN_ANIM:
            await msg.edit(content=frame)
            await asyncio.sleep(0.8)

        result = [random.choice(EMOJIS) for _ in range(3)]
        result_text = " | ".join(result)

        # Check win conditions
        if len(set(result)) == 1:
            multiplier = 5
            title = "🎉 JACKPOT!"
            color = discord.Color.gold()
        elif len(set(result)) == 2:
            multiplier = 2
            title = "✨ Small Win!"
            color = discord.Color.green()
        else:
            multiplier = 0
            title = "💀 You Lose!"
            color = discord.Color.red()

        payout = bet * multiplier
        embed = discord.Embed(title=title, description=f"🎰 Result: {result_text}", color=color)
        if multiplier > 0:
            embed.add_field(name="Payout", value=f"You won **{payout} coins!** 🪙", inline=False)
        else:
            embed.add_field(name="Loss", value=f"You lost **{bet} coins.** Better luck next spin.", inline=False)
        await msg.edit(content=None, embed=embed)


async def setup(bot):
    await bot.add_cog(SlotMachine(bot))
