from logging import warning
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
from collections import defaultdict

# Environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise RuntimeError("DISCORD_TOKEN not found")
poll_votes = defaultdict(set)
# Logging setup
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Bot configuration
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True
intents.members = True
intents.typing = True

addRole1 = "PIRATE"

## EVENTS ##
@bot.event
async def on_ready():
  print(f"we are ready to go. {bot.user.name}")

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to the server {member.name} !")
    except discord.Forbidden:
        logging,warning(f"Failed to send message to {member.name}. DM might be disabled.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "trump" in message.content.lower():
        await message.channel.send(f"{message.author.mention} - No, no no.. Not today!")
    await bot.process_commands(message)

## COMMANDS ##
@bot.command()
async def rand(ctx, upper_limit: int):          # random numbers
    try:
        if upper_limit <= 0:
            await ctx.send("Positive numbers only. Try again.")
            return

        random_number = random.randint(1, upper_limit)
        await ctx.send(f"Your random number is: {random_number}")
    except ValueError:
        await ctx.send("Invalid input. Enter a valid number please.")
    except Exception as e:
        logging.error(f"Error in rand command: {e}")
        await ctx.send("An unexpected error occurred. Please try again.")

@bot.command()
async def assign(ctx):                         # assign roles
    try:
        role = discord.utils.get(ctx.guild.roles, name=addRole1)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} has been assigned the role of: {role}!")
        else:
            await ctx.send("Role does not exist.")
    except discord.Forbidden:
        logging.warning("Bot doesn't have permission to assign roles.")
        await ctx.send("I don't have permission to assign roles.")
    except discord.DiscordException as e:
        logging.error(f"Error in assign command: {e}")
        await ctx.send("Failed to assign role due to an error.")

@bot.command()
async def remove(ctx):                           # remove roles
    try:
        role = discord.utils.get(ctx.guild.roles, name=addRole1)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention}, your {role} role has been removed.")
        else:
            await ctx.send("Role does not exist.")
    except discord.Forbidden:
        logging.warning("Bot doesn't have permission to remove roles.")
        await ctx.send("I don't have permission to remove roles.")
    except discord.DiscordException as e:
        logging.error(f"Error in remove command: {e}")
        await ctx.send("Failed to remove role due to an unexpected error.")

@bot.command()
@commands.has_role(addRole1)
async def test(ctx):                            # can use only if valid level of auth
    try:
        await ctx.send("Welcome to the club bud.")
    except discord.DiscordException as e:
        logging.error(f"Error in test command: {e}")
        await ctx.send("Oops! Something went wrong.")

@bot.command()
async def ping(ctx):                            # test command
    await ctx.send("Pong!")

@bot.command()
async def dm(ctx, *, msg):                          # dm the user
    try:
        await ctx.author.send(f"You said: {msg}")
    except discord.Forbidden:
        logging.warning(f"Failed to send DM to {ctx.author}. DMs might be disabled.")
        await ctx.send("I can't send a DM to you. Please check your privacy settings.")

@bot.command()
async def reply(ctx):                                 # reply to the user
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def poll(ctx, *, question):                   # creates poll -> !poll does bapper smell?
    try:
        embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
        poll_message = await ctx.send(embed=embed)

        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")

        poll_votes[poll_message.id] = set()

    except discord.DiscordException as e:
        logging.error(f"Error in poll command: {e}")
        await ctx.send("Failed to create poll due to an unexpected error.")
# poll events
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    if message_id not in poll_votes:
        return

    if user.id in poll_votes[message_id]:
        try:
            await reaction.remove(user)
            await reaction.message.channel.send(f"{user.mention}, you can only vote once!")
        except discord.Forbidden:
            logging.warning(f"Failed to remove reaction from {user.name}.")
        except discord.DiscordException as e:
            logging.error(f"Error in on_reaction_add: {e}")
    else:
        poll_votes[message_id].add(user.id)
@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    if message_id in poll_votes and user.id in poll_votes[message_id]:
        poll_votes[message_id].remove(user.id)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command! Use `!help` to see the available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("A required argument is missing. Please check your command and try again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to execute this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the required permissions for this action.")
    else:
        logging.error(f"Unexpected error: {error}")
        await ctx.send("An unexpected error occurred. Please try again.")

@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the required role to use this command.")
    else:
        await ctx.send("An unexpected error occurred.")
        logging.error(f"Unexpected error in test command: {error}")



# runs bot. bot will only be active when script is running
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

