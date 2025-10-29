import discord
from discord import app_commands
from discord.ext import commands
import random

class GuessNumber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Track ongoing games per user {user_id: {...}}

    # Slash command definition
    @app_commands.command(name="guessnumber", description="Play Guess the Number! Bet and win double if you guess right.")
    @app_commands.describe(bet="Amount you want to bet (must be greater than 0)")
    async def guessnumber(self, interaction: discord.Interaction, bet: int):
        user = interaction.user

        # Prevent duplicate sessions
        if user.id in self.active_games:
            await interaction.response.send_message(
                f"🎮 {user.mention}, you already have a game running!", ephemeral=True
            )
            return

        if bet <= 0:
            await interaction.response.send_message("💰 Your bet must be greater than zero.", ephemeral=True)
            return

        # Initialize the game
        target_number = random.randint(1, 100)
        self.active_games[user.id] = {
            "number": target_number,
            "attempts": 0,
            "bet": bet
        }

        await interaction.response.send_message(
            f"🎯 {user.mention}, I’ve picked a number between **1 and 100**.\n"
            f"You have **5 guesses** to find it! Type your guesses in the chat below."
        )

        def check(message):
            return (
                message.author == user
                and message.channel == interaction.channel
                and message.content.isdigit()
            )

        # Handle up to 5 guesses
        while self.active_games[user.id]["attempts"] < 5:
            try:
                guess_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
            except:
                await interaction.followup.send(f"⌛ {user.mention}, you took too long! Game over.")
                del self.active_games[user.id]
                return

            guess = int(guess_msg.content)
            game = self.active_games[user.id]
            game["attempts"] += 1

            if guess == game["number"]:
                win_amount = game["bet"] * 2
                await interaction.followup.send(
                    f"🎉 You nailed it, {user.mention}! The number was **{game['number']}**.\n"
                    f"You won **{win_amount} coins!** 🪙"
                )
                del self.active_games[user.id]
                return
            elif guess < game["number"]:
                await interaction.followup.send(f"⬆️ Too low! ({5 - game['attempts']} guesses left)")
            else:
                await interaction.followup.send(f"⬇️ Too high! ({5 - game['attempts']} guesses left)")

        await interaction.followup.send(
            f"💀 {user.mention}, you're out of guesses! The number was **{self.active_games[user.id]['number']}**.\n"
            f"You lost your **{bet} coins.** Better luck next time!"
        )
        del self.active_games[user.id]

async def setup(bot):
    await bot.add_cog(GuessNumber(bot))