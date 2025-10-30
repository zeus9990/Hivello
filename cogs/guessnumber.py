import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

EMBED_COLOR = discord.Color.blue()
MAX_GUESSES = 5
GUESS_TIMEOUT = 30.0  # seconds per guess

def make_embed(title: str, description: str, color=EMBED_COLOR):
    return discord.Embed(title=title, description=description, color=color)

class GuessNumber(commands.Cog):
    """Guess the Number — slash command version with embeds & polished UX."""

    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # user_id -> {number, attempts, bet}

    @app_commands.command(name="guessnumber", description="Bet and guess a number between 1 and 100. 5 guesses max.")
    @app_commands.describe(bet="Amount to bet (must be > 0)")
    async def guessnumber(self, interaction: discord.Interaction, bet: int):
        user = interaction.user

        if bet <= 0:
            await interaction.response.send_message(
                embed=make_embed("Invalid Bet", "💸 Bet must be greater than 0."), ephemeral=True
            )
            return

        if user.id in self.active_games:
            await interaction.response.send_message(
                embed=make_embed("Already Playing", "🎮 You already have a GuessNumber game in progress."), ephemeral=True
            )
            return

        target = random.randint(1, 100)
        self.active_games[user.id] = {"number": target, "attempts": 0, "bet": bet}

        # initial public message
        start_embed = make_embed(
            "🎯 Guess The Number",
            f"{user.mention}, I've picked a number between **1** and **100**.\n"
            f"You have **{MAX_GUESSES}** guesses. Type your guesses in this channel.\n\n"
            f"Bet: **{bet} coins** · Win: **{bet*2} coins**"
        )
        await interaction.response.send_message(embed=start_embed)

        def check(m: discord.Message):
            return m.author.id == user.id and m.channel == interaction.channel and m.content.isdigit()

        while self.active_games[user.id]["attempts"] < MAX_GUESSES:
            try:
                # wait for guess message
                guess_msg = await self.bot.wait_for("message", check=check, timeout=GUESS_TIMEOUT)
            except asyncio.TimeoutError:
                # timeout
                await interaction.followup.send(embed=make_embed(
                    "⌛ Time Out",
                    f"{user.mention}, you took too long. Game ended. The number was **{self.active_games[user.id]['number']}**."
                ))
                del self.active_games[user.id]
                return

            guess = int(guess_msg.content)
            game = self.active_games[user.id]
            game["attempts"] += 1
            remaining = MAX_GUESSES - game["attempts"]

            # small "thinking" animation (edit the followup)
            rolling = await interaction.followup.send(f"🔎 Checking your guess `{guess}`...")
            await asyncio.sleep(0.8)
            await rolling.edit(content=f"🔎 Checking your guess `{guess}`... done.")

            if guess == game["number"]:
                win_amount = game["bet"] * 2
                win_embed = make_embed(
                    "🎉 Correct!",
                    f"{user.mention} guessed **{guess}** — that’s the number!\n\n"
                    f"🏆 You won **{win_amount} coins**.\n"
                    f"Guesses used: **{game['attempts']} / {MAX_GUESSES}**"
                )
                await interaction.followup.send(embed=win_embed)
                del self.active_games[user.id]
                return
            else:
                hint = "⬆️ Too low!" if guess < game["number"] else "⬇️ Too high!"
                hint_embed = make_embed(
                    f"{hint}",
                    f"{user.mention}, `{guess}` is not it. {remaining} guesses left."
                )
                await interaction.followup.send(embed=hint_embed)

        # out of guesses
        number = self.active_games[user.id]["number"]
        lose_embed = make_embed(
            "💀 Out of Guesses",
            f"{user.mention}, you're out of guesses. The number was **{number}**.\n"
            f"You lost **{bet} coins**. Better luck next time!"
        )
        await interaction.followup.send(embed=lose_embed)
        del self.active_games[user.id]


async def setup(bot):
    await bot.add_cog(GuessNumber(bot))
