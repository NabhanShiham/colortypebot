import discord
import random
import time
from discord.ext import commands
import asyncio

# Set up intents to enable message content access
intents = discord.Intents.default()
intents.message_content = True  # Required to access message content

# Initialize bot with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Expanded color targets dictionary with at least 20 colors
color_targets = {
    "🔴": "red",
    "🔵": "blue",
    "🟢": "green",
    "🟡": "yellow",
    "🟠": "orange",
    "🟣": "purple",
    "🟤": "brown",
    "⚫": "black",
    "⚪": "white"
}

# Dictionary to store each player's cumulative reaction times and number of rounds completed
reaction_times = {}
round_counts = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def reactionchallenge(ctx, opponent: discord.Member):
    # Ensure the player isn't challenging themselves
    if opponent == ctx.author:
        await ctx.send("You can't challenge yourself!")
        return

    await ctx.send(f"{ctx.author.mention} has challenged {opponent.mention} to a reaction time game! Get ready...")

    # Initialize reaction times and round counts for both players
    reaction_times[ctx.author] = 0
    reaction_times[opponent] = 0
    round_counts[ctx.author] = 0
    round_counts[opponent] = 0
    
    game_active = False

    # Start rounds
    for round_num in range(5):  # 5 rounds
        # Choose a random target emoji and get its color name
        target_emoji, target_color = random.choice(list(color_targets.items()))
        await ctx.send(f"**Round {round_num + 1}! Target:** {target_emoji} - Type the color!")

        # Track start time
        start_time = time.time()

        # Check for correct responses
        def check(message):
            return message.author in [ctx.author, opponent] and message.content.lower() == target_color and message.channel == ctx.channel

        try:
            # Wait for a response within 5 seconds
            response = await bot.wait_for("message", check=check, timeout=5)
            end_time = time.time()
            reaction_time = end_time - start_time

            # Add reaction time to the player's total and increment their round count
            reaction_times[response.author] += reaction_time
            round_counts[response.author] += 1
            await ctx.send(f"{response.author.mention} got it right in {reaction_time:.2f} seconds!")
            game_active = True 
        except asyncio.TimeoutError:
            # Apply a high penalty if no response within the time limit
            await ctx.send(f"No one responded in time! Moving to the next round.")
            # Add a penalty time for players who didn't respond and increment their round count
            reaction_times[ctx.author] += 999    
            reaction_times[opponent] += 999  
            round_counts[ctx.author] += 1
            round_counts[opponent] += 1

    if not game_active:
        await ctx.send("Oh no, neither player responded in any round! The game ends sadly.")
        return

    # Calculate average reaction time for each player
    average_times = {}

    for player in reaction_times:
        if round_counts[player] > 0:
            average_times[player] = reaction_times[player] / round_counts[player]
        else:
            average_times[player] = float('inf')

    # Determine the winner based on the lowest average reaction time
    winner = min(average_times, key=average_times.get)
    if average_times[winner] == float('inf'):
        await ctx.send(f"Neither player responded correctly in any round...ending the game.")
    else: 
        await ctx.send(f"{winner.mention} wins the game with an average reaction time of {average_times[winner]:.2f} seconds!")

    # Clear reaction times and round counts for the next game
    reaction_times.clear()
    round_counts.clear()

# add token here
# bot.run("")
