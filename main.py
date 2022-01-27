from unicodedata import name
import discord
from discord.ext import commands
import os
from webserver import keep_alive
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord import Color
import sqlite3
import random
import asyncio
from discord.ext.commands import cooldown, BucketType

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='$',
                      case_insensitive=True,
                      intents=intents, help_command=None)

slash = SlashCommand(client, sync_commands=True)

db = sqlite3.connect('mainbank.db')
cursor = db.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS account_table (user_id int PRIMARY KEY, wallet_amt int, bank_amt int)"""
)
db.commit()

@client.event
async def on_ready():
    print("Bot is ready.")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="For $Helpme.")
    await client.change_presence(status=discord.Status.dnd, activity=activity)

@client.command()
async def td(ctx):
    pass

@client.command()
async def nacc(ctx):
    member = ctx.author.id
    cursor.execute(f"INSERT OR IGNORE INTO account_table VALUES(?,?,?)",
                   (int(member), 0, 0))
    db.commit()
    embed = discord.Embed(
        title='Account created.',
        description=f'**Account created for {ctx.author.mention}**',
        color=0x00ff05)
    embed.add_field(name="wallet", value='0', inline=True)
    embed.add_field(name="bank", value='0', inline=True)
    await ctx.send(embed=embed)


@client.command(aliases=["bal"])
async def balance(ctx):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
    )
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {ctx.author.id};")
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    embed = discord.Embed(
        title=f'Account Balance.',
        description=f'**:coin: :dollar: This is the balance of your account.**',
        color=0xff0000)
    embed.set_image(
        url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/285/classical-building_1f3db-fe0f.png"
    )
    embed.add_field(name=f'Wallet', value=f'{result_w} :coin:', inline=True)
    embed.add_field(name=f'Bank', value=f'{result_b} :dollar:', inline=True)
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def beg(ctx):
    chance = random.randint(1, 3)
    if chance % 2 != 0:
        cursor.execute(
            f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
        )
        db.commit()
        result = cursor.fetchall()
        result = str(result).strip('[](),')
        result = int(result)
        earnings = random.randint(10, 100)
        result_new = result + earnings
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_new} WHERE user_id = {ctx.author.id}"
        )
        db.commit()
        embed = discord.Embed(
            title='Get a job ffs.',
            description=f'**{ctx.author.mention} begged and got {earnings} :coin: coins. What a loser.**',
            color=0x00ff05)
        await ctx.send(embed=embed)
    else:
        await ctx.send(
            f"Ain't no one giving you anything. {ctx.author.mention}")


@client.command()
async def coinflip(ctx, guess: str, money: int):
    if money < 20000 and money > 200:
        guesses = ("Heads", "Tails")
        chance = random.choice(guesses)
        cursor.execute(
            f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
        )
        db.commit()
        result = cursor.fetchall()
        result = str(result).strip("[](),")
        result = int(result)
        if result < money:
            await ctx.send(
                f"You are broke. You can't bet. {ctx.author.mention}")
        else:

            if guess != chance:
                cursor.execute(
                    f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
                )
                db.commit()
                result = cursor.fetchall()
                result = str(result).strip("[](),")
                result = int(result)
                result = result - money
                await ctx.send(
                    f"You lost, The bet and {money} :coin: coins. {ctx.author.mention}"
                )
                cursor.execute(
                    f"UPDATE account_table SET wallet_amt = {result} WHERE user_id = {ctx.author.id};"
                )
                db.commit()
            elif guess == chance:
                cursor.execute(
                    f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
                )
                db.commit()
                result = cursor.fetchall()
                result = str(result).strip("[](),")
                result = int(result)
                result = result + money
                await ctx.send(
                    f"You won, The bet and {money} :coin: coins. {ctx.author.mention}"
                )
                cursor.execute(
                    f"UPDATE account_table SET wallet_amt = {result} WHERE user_id = {ctx.author.id};"
                )
                db.commit()
    else:
        await ctx.send(
            "The maximum you can bet is 20k and the minimum is 200. Don't flex your money or don't show you are broke..."
        )


@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def work(ctx):
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {ctx.author.id};")
    db.commit()
    result = cursor.fetchall()
    result = str(result).strip("[](),")
    result = int(result)
    chance = random.randint(1, 3)
    actual_work = random.randint(1, 6)
    guess = random.randint(1, 6)
    if chance % 2 != 0:
        if guess < actual_work:
            earnings = random.randint(200, 400)
            embed = discord.Embed(
                title='Work not done.',
                description=f'**Your work merely satisfied your employer, You earned {earnings} :coin: coins.**',
                color=0xff0000)
            embed.set_image(
                url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/joypixels/291/cross-mark_274c.png"
            )
            embed.set_footer(text='Work harder.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {ctx.author.id};"
            )
            db.commit()
            await ctx.send(embed=embed)
        elif guess <= actual_work:
            earnings = random.randint(400, 800)
            embed = discord.Embed(
                title='Work done.',
                description=f'**Your work satisfied your employer, You earned {earnings} :coin: coins.**',
                color=0x000000)
            embed.set_footer(text='Well done.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {ctx.author.id};"
            )
            db.commit()
            await ctx.send(embed=embed)
        elif guess > actual_work:
            earnings = random.randint(800, 1000)
            embed = discord.Embed(
                title='Work perfectly done.',
                description=f'**Your employer was really happy with your work, You earned {earnings} :coin: coins.**',
                color=0x00ff05)
            embed.set_image(url="https://emoji.gg/assets/emoji/CheckMark.png")
            embed.set_footer(text='Nice work.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {ctx.author.id};"
            )
            db.commit()
            await ctx.send(embed=embed)
    else:
        await ctx.send(
            f"You tried acting sigma but ended up being a beta. you earn 0 coins. {ctx.author.mention}"
        )


@client.command(aliases=['dp'])
async def deposit(ctx, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {ctx.author.id};")
    db.commit()
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    result_b = int(result_b)
    if money > result_w:
      await ctx.send(f"You can't deposit more many than you have... {ctx.author.mention}")
    elif money <= result_w:
      result_w = result_w - money
      result_b = result_b + money
      cursor.execute(
          f"UPDATE account_table SET wallet_amt = {result_w}, bank_amt = {result_b} WHERE user_id = {ctx.author.id}")
      db.commit()
      embed = discord.Embed(title='Money deposited.',
                            description=f'{money} :coin:  was deposited to your account.', color=0x00ff05)
      embed.add_field(name='wallet', value=f'{result_w} :coin:', inline=True)
      embed.add_field(name='bank', value=f'{result_b} :dollar:', inline=True)
      await ctx.send(embed=embed)


@client.command(aliases=['wd'])
async def withdraw(ctx, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {ctx.author.id};")
    db.commit()
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    result_b = int(result_b)
    if money > result_b:
      await ctx.send(f"You can't withdraw more many than you have... {ctx.author.mention}")
    elif money <= result_b:
      result_w = result_w + money
      result_b = result_b - money
      cursor.execute(
          f"UPDATE account_table SET wallet_amt = {result_w}, bank_amt = {result_b} WHERE user_id = {ctx.author.id}")
      db.commit()
      embed = discord.Embed(title='Money Withdrawn.',
                            description=f'{money} was withdrawn from your account.', color=0x00ff05)
      embed.add_field(name='wallet', value=f'{result_w} :coin:', inline=True)
      embed.add_field(name='bank', value=f'{result_b} :dollar:', inline=True)
      await ctx.send(embed=embed)


@client.command()
async def tsend(ctx, member: discord.Member, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {member.id};")
    db.commit()
    result_wm = str(cursor.fetchone())
    result_wm = str(result_wm).strip('[](),')
    result_wm = int(result_wm)
    if money > result_w:
        embed = discord.Embed(
            title='Don\'t try to oversmart me.',
            description='**You can\'t give money to someone you don\'t have.**',
            color=0xff0000)
        embed.set_footer(text='I mean come on that\'s common sense.')
    elif money <= result_w:
        result_w = result_w - money
        result_wm = result_wm + money
        cursor.execute(
            f"UPDATE account_table SET bank_amt = {result_w} WHERE user_id = {ctx.author.id};"
        )
        db.commit()
        cursor.execute(
            f"UPDATE account_table SET bank_amt = {result_wm} WHERE user_id = {member.id};"
        )
        db.commit()
        await ctx.send(
            f"**{ctx.author.mention} transfered {member.mention} {money} :coin: coins.**"
        )


@client.command()
async def wsend(ctx, member: discord.Member, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {ctx.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {member.id};")
    db.commit()
    result_wm = str(cursor.fetchone())
    result_wm = str(result_wm).strip('[](),')
    result_wm = int(result_wm)
    if money > result_w:
        embed = discord.Embed(
            title='Don\'t try to oversmart me.',
            description='**You can\'tgive money to someone you don\'t have.**',
            color=0xff0000)
        embed.set_footer(text='I mean come on that\'s common sense.')
    elif money <= result_w and money <= 20000:
        result_w = result_w - money
        result_wm = result_wm + money
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_w} WHERE user_id = {ctx.author.id};"
        )
        db.commit()
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_wm} WHERE user_id = {member.id};"
        )
        db.commit()
        await ctx.send(
            f"**{ctx.author.mention} gave {member.mention} {money}:coin: coins.**"
        )
    else:
        await ctx.send(
            "You can't send more than 20000 coins via hand. Use v!transfermoney for transfering money to bank account."
        )

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: commands.MemberConverter, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title='Kicked.',
        description=
        f'**{member.mention} has been kicked by {ctx.message.author}.**',
        color=0xff0000)
    embed.add_field(name='Reason.', value=f'{reason}', inline=True)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: commands.MemberConverter, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title='Banned.',
        description=
        f'**{member.mention} has been banned by {ctx.message.author}.**',
        color=0xff0000)
    embed.add_field(name='Reason.', value=f'{reason}', inline=True)
    await ctx.send(embed=embed)


@client.command(name='unban')
@commands.has_permissions(ban_members=True)
async def _unban(self, ctx, id: int):
    user = await self.client.fetch_user(id)
    embed = discord.Embed(
        title='Unbanned.',
        description=
        f'**{user.mention} has been unbanned by {ctx.message.author}.**',
        color=0x00ff05)
    await ctx.send(embed=embed)
    await ctx.guild.unban(user)


@client.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: commands.MemberConverter, *, reason=None):
    if member.id == 385397540968988672 in ctx.message.content:
        await ctx.send(
            f'{ctx.author.mention} not a good idea trying to mute the server owner...'
        )
    else:
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        await member.add_roles(mutedRole, reason=reason)
        embed = discord.Embed(
            title=f'Muted.',
            description=f'**{member.mention} has been muted.**',
            color=0xff0000)
        embed.add_field(name='reason', value=f'{reason}', inline=True)
        await ctx.send(embed=embed)
        await member.send(embed=embed)


@client.command()
@commands.has_permissions(manage_messages=True)
async def tmute(ctx, member: discord.Member, time):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    tempmute = int(time[0]) * time_convert[time[-1]]
    await ctx.message.delete()
    await member.add_roles(muted_role)
    embed = discord.Embed(
        description=
        f"✅ **{member.display_name}#{member.discriminator} muted successfully.**",
        color=0x00ff05)
    await ctx.send(embed=embed, delete_after=5)
    await asyncio.sleep(tempmute)
    await member.remove_roles(muted_role)


@client.command()
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: commands.MemberConverter):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    embed = discord.Embed(
        title=f'Unmuted.',
        description=f'**{member.mention} has been unmuted.**',
        color=0x00ff05)
    await ctx.send(embed=embed)
    await member.send(embed=embed)


@client.command(aliases=['clr', 'cls'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=10):
    channel = ctx.message.channel
    await ctx.channel.purge(limit=amount + 1)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def add_role(ctx, member: commands.MemberConverter, role: discord.Role):
    await member.add_roles(role)
    embed = discord.Embed(
        title='Role given.',
        description=f'**{member.mention} has been given {role} role.**',
        color=0x00ff05)
    await ctx.send(embed=embed)
    await member.send(embed=embed)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def remove_role(ctx,
                      member: commands.MemberConverter,
                      role: discord.Role,
                      *,
                      reason=None):
    await member.remove_roles(role)
    embed = discord.Embed(
        title='Role removed.',
        description=f'**{role} role has been removed from {member.mention}** ',
        color=0xff0000)
    embed.add_field(name='Reason', value=f'{reason}', inline=True)
    await ctx.send(embed=embed)
    await member.send(embed=embed)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            f"No such command, {ctx.author.mention}. type $help for available cmds!"
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Please enter all required arguments.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            f'The command does not take that as the argument, {ctx.author.mention}.'
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            f'I miss the permissions to perform that, Make sure to put my role at the top! {ctx.author.mention}.'
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            f'You miss the roles to use this command! {ctx.author.mention}.')
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title=f'Cool down before I burn you up.',
            description=f'Try the command again in {int(error.retry_after)}s.',
            color=0x000000)
        await ctx.send(embed=embed)
    else:
      raise error


@client.command(aliases=["cmds"])
async def Helpme(ctx):
    embed = discord.Embed(
        title='Help',
        description='These are the commands available for use at the moment.',
        color=0x000000)
    embed.set_author(name=f"{ctx.author.name}")
    embed.add_field(
        name="v!paww",
        value='Happy animals make humans happy, Watch some cute pandas.',
        inline=True)
    embed.add_field(name="$nacc",
                    value='New currency system! Open an account now!',
                    inline=True)
    embed.add_field(name="$beg",
                    value='Beg to get money... Totally not cool but ok.',
                    inline=True)
    embed.add_field(name="$bal",
                    value='Check your bank account balance.',
                    inline=True)
    embed.add_field(
        name="$coinflip",
        value='Feeling lucky? Bet on coin-flipping and earn money.',
        inline=True)
    embed.add_field(name="$work",
                    value='Earn money the right way, Work for it.',
                    inline=True)
    embed.add_field(name="$withdraw",
                    value='Withdraw money from your bank account.',
                    inline=True)
    embed.add_field(name="$deposit",
                    value='Deposit money to your bank account.',
                    inline=True)
    embed.add_field(name="$wsend",
                    value='Give upto 20k coins to anyone by hand.',
                    inline=True)
    embed.add_field(
        name="$tsend",
        value='Transfer as much money as you want to anyone\'s bank account.',
        inline=True)
    await ctx.send(embed=embed)

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run(TOKEN)
