import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
"""
!help - !ban - !kick - !mute(no msg send) - !unmute - !play(add music command to search google)
!stop - !pause - !resume - !info(server or user info(maybe try and add analytics)) - !welcome
-------------------------------------------------------------------------------------------------
!translate(toss to google translate possibly) - !random(#) - !stats(tracks activity) - !quote
!tz(timezone converter) - !suggestion(user offered for whatever i guess) 
"""



load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# INTENTS(might need to put more for different permissions)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.typing = True
# prefix for bot commands
bot = commands.Bot(command_prefix='!', intents=intents)

addRole1 = "PIRATE"
# bigBossRole = "Admin"  add this role under bappers top role for ban/kick

@bot.event
async def on_ready():
  print(f"we are ready to go. {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name} !")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "trump" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - No, no no.. Not today!")
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.metion}!")
# roles assign and remove
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=addRole1)
    if role:
        await ctx.author.add_roles(role)
        await  ctx.send(f"{ctx.author.mention} has been assigned the role of: {role}!")
    else:
        await ctx.send("Role does not exist.")
@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=addRole1)
    if role:
        await ctx.author.remove_roles(role)
        await  ctx.send(f"{ctx.author.mention}, your {role} role has been removed.")
    else:
        await ctx.send("Role does not exist.")
# testing out commands
@bot.command()
@commands.has_role(addRole1)
async def test(ctx):
    await ctx.send("Welcome to the club bud.")
@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the required role.")
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")
@bot.command()
async def reply(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")


# runs bot. bot will only be active when script is running
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

