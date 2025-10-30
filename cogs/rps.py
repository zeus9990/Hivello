import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

EMBED_COLOR = discord.Color.green()
CHOICES = {
    "rock": ("Rock 🪨", "🪨"),
    "paper": ("Paper 📄", "📄"),
    "scissors": ("Scissors ✂️", "✂️"),
}

def make_embed(title: str, description: str, color=EMBED_COLOR):
    return discord.Embed(title=title, description=description, color=color)

class RockPaperScissors(commands.Cog):
    """Rock Paper Scissors with embeds and a short reveal animation."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Play Rock Paper Scissors. Win = double your bet.")
    @app_commands.describe(bet="Bet amount (> 0)", choice="Your move")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock 🪨", value="rock"),
        app_commands.Choice(name="Paper 📄", value="paper"),
        app_commands.Choice(name="Scissors ✂️", value="scissors"),
    ])
    async def rps(self, interaction: discord.Interaction, bet: int, choice: app_commands.Choice[str]):
        user = interaction.user
        if bet <= 0:
            await interaction.response.send_message(embed=make_embed("Invalid Bet", "💸 Bet must be > 0."), ephemeral=True)
            return

        player_key = choice.value
        player_label, player_emoji = CHOICES[player_key]

        # initial ephemeral acknowledgement to avoid long response latency for slash
        await interaction.response.send_message(embed=make_embed("🪨📄✂️ RPS", f"{user.mention} chose **{player_label}**\nBet: **{bet} coins**"))

        # small suspense
        thinking = await interaction.followup.send("🤖 The bot is thinking...")
        await asyncio.sleep(1.0)

        bot_choice_key = random.choice(list(CHOICES.keys()))
        bot_label, bot_emoji = CHOICES[bot_choice_key]

        # determine outcome
        if player_key == bot_choice_key:
            outcome = "tie"
        else:
            wins = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}
            outcome = "win" if (player_key, bot_choice_key) in wins else "lose"

        # edit the thinking message into a neat embed result
        title = {"win": "🎉 You Win!", "lose": "💀 You Lose", "tie": "🤝 It's a Tie"}[outcome]
        description = (
            f"{user.mention} **{player_label}** {player_emoji}\n"
            f"Bot **{bot_label}** {bot_emoji}\n\n"
        )
        if outcome == "win":
            description += f"You won **{bet*2} coins**! 🪙"
        elif outcome == "lose":
            description += f"You lost **{bet} coins**. Better luck next time!"
        else:
            description += "It's a tie — your bet is returned."

        result_embed = make_embed(title, description)
        await thinking.edit(content=None, embed=result_embed)


async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))
