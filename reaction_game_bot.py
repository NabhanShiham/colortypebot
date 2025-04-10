import discord
import random
import time
from discord.ext import commands
import asyncio


intents = discord.Intents.default()
intents.message_content = True  


bot = commands.Bot(command_prefix="!", intents=intents)


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

reaction_times = {}
round_counts = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def reactionchallenge(ctx, opponent: discord.Member):
    if opponent == ctx.author:
        await ctx.send("You can't challenge yourself!")
        return

    await ctx.send(f"{ctx.author.mention} has challenged {opponent.mention} to a reaction time game! Get ready...")

    reaction_times[ctx.author] = 0
    reaction_times[opponent] = 0
    round_counts[ctx.author] = 0
    round_counts[opponent] = 0
    
    game_active = False

    for round_num in range(5): 
        target_emoji, target_color = random.choice(list(color_targets.items()))
        await ctx.send(f"**Round {round_num + 1}! Target:** {target_emoji} - Type the color!")

        start_time = time.time()

        def check(message):
            return message.author in [ctx.author, opponent] and message.content.lower() == target_color and message.channel == ctx.channel

        try:
            response = await bot.wait_for("message", check=check, timeout=5)
            end_time = time.time()
            reaction_time = end_time - start_time

            reaction_times[response.author] += reaction_time
            round_counts[response.author] += 1
            await ctx.send(f"{response.author.mention} got it right in {reaction_time:.2f} seconds!")
            game_active = True 
        except asyncio.TimeoutError:
            await ctx.send(f"No one responded in time! Moving to the next round.")
            reaction_times[ctx.author] += 999    
            reaction_times[opponent] += 999  
            round_counts[ctx.author] += 1
            round_counts[opponent] += 1

    if not game_active:
        await ctx.send("Oh no, neither player responded in any round! The game ends sadly.")
        return

    average_times = {}

    for player in reaction_times:
        if round_counts[player] > 0:
            average_times[player] = reaction_times[player] / round_counts[player]
        else:
            average_times[player] = float('inf')

    winner = min(average_times, key=average_times.get)
    if average_times[winner] == float('inf'):
        await ctx.send(f"Neither player responded correctly in any round...ending the game.")
    else: 
        await ctx.send(f"{winner.mention} wins the game with an average reaction time of {average_times[winner]:.2f} seconds!")

    reaction_times.clear()
    round_counts.clear()

# add token here
# bot.run("")
