from unicodedata import name
import discord
from discord.ext import commands
import os
from webserver import keep_alive
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord import Color

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='$',
                      case_insensitive=True,
                      intents=intents, help_command=None)

slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
    print("Bot is ready.")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="For $help")
    await client.change_presence(status=discord.Status.dnd, activity=activity)

@client.command()
async def help(ctx):
    embed = discord.Embed(title='Commands', description='**These are the commands available to you at the moment.**', color = discord.Color.green())
    embed.add_field(name='help', value='Shows this embed.', inline = True)
    embed.set_author(name=f"{ctx.author.name}")
    embed.set_footer(text='Made by ! H1ddeN#1952 and Prakhar#7004')
    await ctx.send(embed=embed)

@slash.slash(name='ping', description='Pings the user, Testing slash commands.')
async def ping(ctx):
    await ctx.send(f"{ctx.author.mention}")

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run(TOKEN)
