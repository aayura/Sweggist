from unicodedata import name
import discord
from discord.ext import commands
import os
from webserver import keep_alive
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='sw',
                      case_insensitive=True,
                      intents=intents, help_command=None)

slash = SlashCommand(client)

@client.event
async def on_ready():
    print("Bot is ready.")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="For sw_helpme")
    await client.change_presence(status=discord.Status.dnd, activity=activity)

@client.command()
async def help(ctx):
    embed = discord.Embed(title='Commands', description='These are the commands available to you at the moment.', color = discord.color.Green())
    embed.add_field(name='help', value='Shows this embed.', inline = True)
    await ctx.send(embed=embed)
    
# just for committing issues.

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run(TOKEN)
