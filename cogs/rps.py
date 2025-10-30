import discord
from discord import app_commands
from discord.ext import commands
import random

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Play Rock Paper Scissors against the bot!")
    @app_commands.describe(
        bet="The amount you want to bet (must be greater than 0)",
        choice="Your move: Rock, Paper, or Scissors"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock 🪨", value="rock"),
        app_commands.Choice(name="Paper 📄", value="paper"),
        app_commands.Choice(name="Scissors ✂️", value="scissors")
    ])
    async def rps(self, interaction: discord.Interaction, bet: int, choice: app_commands.Choice[str]):
        user = interaction.user

        if bet <= 0:
            await interaction.response.send_message("💰 Bet must be greater than zero!", ephemeral=True)
            return

        user_choice = choice.value
        bot_choice = random.choice(["rock", "paper", "scissors"])

        # Outcome logic
        results = {
            ("rock", "scissors"): "win",
            ("scissors", "paper"): "win",
            ("paper", "rock"): "win",
            ("scissors", "rock"): "lose",
            ("paper", "scissors"): "lose",
            ("rock", "paper"): "lose"
        }

        if user_choice == bot_choice:
            outcome = "tie"
        else:
            outcome = results.get((user_choice, bot_choice), "lose")

        await interaction.response.send_message(
            f"🪨📄✂️ {user.mention} chose **{user_choice.capitalize()}**, I chose **{bot_choice.capitalize()}**."
        )

        if outcome == "tie":
            await interaction.followup.send("🤝 It’s a tie! You keep your bet.")
        elif outcome == "win":
            await interaction.followup.send(f"🎉 You win! You earned **{bet * 2} coins!** 🪙")
        else:
            await interaction.followup.send(f"💀 You lose! You lost **{bet} coins.** Better luck next time!")

async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))
