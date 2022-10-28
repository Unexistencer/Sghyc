from discord.ext import commands
from discord import ActionRow, Button, ButtonStyle
import os
import discord
import random
import asyncio
import datetime
import bank

from numpy import true_divide
# from server import keep_alive

TOKEN_main = os.getenv('discord_TOKEN_main')
TOKEN_sub = os.getenv('discord_TOKEN_sub')

bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=discord.Intents.all())

# bot_ID = 991200202855813262
list = ['.choose A B C ...',
        '.cock',
        '.arena',
        '.counter on/off and type some "屌你老母"',
        '.bank']
counter = 0
chooseCount = 0


@bot.event
async def on_ready():
    print('Project starts.')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    global counter
    global chooseCount

    if message.content == ('.counter on'):
        counter = 1
        embed = discord.Embed(title='Counter mode has been enabled')
        await message.channel.send(embed=embed)

    if message.content == ('.counter off'):
        counter = 0
        embed = discord.Embed(title='Counter mode has been disabled')
        await message.channel.send(embed=embed)

    if message.content.startswith('.choose '):
        chooseCount = plus(chooseCount)
        print("["+str(datetime.datetime.now())+"]Choose Used: " + str(chooseCount) + " from ["+message.guild.name+"]")
        await choose(message)
        return

    if message.content == ('.cock'):
        await cock(message)
        return

    if message.content == '.arena':
        await arena(message)
        return

    if counter == 1 and '屌你老母' in str(message.content):
        await noplz(message)
        return

    if counter == 1 and '抵' in str(message.content):
        await lmao(message)
        return

    if message.content == ('.?'):
        await what(message)
        return

    if message.content == ('.bank'):
        await bank.balance(message)
        return

def plus(num):
    return (num + 1)

# ?
async def what(message):
    description = ""
    for i in list:
        description += i + "\n"
    embed = discord.Embed(title='Commands',
                          description=description +
                          '\nupdate when have time/idea')
    await message.channel.send(embed=embed)


# noplz
async def noplz(message):
    pattern = ['唔好啦', '屌番你老母', '笑死', '睇吓點', '吓...', '8D都仲好意思屌我老母']
    await message.channel.send(''.join(random.choice(pattern)))


# lmao
async def lmao(message):
    pattern = ['你都抵', '抵', '唔抵']
    await message.channel.send(''.join(random.choice(pattern)))


# choose
async def choose(message):
    arr = message.content.split()
    arr.pop(0)
    if len(arr) <= 1:
        embed = discord.Embed(title='點揀呀',
                              description='下次比夠2個以上選擇我先好叫我揀',
                              color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        num = random.randint(0, len(arr) - 1)
        result = str(arr[num])
        if len(result) > 1 and random.randint(1, 100) == 100:
            word = arr[random.randint(0, len(arr) - 1)]
            prefix = str(word)[0:int(len(str(word))/2)]
            arr.remove(word)
            word = arr[random.randint(0, len(arr) - 1)]
            suffix = str(word)[int(len(str(word))/2):int(len(str(word)))]
            embed = discord.Embed(title='「' + prefix+suffix + '」',
                                  description='嗱幫你揀咗喇，唔好反口呀。',
                                  color=discord.Color.green())
            await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            embed = discord.Embed(title='「' + result + '」',
                                  description='講吓姐，幫你揀左喇。',
                                  color=discord.Color.green())
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title='「' + result + '」',
                                  description='嗱幫你揀咗喇，唔好反口呀。',
                                  color=discord.Color.green())
            await message.channel.send(embed=embed)


# Cock
async def cock(message: commands.Context):
    components = [ActionRow(Button(label='Normal',
                                   custom_id='normal',
                                   style=ButtonStyle.green),
                            Button(label='Hard',
                                   custom_id='hard',
                                   style=ButtonStyle.red))
                  ]
    embed = discord.Embed(description='Choose your cock...', color=discord.Color.random())
    msg = await message.channel.send(embed=embed, components=components)
    guild = message.guild
    user = message.author

    def _check(i: discord.Interaction, b):
        return i.message == msg and i.member == message.author

    interaction, button = await bot.wait_for('button_click', check=_check)
    button_id = button.custom_id

    await interaction.defer()
    if button_id == "normal":
        await interaction.edit(embed=embed.add_field(name='Your cock size',
                                                     value="\n8" + ("=" * random.randint(0, 20)) + "D"),
                                                     components=[])
        return

    if button_id == "hard":
        cock = 0
        count = random.randint(0, 1)
        while count != 0:
            cock += 1
            count = random.randint(0, 1)
        if cock >= 4:
            await bank.earn(guild, user, cock/4)
            await interaction.edit(embed=embed.add_field(name='Your cock size (Hard Mode)',
                                                     value="\n8" + ("=" * cock) + "D\nYou got a Sing Coin!"),
                                                     components=[])
            return
        await interaction.edit(embed=embed.add_field(name='Your cock size (Hard Mode)',
                                                     value="\n8" + ("=" * cock) + "D"),
                                                     components=[])
        return


# Arena
async def arena(message):
    guild = message.guild
    arenaID = []
    arenaID.append(message.author.id)

    embed = discord.Embed(title=message.author.name + '發起了Cock Arena!!',
                          description='參賽報名請於20秒內點擊下方的✅',
                          color=discord.Color.red())
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction('✅')

    await asyncio.sleep(3)

    getmsg = await message.channel.fetch_message(msg.id)

    async for user in getmsg.reactions[0].users():
        if user.id != bot.user.id and user.id != message.author.id:
            arenaID.append(user.id)

    print('done')

    if len(arenaID) <= 1:
        embed = discord.Embed(title="沒有人想跟你比拼...",
                              description="下次記得約齊人",
                              color=discord.Color.greyple())
    else:
        description = ""
        leng = [0]*len(arenaID)
        winner = []
        loser = []

        for x in arenaID:
            description += f"\n\n**{arenaID.index(x) + 1}.** <@{x}>"
            # leng[arenaID.index(x)] = 3
            leng[arenaID.index(x)] = random.randint(0, 40)
            description += "\n8" + ("=" * leng[arenaID.index(x)]) + "D"
        
        description += "\n\n"
        for i in range(len(leng)):
            if leng[i] == max(leng):
                winner.append(arenaID[i])
        for user in winner:
            await bank.earn(guild, user, 1)
            description += f"<@{user}> "
        description += "\n嬴取一枚成Coin!"
    
        if max(leng) != min(leng):
            description += "\n\n"
            for i in range(len(leng)):
                if leng[i] == min(leng):
                    loser.append(arenaID[i])
            for user in loser:
                await bank.pay(guild, user, 1)
                description += f"<@{user}> "
            description += "\n失去一枚成Coin!"

        embed = discord.Embed(title="==========Cock Arena==========",
                                description=description,
                                color=discord.Color.greyple())

    await message.channel.send(embed=embed)





bot.run(TOKEN_main)

# keep_alive()
# try:
#     bot.run(TOKEN)
# except:
#     os.system("kill 1")