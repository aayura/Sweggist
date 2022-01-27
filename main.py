import discord
from discord.ext import commands
import os
from webserver import keep_alive
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='sw',
                      case_insensitive=True,
                      intents=intents)


@client.event
async def on_ready():
    print("Bot is ready.")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="For help, swhelp.")
    await client.change_presence(status=discord.Status.dnd, activity=activity)

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run(TOKEN)
