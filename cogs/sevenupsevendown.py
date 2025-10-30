import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

EMBED_COLOR = discord.Color.purple()
ROLL_ANIM_SECONDS = 1.0

def make_embed(title: str, description: str, color=EMBED_COLOR):
    return discord.Embed(title=title, description=description, color=color)

class SevenUpSevenDown(commands.Cog):
    """7 Up 7 Down dice game — polished presentation and rolling animation."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="7up7down", description="Bet on 7 Up (sum>7) or 7 Down (sum<7). House wins on 7.")
    @app_commands.describe(bet="Bet amount (>0)", choice="Choose Up or Down")
    @app_commands.choices(choice=[
        app_commands.Choice(name="7 Up (sum > 7)", value="up"),
        app_commands.Choice(name="7 Down (sum < 7)", value="down")
    ])
    async def seven_up_down(self, interaction: discord.Interaction, bet: int, choice: app_commands.Choice[str]):
        user = interaction.user
        if bet <= 0:
            await interaction.response.send_message(embed=make_embed("Invalid Bet", "💸 Bet must be > 0."), ephemeral=True)
            return

        player_choice = choice.value  # "up" or "down"
        await interaction.response.send_message(embed=make_embed("🎲 7 Up 7 Down", f"{user.mention} bet **{bet} coins** on **{choice.name}**"))

        # send a rolling placeholder, then update after a short delay
        rolling_msg = await interaction.followup.send("🎲 Rolling the dice...")
        await asyncio.sleep(ROLL_ANIM_SECONDS)

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2

        # Build result embed
        if total == 7:
            # house wins on exactly 7
            desc = (
                f"🎲 You rolled **{dice1}** and **{dice2}** → **{total}**\n\n"
                f"😬 It’s exactly **7** — the house wins. You lost **{bet} coins**."
            )
            result_embed = make_embed("😵 House Wins on 7", desc)
            await rolling_msg.edit(content=None, embed=result_embed)
            return

        result = "up" if total > 7 else "down"
        success = (player_choice == result)

        if success:
            desc = (
                f"🎲 You rolled **{dice1}** and **{dice2}** → **{total}**\n\n"
                f"🎉 {user.mention}, you guessed **{choice.name}** and won **{bet*2} coins!** 🪙"
            )
            title = "🎉 You Win!"
        else:
            desc = (
                f"🎲 You rolled **{dice1}** and **{dice2}** → **{total}**\n\n"
                f"💀 {user.mention}, you guessed **{choice.name}**, but the result was **{'7 Up' if result=='up' else '7 Down'}**.\n"
                f"You lost **{bet} coins**."
            )
            title = "💔 You Lose"

        result_embed = make_embed(title, desc)
        await rolling_msg.edit(content=None, embed=result_embed)


async def setup(bot):
    await bot.add_cog(SevenUpSevenDown(bot))
