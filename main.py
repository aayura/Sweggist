import disnake
from disnake.ext import commands
from webserver import keep_alive
import os
import random
import json
import asyncio
import sqlite3

intents = disnake.Intents.all()
intents.members = True

client = disnake.Client()

bot = commands.Bot(command_prefix="$", test_guilds=[935002085685100544], sync_commands_debug=True, case_insensitive=True, intents=intents,help_command=False)

db = sqlite3.connect('mainbank.db')
cursor = db.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS account_table (user_id int PRIMARY KEY, wallet_amt int, bank_amt int)"""
)
db.commit()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS suggestions (msg_id int PRIMARY KEY,user_name text,suggestion text)"""
)
db.commit()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS shop_items (item_id text PRIMARY KEY, quantity int, amount int)""")
db.commit()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")
    activity = disnake.Activity(type=disnake.ActivityType.watching,
                                name="For /help.")
    await client.change_presence(status=disnake.Status.dnd, activity=activity)

@bot.slash_command(description="Play Truth and Dare with your friends.")
async def td(inter, *Players: commands.MemberConverter):
    lst = []
    for i in Players:
        lst.append(i)
    player = random.choice(lst)
    await inter.response.send_message(f'{player}, Its your turn to choose.\n')
    await inter.response.send_message("Truth or dare?")
    with open("tdq.json", "r") as f:
        data = json.load(f)

        def check(msg):
          return msg.author.id == player.id and msg.channel == inter.channel and msg.content.lower() in ["truth", "dare"]
        msg = await bot.wait_for("message", check=check, timeout=10)
        try:
            if msg.content.lower() == "truth":
                await inter.response.send_message(random.choice(data["truth"]))
            elif msg.content.lower() == "dare":
                await inter.response.send_message(random.choice(data["truth"]))
                await (random.choice(data["dare"]))
            else:
                await inter.response.send_message(random.choice(data["truth"]))
                await ("This is truth and dare not something else, Choose from truth or dare.")
        except asyncio.TimeoutError:
            await inter.response.send_message("Timed out!")

@bot.slash_command(description="Open a bank account.")
async def nacc(inter):
    member = inter.author.id
    cursor.execute(f"INSERT OR IGNORE INTO account_table VALUES(?,?,?)",
                   (int(member), 0, 0))
    db.commit()
    embed = disnake.Embed(
        title='Account created.',
        description=f'**Account created for {inter.author.mention}**',
        color=0x00ff05)
    embed.add_field(name="wallet", value='0', inline=True)
    embed.add_field(name="bank", value='0', inline=True)
    await inter.response.send_message(embed=embed)

@bot.slash_command(description="Check your account balance.")
async def bal(inter):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
    )
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {inter.author.id};")
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    embed = disnake.Embed(
        title=f'Account Balance.',
        description=f'**:coin: :dollar: This is the balance of your account.**',
        color=0xff0000)
    embed.set_image(
        url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/285/classical-building_1f3db-fe0f.png"
    )
    embed.add_field(name=f'Wallet', value=f'{result_w} :coin:', inline=True)
    embed.add_field(name=f'Bank', value=f'{result_b} :dollar:', inline=True)
    await inter.response.send_message(embed=embed)

@bot.slash_command(description="Beg for money.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def beg(inter):
    chance = random.randint(1, 3)
    if chance % 2 != 0:
        cursor.execute(
            f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
        )
        db.commit()
        result = cursor.fetchall()
        result = str(result).strip('[](),')
        result = int(result)
        earnings = random.randint(10, 100)
        result_new = result + earnings
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_new} WHERE user_id = {inter.author.id}"
        )
        db.commit()
        embed = disnake.Embed(
            title='Get a job ffs.',
            description=f'**{inter.author.mention} begged and got {earnings} :coin: coins. What a loser.**',
            color=0x00ff05)
        await inter.response.send_message(embed=embed)
    else:
        await inter.response.send_message(
            f"Ain't no one giving you anything. {inter.author.mention}")

@bot.slash_command(description="Flip a coin and bet on the result.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def coinflip(inter, guess: str, money: int):
    if money < 20000 and money > 200:
        guesses = ("Heads", "Tails")
        chance = random.choice(guesses)
        cursor.execute(
            f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
        )
        db.commit()
        result = cursor.fetchall()
        result = str(result).strip("[](),")
        result = int(result)
        if result < money:
            await inter.response.send_message(
                f"You are broke. You can't bet. {inter.author.mention}")
        else:

            if guess != chance:
                cursor.execute(
                    f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
                )
                db.commit()
                result = cursor.fetchall()
                result = str(result).strip("[](),")
                result = int(result)
                result = result - money
                await inter.response.send_message(
                    f"You lost, The bet and {money} :coin: coins. {inter.author.mention}"
                )
                cursor.execute(
                    f"UPDATE account_table SET wallet_amt = {result} WHERE user_id = {inter.author.id};"
                )
                db.commit()
            elif guess == chance:
                cursor.execute(
                    f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
                )
                db.commit()
                result = cursor.fetchall()
                result = str(result).strip("[](),")
                result = int(result)
                result = result + money
                await inter.response.send_message(
                    f"You won, The bet and {money} :coin: coins. {inter.author.mention}"
                )
                cursor.execute(
                    f"UPDATE account_table SET wallet_amt = {result} WHERE user_id = {inter.author.id};"
                )
                db.commit()
    else:
        await inter.response.send_message(
            "The maximum you can bet is 20k and the minimum is 200. Don't flex your money or don't show you are broke..."
        )

@bot.slash_command(description="Work for your money.")
async def work(inter):
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {inter.author.id};")
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
            embed = disnake.Embed(
                title='Work not done.',
                description=f'**Your work merely satisfied your employer, You earned {earnings} :coin: coins.**',
                color=0xff0000)
            embed.set_image(
                url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/joypixels/291/cross-mark_274c.png"
            )
            embed.set_footer(text='Work harder.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {inter.author.id};"
            )
            db.commit()
            await inter.response.send_message(embed=embed)
        elif guess <= actual_work:
            earnings = random.randint(400, 800)
            embed = disnake.Embed(
                title='Work done.',
                description=f'**Your work satisfied your employer, You earned {earnings} :coin: coins.**',
                color=0x000000)
            embed.set_footer(text='Well done.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {inter.author.id};"
            )
            db.commit()
            await inter.response.send_message(embed=embed)
        elif guess > actual_work:
            earnings = random.randint(800, 1000)
            embed = disnake.Embed(
                title='Work perfectly done.',
                description=f'**Your employer was really happy with your work, You earned {earnings} :coin: coins.**',
                color=0x00ff05)
            embed.set_image(url="https://emoji.gg/assets/emoji/CheckMark.png")
            embed.set_footer(text='Nice work.')
            new_result = result + earnings
            cursor.execute(
                f"UPDATE account_table SET bank_amt = {new_result} WHERE user_id = {inter.author.id};"
            )
            db.commit()
            await inter.response.send_message(embed=embed)
    else:
        await inter.response.send_message(
            f"You tried acting sigma but ended up being a beta. you earn 0 coins. {inter.author.mention}"
        )

@bot.slash_command(description="Deposit money to your bank account.")
async def dp(inter, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {inter.author.id};")
    db.commit()
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    result_b = int(result_b)
    if money > result_w:
      await inter.response.send_message(f"You can't deposit more many than you have... {inter.author.mention}")
    elif money <= result_w:
      result_w = result_w - money
      result_b = result_b + money
      cursor.execute(
          f"UPDATE account_table SET wallet_amt = {result_w}, bank_amt = {result_b} WHERE user_id = {inter.author.id}")
      db.commit()
      embed = disnake.Embed(title='Money deposited.',
                            description=f'{money} :coin:  was deposited to your account.', color=0x00ff05)
      embed.add_field(name='wallet', value=f'{result_w} :coin:', inline=True)
      embed.add_field(name='bank', value=f'{result_b} :dollar:', inline=True)
      await inter.response.send_message(embed=embed)

@bot.slash_command(description="Withdraw money from your bank account.")
async def wd(inter, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
    )
    db.commit()
    result_w = str(cursor.fetchone())
    result_w = str(result_w).strip('[](),')
    result_w = int(result_w)
    cursor.execute(
        f"SELECT bank_amt FROM account_table WHERE user_id = {inter.author.id};")
    db.commit()
    result_b = str(cursor.fetchone())
    result_b = str(result_b).strip('[](),')
    result_b = int(result_b)
    if money > result_b:
      await inter.response.send_message(f"You can't withdraw more many than you have... {inter.author.mention}")
    elif money <= result_b:
      result_w = result_w + money
      result_b = result_b - money
      cursor.execute(
          f"UPDATE account_table SET wallet_amt = {result_w}, bank_amt = {result_b} WHERE user_id = {inter.author.id}")
      db.commit()
      embed = disnake.Embed(title='Money Withdrawn.',
                            description=f'{money} was withdrawn from your account.', color=0x00ff05)
      embed.add_field(name='wallet', value=f'{result_w} :coin:', inline=True)
      embed.add_field(name='bank', value=f'{result_b} :dollar:', inline=True)
      await inter.response.send_message(embed=embed)

@bot.slash_command(description="Give someone money, wallet to wallet.")
async def wsend(inter, member: commands.MemberConverter, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
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
        embed = disnake.Embed(
            title='Don\'t try to oversmart me.',
            description='**You can\'tgive money to someone you don\'t have.**',
            color=0xff0000)
        embed.set_footer(text='I mean come on that\'s common sense.')
    elif money <= result_w and money <= 20000:
        result_w = result_w - money
        result_wm = result_wm + money
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_w} WHERE user_id = {inter.author.id};"
        )
        db.commit()
        cursor.execute(
            f"UPDATE account_table SET wallet_amt = {result_wm} WHERE user_id = {member.id};"
        )
        db.commit()
        await inter.response.send_message(
            f"**{inter.author.mention} gave {member.mention} {money}:coin: coins.**"
        )
    else:
        await inter.response.send_message(
            "You can't send more than 20000 coins via hand. Use $tsend for transfering money to bank account."
        )

@bot.slash_command(description="Transfer someone money, bank to bank.")
async def tsend(inter, member: commands.MemberConverter, money: int):
    cursor.execute(
        f"SELECT wallet_amt FROM account_table WHERE user_id = {inter.author.id};"
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
        embed = disnake.Embed(
            title='Don\'t try to oversmart me.',
            description='**You can\'t give money to someone you don\'t have.**',
            color=0xff0000)
        embed.set_footer(text='I mean come on that\'s common sense.')
    elif money <= result_w:
        result_w = result_w - money
        result_wm = result_wm + money
        cursor.execute(
            f"UPDATE account_table SET bank_amt = {result_w} WHERE user_id = {inter.author.id};"
        )
        db.commit()
        cursor.execute(
            f"UPDATE account_table SET bank_amt = {result_wm} WHERE user_id = {member.id};"
        )
        db.commit()
        await inter.response.send_message(
            f"**{inter.author.mention} transfered {member.mention} {money} :coin: coins.**"
        )

@bot.slash_command(description="Kick someone from the server.")
@commands.has_permissions(kick_members=True)
async def kick(inter, member: commands.MemberConverter, *, reason=None):
    await member.kick(reason=reason)
    embed = disnake.Embed(
        title='Kicked.',
        description=f'**{member.mention} has been kicked by {inter.message.author}.**',
        color=0xff0000)
    embed.add_field(name='Reason.', value=f'{reason}', inline=True)
    await inter.response.send_message(embed=embed)

@bot.slash_command(description="Ban someone from the server.")
@commands.has_permissions(ban_members=True)
async def ban(inter, member: commands.MemberConverter, *, reason=None):
    await member.ban(reason=reason)
    embed = disnake.Embed(
        title='Banned.',
        description=f'**{member.mention} has been banned by {inter.message.author}.**',
        color=0xff0000)
    embed.add_field(name='Reason.', value=f'{reason}', inline=True)
    await inter.response.send_message(embed=embed)

@bot.slash_command(description="Unban someone from the server.")
@commands.has_permissions(ban_members=True)
async def unban(inter, id: int):
    user = await bot.fetch_user(id)
    embed = disnake.Embed(
        title='Unbanned.',
        description=f'**{user.mention} has been unbanned by {inter.message.author}.**',
        color=0x00ff05)
    await inter.response.send_message(embed=embed)
    await inter.guild.unban(user)

@bot.slash_command(description="Mute someone in the server.")
@commands.has_permissions(kick_members=True)
async def mute(inter, member: commands.MemberConverter, *, reason=None):
    guild = inter.guild
    mutedRole = disnake.utils.get(guild.roles, id=935417321453944833)
    await member.add_roles(mutedRole, reason=reason)
    embed = disnake.Embed(
        title=f'Muted.',
        description=f'**{member.mention} has been muted.**',
        color=0xff0000)
    embed.add_field(name='reason', value=f'{reason}', inline=True)
    await inter.response.send_message(embed=embed)
    await member.send(embed=embed)


@bot.slash_command(description="Mute someone for some time in the server.")
@commands.has_permissions(manage_messages=True)
async def tmute(inter, member: disnake.Member, time):
    muted_role = disnake.utils.get(inter.guild.roles, id=935417321453944833)
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    tempmute = int(time[0]) * time_convert[time[-1]]
    await inter.message.delete()
    await member.add_roles(muted_role)
    embed = disnake.Embed(
        description=f"✅ **{member.display_name}#{member.discriminator} muted successfully.**",
        color=0x00ff05)
    await inter.response.send_message(embed=embed, delete_after=5)
    await asyncio.sleep(tempmute)
    await member.remove_roles(muted_role)


@bot.slash_command(description="Unmute someone from the server.")
@commands.has_permissions(kick_members=True)
async def unmute(inter, member: commands.MemberConverter):
    guild = inter.guild
    mutedRole = disnake.utils.get(guild.roles, id=935417321453944833)
    await member.remove_roles(mutedRole)
    embed = disnake.Embed(
        title=f'Unmuted.',
        description=f'**{member.mention} has been unmuted.**',
        color=0x00ff05)
    await inter.response.send_message(embed=embed)
    await member.send(embed=embed)


@bot.slash_command(description="Purge messages.")
@commands.has_permissions(administrator=True)
async def clear(inter, amount=10):
    channel = inter.message.channel
    await inter.channel.purge(limit=amount + 1)


@bot.slash_command(description="Add roles to someone.")
@commands.has_permissions(administrator=True)
async def ar(inter, member: commands.MemberConverter, role: disnake.Role):
    await member.add_roles(role)
    embed = disnake.Embed(
        title='Role given.',
        description=f'**{member.mention} has been given {role} role.**',
        color=0x00ff05)
    await inter.response.send_message(embed=embed)
    await member.send(embed=embed)


@bot.slash_command(description="Remove roles from someone.")
@commands.has_permissions(administrator=True)
async def rr(inter,
             member: commands.MemberConverter,
             role: disnake.Role,
             *,
             reason=None):
    await member.remove_roles(role)
    embed = disnake.Embed(
        title='Role removed.',
        description=f'**{role} role has been removed from {member.mention}** ',
        color=0xff0000)
    embed.add_field(name='Reason', value=f'{reason}', inline=True)
    await inter.response.send_message(embed=embed)
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
        embed = disnake.Embed(
            title=f'Cool down before I burn you up.',
            description=f'Try the command again in {int(error.retry_after)}s.',
            color=0x000000)
        await ctx.send(embed=embed)
    else:
      raise error


@bot.slash_command(invoke_without_command=True)
async def help(inter):
    embed = disnake.Embed(
        title='Help', description='List of commands available to you, type $help <cmd> for more information.', color=0xFFFF00)
    embed.add_field(name='**Ecomony commands.**',
                    value='beg, work, tsend, wsend, dp, wd, nacc', inline=False)
    embed.add_field(name='**Gambling commands**',
                    value='coinflip', inline=False)
    embed.add_field(name='**Miscellaneous commands**',
                    value='td, suggestion', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def beg(inter):
    embed = disnake.Embed(title='Economic command `$Beg`',
                          description='Beg for money like a loser.', color=0xFFFF00)
    embed.add_field(name='**syntax**', value='`$beg`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def work(inter):
    embed = disnake.Embed(
        title='Economic command `$work`', description='Work and earn money.', color=0xFFFF00)
    embed.add_field(name='**syntax**', value='`$work`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def tsend(inter):
    embed = disnake.Embed(title='Economic command `$tsend`',
                          description='Transfer money from bank to bank.', color=0xFFFF00)
    embed.add_field(name='**syntax**',
                    value='`$tsend <member> [amount]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def wsend(inter):
    embed = disnake.Embed(
        title='Economic command `$wsend`', description='Give money from wallet to wallet.', color=0xFFFF00)
    embed.add_field(name='**syntax**',
                    value='`$wsend <member> [amount]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def dp(inter):
    embed = disnake.Embed(title='Economic command `$dp`',
                          description='Deposit money from wallet to bank account.', color=0xFFFF00)
    embed.add_field(name='**syntax**', value='`$dp [amount]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def wd(inter):
    embed = disnake.Embed(
        title='Economic command `$wd`', description='Withdraw money from bank to wallet.', color=0xFFFF00)
    embed.add_field(name='**syntax**', value='`$wd [amount]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def nacc(inter):
    embed = disnake.Embed(
        title='Economic command `$nacc`', description='Open account.', color=0xFFFF00)
    embed.add_field(name='**syntax**', value='`$nacc`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def coinflip(inter):
    embed = disnake.Embed(title='Gambling command `$coinflip`',
                          description='Flip a coin and bet money on your call.', color=0xFFFF00)
    embed.add_field(name='**syntax**',
                    value='`$coinflip <Heads/Tails> [Money]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def td(inter):
    embed = disnake.Embed(
        title='Miscellaneous command `$td`', description='Play Truth or Dare with your friends!', color=0xFFFF00)
    embed.add_field(name='**syntax**',
                    value='`$td [Player_1] [Player_2] [Player_N]`', inline=False)
    await inter.response.send_message(embed=embed)


@help.slash_command()
async def suggestion(inter):
    embed = disnake.Embed(
        title='Miscellaneous command `$suggestion`', description='Suggest something for the bot or the server.', color=0xFFFF00)
    embed.add_field(name='**syntax**',
                    value='`$suggestion [suggestion]`', inline=False)
    await inter.response.send_message(embed=embed)


@bot.slash_command(description="Add suggestions for the bot and the server.")
async def suggestion(inter, *, suggest):
    cursor.execute("INSERT OR IGNORE INTO suggestions VALUES(?,?,?);",
                   (str(inter.author.name), str(suggest), int(inter.message.id)))
    db.commit()
    embed = disnake.Embed(title='Suggestion added.',
                          description=f'**{suggest}**', color=disnake.Color.green())
    embed.set_author(name=f'{inter.author.name}')
    await inter.response.send_message(embed=embed)


@bot.slash_command(description="Check for suggestions.")
@commands.has_permissions(kick_members=True)
async def check_suggestions(inter):
    chk = cursor.execute("SELECT * FROM suggestions")
    db.commit()
    chk = cursor.fetchall()
    for i in chk:
        await inter.response.send_message(f'{str(i)}')


@bot.slash_command(description="Remove suggestions.")
@commands.has_permissions(kick_members=True)
async def rem_suggestions(inter, msg_id: int):
    cursor.execute(f"DELETE FROM suggestions WHERE msg_id = {msg_id}")
    db.commit()
    await inter.response.send_message("Suggestion Removed.")


@bot.slash_command(description="Commands for mods.")
@commands.has_permissions(kick_members=True)
async def HelpMod(inter):
    member = disnake.Member
    embed = disnake.Embed(
        title="Help",
        description="These are the commands available for use for mods at the moment.",
        color=0x000000)
    embed.set_author(name="Sweggist")
    embed.add_field(name="clear",
                    value="Clears messages for you.",
                    inline=False)
    embed.add_field(name="kick",
                    value="Kicks the offender for you.",
                    inline=False)
    embed.add_field(name="ban",
                    value="Bans the offender for you.",
                    inline=False)
    embed.add_field(name="unban",
                    value="Unbans the pity soul for you.",
                    inline=False)
    embed.add_field(name="mute", value="Shut them up.", inline=False)
    embed.add_field(name="tmute",
                    value="Shut them up, Temporarily.",
                    inline=False)
    embed.add_field(name="unmute",
                    value="Unmute the person you so mercilessly muted.",
                    inline=False)
    embed.add_field(
        name="ar",
        value="Add a new role to someone. It better be a promotion :D",
        inline=False)
    embed.add_field(
        name="rr",
        value="remove roles from power abusers. Great powers comes with great responsibilities ;)",
        inline=False)
    await inter.response.send_message(f'{inter.author.mention} check your DMs!')
    await member.send(embed=embed)


@bot.slash_command(description="Add items to the shop.")
@commands.has_permissions(kick_members=True)
async def add_item(inter, itemid, quantity: int, amount: int):
    cursor.execute("INSERT OR IGNORE INTO shop_items VALUES(?,?,?)",
                   (itemid, quantity, amount))
    db.commit()
    await inter.response.send_message(f"Emoji {itemid} added in quantity {quantity} for {amount}:coin: coins.")


@bot.slash_command(description="Check items in the shop.")
@commands.has_permissions(kick_members=True)
async def check_items(inter):
    cursor.execute("SELECT * FROM shop_items")
    res = cursor.fetchall()
    for i in res:
        await inter.response.send_message(f'{i}')

@bot.slash_command(description="Buy something from the shop.")
async def buy(ctx):
    pass

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client.run()