import discord
from discord import app_commands
from discord.ext import commands
import random

class SevenUpSevenDown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="7up7down", description="Play 7 Up 7 Down — a quick dice betting game!")
    @app_commands.describe(
        bet="The amount you want to bet (must be greater than 0)",
        choice="Choose 'up' for above 7 or 'down' for below 7"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="7 Up (sum > 7)", value="up"),
        app_commands.Choice(name="7 Down (sum < 7)", value="down")
    ])
    async def seven_up_down(self, interaction: discord.Interaction, bet: int, choice: app_commands.Choice[str]):
        user = interaction.user

        if bet <= 0:
            await interaction.response.send_message("💰 Bet must be greater than zero!", ephemeral=True)
            return

        player_choice = choice.value

        # Roll two dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2

        await interaction.response.send_message(f"🎲 Rolling the dice for {user.mention}...")
        await interaction.followup.send(
            f"🎲 You rolled **{dice1}** and **{dice2}** → Total = **{total}**"
        )

        # Determine outcome
        if total == 7:
            await interaction.followup.send(f"😬 It’s exactly **7**! The house wins. You lost your **{bet} coins.**")
            return

        result = "up" if total > 7 else "down"

        if player_choice == result:
            win_amount = bet * 2
            await interaction.followup.send(
                f"🎉 Congratulations {user.mention}! You guessed **{choice.name}** and were right!\n"
                f"You won **{win_amount} coins!** 🪙"
            )
        else:
            await interaction.followup.send(
                f"💀 Sorry {user.mention}, you guessed **{choice.name}**, but the result was **{'7 Up' if result == 'up' else '7 Down'}**.\n"
                f"You lost your **{bet} coins.**"
            )

async def setup(bot):
    await bot.add_cog(SevenUpSevenDown(bot))
