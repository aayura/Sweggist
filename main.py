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

@slash.slash(name='helpme', description='Tells you the available commands.', guild_ids=[935002085685100544])
async def help(ctx: SlashContext):
    embed = discord.Embed(title='HELP COMMAND', description='/helpme - Will show this command', color = 0x0BD4B0)
    await ctx.send(content='_helpme', embeds=[embed])

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run(TOKEN)
