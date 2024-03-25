# ============================================================
# 230105 bug fixed: cock hard mode挑戰成功時獲得成coin數量表示錯誤(cock % 4 -> cock // 4)
# 230110 調整成coin表示方式
# 230315 開始新增music
# 230502 bank.json格式修改, 新增查看Ranking功能
# 230612 新增logging
# 240215 logging -> logger
# 240319 新增偷聽checker
#
# ============================================================

from discord.ext import commands
from discord import ActionRow, Button, ButtonStyle
import os
import discord
import random
import asyncio
import bank
import time
# from num2chinese import num2chinese
# import music
import json
import sys
import logging
from logging.handlers import RotatingFileHandler
import re
import online_check

config_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "config.json")
announce_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "announce_channel.json")

class joinVC:
    def __init__(self, userID, befChannel, aftChannel, diffTime):
        self.userID = userID
        self.befchannel = befChannel
        self.aftChannel = aftChannel
        self.diffTime = diffTime

if not os.path.isfile(config_path):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(config_path) as file:
        config = json.load(file)

if not os.path.isfile(announce_path):
    sys.exit("'announce_channel.json' not found! Please add it and try again.")
else:
    with open(announce_path) as file:
        announce = json.load(file)

def get_next_log_filename(log_dir):
    # get all files starts with 'log-'
    log_files = [f for f in os.listdir(log_dir) if f.startswith('log-')]
    
    # if none, create 'log-1.log'
    if not log_files:
        return os.path.join(log_dir, 'log-1.log')
    
    # if exist, find the latest one (which is largest num)
    latest_log_num = max([int(re.search(r'log-(\d+)\.log', f).group(1)) for f in log_files])
    latest_log_file = os.path.join(log_dir, f"log-{latest_log_num}.log")

    # check file size, create a new one if the latest file's size is over 1mb
    if os.path.getsize(latest_log_file) >= 1 * 1024 * 1024:
        return os.path.join(log_dir, f"log-{latest_log_num + 1}.log")
    else:
        return latest_log_file


def setup_logging():
    # set log file
    log_dir = '.'
    log_filename = get_next_log_filename(log_dir)
    
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # create RotatingFileHandler, with the size limit of 1mb
    handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # add handler to logger
    logger.addHandler(handler)
    
    return logger

if __name__ == "__main__":
    logger = setup_logging()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)

command_list = ['.choose A B C ...',
        '.cock',
        '.arena',
        '.counter on/off and type some "屌你老母"',
        '.info',
        '.ranking',
        '.ran',
        '.rran',
        '.sran']
counter = 0
token = config.get('token_main') if config.get('safemode') == 0 else config.get('token_sub')

joinVC_list = []

# os.chdir('/home/lab-rat/Documents/bot')
os.chdir(f"{os.path.realpath(os.path.dirname(__file__))}")

time.sleep(10)

@bot.event
async def on_ready():
    logger.info('Bot started')
    print('Project starts.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    global counter

    words = message.content.split()
    if isinstance(words, list):
        command = words[0]
        command = command[1:]
    else:
        command = words[1:]

    if message.content == ('.counter on'):
        counter = 1
        embed = discord.Embed(title='Counter mode has been enabled')
        await message.channel.send(embed=embed)

    if message.content == ('.counter off'):
        counter = 0
        embed = discord.Embed(title='Counter mode has been disabled')
        await message.channel.send(embed=embed)
    
    if message.content == ('.announce'):
        await log(message, command)
        set_check = await online_check.set_announce_channel(message.guild, message.channel)
        if (set_check):
            embed = discord.Embed(title='Set as announcement channel.')
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title='Announcement channel setup error.')
            await message.channel.send(embed=embed)
        return
    
    if message.content == ('.?'):
        await log(message, command)
        await what(message)
        return
    
    if message.content.startswith('.choose'):
        await log(message, command)
        await choose(message)
        return 

    if message.content == ('.cock'):
        await log(message, command)
        await cock(message)
        logger.info('Success')
        return

    if message.content == '.arena':
        await log(message, command)
        await arena(message)
        logger.info('Success')
        return

    if counter == 1 and '屌你老母' in str(message.content):
        await noplz(message)
        return

    if counter == 1 and '抵' in str(message.content):
        await lmao(message)
        return

    if message.content == ('.info'):
        await log(message, command)
        await choose_info(message)
        logger.info('Success')
        return
    
    if message.content.startswith('.dice'):
        await log(message, command)
        await dice(message)
        logger.info('Success')
        return
    
    if message.content == ('.ranking'):
        await log(message, command)
        # await bank.ranking_check(message)
        await ranking(message)
        logger.info('Success')
        return

    if message.content.startswith('.move '):
        await log(message, command)
        if message.author.id in config['owners']:
            await move(message)
            logger.info('Success')
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return
    
    if message.content.startswith('.give '):
        await log(message, command)
        if message.author.id in config['owners']:
            await give(message)
            logger.info('Success')
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return
    
    if message.content.startswith('.take '):
        await log(message, command)
        if message.author.id in config['owners']:
            await take(message)
            logger.info('Success')
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return
    
    if message.content == ('.ran'):
        if message.reference is not None:
            await ran(message.reference.resolved)
        else:
            msg = await message.channel.history(limit=100).flatten()
            for m in msg:
                if m.author == bot.user or m.content.startswith('.'):
                    continue
                else:
                    filtered = m
                    break
            await ran(filtered)
        return
    
    if message.content == ('.rran'):
        if message.reference is not None:
            await rran(message.reference.resolved)
        else:
            msg = await message.channel.history(limit=100).flatten()
            for m in msg:
                if m.author == bot.user or m.content.startswith('.'):
                    continue
                else:
                    filtered = m
                    break
            await rran(filtered)
        return
    
    if message.content == ('.sran'):
        if message.reference is not None:
            await sran(message.reference.resolved)
        else:
            msg = await message.channel.history(limit=100).flatten()
            for m in msg:
                if m.author == bot.user or m.content.startswith('.'):
                    continue
                else:
                    filtered = m
                    break
            await sran(filtered)
        return

    if message.content.startswith('.set '):
        await log(message, command)
        if message.author.id in config['owners']:
            await set(message)
            logger.info('Success')
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return

    if message.content == ('.change'):
        await log(message, command)
        if message.author.id in config['owners']:
            await season_change(message)
            embed = discord.Embed(title='Season Changed')
            await message.channel.send(embed=embed)
            logger.info('Success')
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return
    
    if message.content == ('.safemode'):
        if message.author.id in config['owners']:
            embed = discord.Embed(title='Enabling safe mode...')
            await message.channel.send(embed=embed)
            config['safemode'] = 1
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            await restart_bot()
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return
    
    if message.content == ('.return'):
        if message.author.id in config['owners']:
            await log(message, command)
            embed = discord.Embed(title='Disabling safe mode...')
            await message.channel.send(embed=embed)
            config['safemode'] = 0
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            await restart_bot()
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return

    if message.content == ('.sudo reboot'):
        if message.author.id in config['owners']:
            await log(message, 'Reboot')
            embed = discord.Embed(title='Rebooting bot...')
            await message.channel.send(embed=embed)
            await restart_bot()
        else:
            embed = discord.Embed(title='？')
            await message.channel.send(embed=embed)
        return


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel == after.channel:
        return False
    joinVC_list.append(joinVC(member.id, before.channel, after.channel, time.time()))
    
    for i, o in enumerate(joinVC_list):
        if o.userID == member.id:
            elapsed_time = time.time() - o.diffTime
            if before.channel and after.channel:
                if elapsed_time > 10 or o.aftChannel != before.channel:
                    del joinVC_list[i]
                else:
                    if str(member.guild.id) in announce:
                        announce_channel = announce[str(member.guild.id)]['channel_id']
                        channel = bot.get_channel(announce_channel)
                        await channel.send(member.name+"入"+ before.channel.name+"偷聽完又走")
                    for i, o in enumerate(joinVC_list):
                        if o.aftChannel != after.channel:
                            del joinVC_list[i]
            elif not after.channel:
                if o.aftChannel:
                    if elapsed_time < 10:
                        if str(member.guild.id) in announce:
                            if before.channel == after.channel:
                                return False
                            announce_channel = announce[str(member.guild.id)]['channel_id']
                            channel = bot.get_channel(announce_channel)
                            await channel.send(member.name+"入"+ before.channel.name+"偷聽完又走")
                    for i, o in enumerate(joinVC_list):
                        if o.userID == member.id:
                            del joinVC_list[i]
            else:
                return
    
    return
    
def plus(num):
    return (num + 1)

# ?
async def what(message):
    description = ""
    for i in command_list:
        description += i + "\n"
    embed = discord.Embed(title='Commands',
                          description=description +
                          '\nupdate when have time/idea')
    await message.channel.send(embed=embed)
    return


# noplz
async def noplz(message):
    pattern = ['唔好啦', '屌番你老母', '笑死', '睇吓點', '吓...', '8D都仲好意思屌我老母']
    await message.channel.send(''.join(random.choice(pattern)))
    return


# lmao
async def lmao(message):
    pattern = ['你都抵', '抵', '唔抵']
    await message.channel.send(''.join(random.choice(pattern)))
    return


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
            logger.info("Critical Attack!!")
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
        logger.info('Success')
        return


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
            coin = cock//4 * 50
            if coin >= 100:
                silver = coin // 100
                bronze = coin - (silver * 100)
                value = "\n8" + ("=" * cock) + "D\nYou got {:d}<:shingcoin_2:952962920940200026> ".format(silver)
                if bronze != 0:
                    value += "{:d}<:shingcoin_3:952963842248421466>".format(bronze)
                value += "！"
            else:
                value = "\n8" + ("=" * cock) + "D\nYou got {:d}<:shingcoin_3:952963842248421466>！".format(coin)
            await bank.earn(guild, user, coin)
            await interaction.edit(embed=embed.add_field(name='Your cock size (Hard Mode)',
                                                     value=value),
                                                     components=[])
            return
        await interaction.edit(embed=embed.add_field(name='Your cock size (Hard Mode)',
                                                     value="\n8" + ("=" * cock) + "D"),
                                                     components=[])
        return




# Dice
    
async def dice(message: commands.Context):
    msg = message.content[6:]
    msg.replace('+', ' ').replace('D','d')
    dice = msg.split(' ')
    # WIP



# Random
async def ran(message):
    msg = message.content
    eng = ''
    ran_msg = ''
    newline = findOccurrences(msg, '\n')
    msg = msg.replace('\n', '')
    lst = []
    for letter in msg:
        if isEnglish(letter):
            eng+=letter
        else:
            if eng != '':
                lst.append(eng)
                eng = ''
            lst.append(letter)
    if eng != '':
        lst.append(eng)
        eng = ''        
    
    if len(lst) == 1:
        text = list(lst[0])
        random.shuffle(text)
        for t in text:
            ran_msg += t
    else:
        random.shuffle(lst)
        for t in lst:
            ran_msg += t
        for n in newline:
            ran_msg = ran_msg[:n]+ '\n' + ran_msg[n:]

    embed = discord.Embed(title='Random',
                                  description=ran_msg,
                                  color=discord.Color.green())
    await message.channel.send(embed=embed)


# Rran
    
async def rran(message):
    msg = message.content
    ran_msg = ''
    newline = findOccurrences(msg, '\n')

    rot = random.randint(1, len(msg)-1)
    ran_msg = (msg * 3)[len(msg) + rot : 2 * len(msg) + rot]
    if random.randint(0, 1):
        ran_msg = ran_msg[::-1]
    ran_msg = ran_msg.replace('\n', '')
    for n in newline:
        ran_msg = ran_msg[:n]+ '\n' + ran_msg[n:]


    embed = discord.Embed(title='R-Random',
                                  description=ran_msg,
                                  color=discord.Color.green())
    await message.channel.send(embed=embed)


# Sran
async def sran(message):
    msg = message.content
    eng = ''
    ran_msg = ''
    newline = findOccurrences(msg, '\n')
    msg = msg.replace('\n', '')
    lst = []
    for letter in msg:
        if isEnglish(letter):
            eng+=letter
        else:
            if eng != '':
                lst.append(eng)
                eng = ''
            lst.append(letter)
    if eng != '':
        if eng[-1] != ' ':
            eng += ' '
        lst.append(eng)
        eng = ''        
    
    if len(lst) == 1:
        text = list(lst[0])
        count = 0
        while count < len(text):
            num = random.randint(0, len(text)-1)
            ran_msg += text[num]
            count += 1
    else:
        count = 0
        while count < len(lst):
            num = random.randint(0, len(lst)-1)
            ran_msg += lst[num]
            count += 1
        for n in newline:
            ran_msg = ran_msg[:n]+ '\n' + ran_msg[n:]

    embed = discord.Embed(title='S-Random',
                                  description=ran_msg,
                                  color=discord.Color.green())
    await message.channel.send(embed=embed)
    

    
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

# Choose info

async def choose_info(message: commands.Context):
    components = [ActionRow(Button(label='本月成績',
                                   custom_id='monthly',
                                   style=ButtonStyle.gray),
                            Button(label='總成績',
                                   custom_id='total',
                                   style=ButtonStyle.gray)
                            )
                  ]
    embed = discord.Embed(description='Info', color=discord.Color.random())
    msg = await message.channel.send(embed=embed, components=components)

    def _check(i: discord.Interaction, b):
        return i.message == msg and i.member == message.author

    interaction, button = await bot.wait_for('button_click', check=_check)
    button_id = button.custom_id

    await interaction.defer()
    if button_id == "monthly":
        embed = await bank.info_season(message)
        await interaction.edit(embed=embed, components=[])
        return

    if button_id == "total":
        embed = await bank.info_total(message)
        await interaction.edit(embed=embed, components=[])
        return

# Ranking

async def ranking(message: commands.Context):
    components = [ActionRow(Button(label='本月成Coin',
                                   custom_id='wallet',
                                   style=ButtonStyle.gray),
                            Button(label='本月勝數',
                                   custom_id='win_count',
                                   style=ButtonStyle.gray),
                            Button(label='本月勝率',
                                   custom_id='ratio',
                                   style=ButtonStyle.gray),
                            Button(label='本月8D',
                                   custom_id='8D_count',
                                   style=ButtonStyle.gray)),
                    ActionRow(Button(label='總合成Coin',
                                   custom_id='total_wallet',
                                   style=ButtonStyle.gray),
                            Button(label='總合勝數',
                                   custom_id='total_win_count',
                                   style=ButtonStyle.gray),
                            Button(label='總合勝率',
                                   custom_id='total_ratio',
                                   style=ButtonStyle.gray),
                            Button(label='總合8D',
                                   custom_id='total_8D_count',
                                   style=ButtonStyle.gray))
                  ]
    embed = discord.Embed(description='Ranking List', color=discord.Color.random())
    msg = await message.channel.send(embed=embed, components=components)

    def _check(i: discord.Interaction, b):
        return i.message == msg and i.member == message.author

    interaction, button = await bot.wait_for('button_click', check=_check)
    button_id = button.custom_id
    label_id = button.label

    await interaction.defer()
    await msg.delete()
    await bank.ranking(message, button_id, label_id)
    return
    





# Arena
async def arena(message):
    guild = message.guild
    arenaID = []
    arenaID.append(message.author.id)

    bet = random.randint(1, 20) * 5
    if bet == 100:
        embed = discord.Embed(title=message.author.name + '發起了Cock Arena!!',
                            description='本次賭注為'+str(bet//100)+'枚<:shingcoin_2:952962920940200026>！\n'+'參賽報名請於20秒內點擊下方的✅',
                            color=discord.Color.red())
    else:
        embed = discord.Embed(title=message.author.name + '發起了Cock Arena!!',
                            description='本次賭注為'+str(bet)+'枚<:shingcoin_3:952963842248421466>！\n'+'參賽報名請於20秒內點擊下方的✅',
                            color=discord.Color.red())
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction('✅')

    await asyncio.sleep(20)

    getmsg = await message.channel.fetch_message(msg.id)

    async for user in getmsg.reactions[0].users():
        if user.id != bot.user.id and user.id != message.author.id:
            arenaID.append(user.id)
            await bank.entry(guild, user.id, 'total_arena_playcount')

    # print('done')

    if len(arenaID) <= 1:
        embed = discord.Embed(title="沒有人想跟你比拼...",
                              description="下次記得約齊人",
                              color=discord.Color.greyple())
    else:
        await bank.entry(guild, message.author.id, 'total_arena_playcount')
        description = ""
        leng = [0]*len(arenaID)
        winner = []
        loser = []

        for x in arenaID:
            description += f"\n\n**{arenaID.index(x) + 1}.** <@{x}>"
            # leng[arenaID.index(x)] = 3
            leng[arenaID.index(x)] = random.randint(0, 40)
            description += "\n8" + ("=" * leng[arenaID.index(x)]) + "D"
            if leng[arenaID.index(x)] == 0:
                await bank.entry(guild, x, "total_8D_count")
        
        for i in range(len(leng)):
            if leng[i] == max(leng):
                winner.append(arenaID[i])
        if max(leng) != min(leng):
            for i in range(len(leng)):
                if leng[i] == min(leng):
                    loser.append(arenaID[i])

        description += "\n\n"
        prize = (len(loser) * bet // len(winner)) + (len(loser) * bet % len(winner))
        for user in winner:
            await bank.earn(guild, user, prize)
            await bank.entry(guild, user, "total_win_count")
            description += f"<@{user}> "
        if prize >= 10000:
            gold = prize // 10000
            silver = (prize - gold * 10000) // 100
            bronze = prize - gold * 10000 - silver * 100
            description += "\n嬴取了"
            description += "{:d}<:shingcoin_1:952960803663937577> ".format(gold)
            if silver != 0:
                description += "{:d}<:shingcoin_2:952962920940200026> ".format(silver)
            if bronze != 0:
                description += "{:d}<:shingcoin_3:952963842248421466>".format(bronze)
            description += "！"
        elif prize >= 100 and prize < 10000:
            silver = prize//100
            bronze = prize - silver*100
            description += "\n嬴取了"
            description += "{:d}<:shingcoin_2:952962920940200026> ".format(silver)
            if bronze != 0:
                description += "{:d}<:shingcoin_3:952963842248421466>".format(bronze)
            description += "！"
        else:
            description = description + "\n嬴取了"
            description = description + "{:d}<:shingcoin_3:952963842248421466>！".format(prize)

        if max(leng) != min(leng):
            description += "\n\n"
            for user in loser:
                await bank.pay(guild, user, bet)
                description += f"<@{user}> "
            if bet >= 10000:
                gold = bet // 10000
                silver = (bet - gold * 10000) // 100
                bronze = bet - gold * 10000 - silver * 100
                description += "\n失去了"
                description += "{:d}<:shingcoin_1:952960803663937577> ".format(gold)
                if silver != 0:
                    description += "{:d}<:shingcoin_2:952962920940200026> ".format(silver)
                if bronze != 0:
                    description += "{:d}<:shingcoin_3:952963842248421466>".format(bronze)
                description += "！"
            elif prize >= 100 and prize < 10000:
                silver = bet // 100
                bronze = bet - silver * 100
                description += "\n失去了"
                description += "{:d}<:shingcoin_2:952962920940200026> ".format(silver)
                if bronze != 0:
                    description += "{:d}<:shingcoin_3:952963842248421466>".format(bronze)
                description += "！"
            else:
                description += "\n失去了"
                description += "{:d}<:shingcoin_3:952963842248421466>！".format(bet)

        embed = discord.Embed(title="==========Cock Arena==========",
                                description=description,
                                color=discord.Color.greyple())

    await message.channel.send(embed=embed)




# seaon change

async def season_change(message):
    guild = message.guild
    with open('bank.json', 'r') as f:
        bank = json.load(f)
    for user in bank[str(guild.id)]:
        user['total_wallet'] += user['wallet']
        user['wallet'] = 0
        user['arena_playcount'] = 0
        user['win_count'] = 0
        user['8D_count'] = 0

    with open('bank.json', 'w') as f:
        json.dump(bank, f, indent=4)
        return
    
@bot.command()
@commands.guild_only()
async def move(message):
    guild = message.guild
    arr = message.content.split()
    arr[1] = arr[1].replace('<@', '')
    arr[1] = arr[1].replace('>', '')
    arr[2] = arr[2].replace('<#', '')
    arr[2] = arr[2].replace('>', '')
    print(arr)
    try:
        member = guild.get_member(int(arr[1]))
        channel = bot.get_channel(int(arr[2]))
    except:
        embed = discord.Embed(title='？')
        await message.channel.send(embed=embed)
        return
    
    await member.move_to(channel)

    description = "Moved "
    description += f"<@{int(arr[1])}>"
    description += " to "
    description += f"<#{int(arr[2])}>"
    embed = discord.Embed(title="==========Move==========",
                                    description=description,
                                    color=discord.Color.greyple())
    await message.channel.send(embed=embed)

async def give(message):
    guild = message.guild
    arr = message.content.split()
    arr[1] = arr[1].replace('<@', '')
    arr[1] = arr[1].replace('>', '')
    # print(arr)
    try:
        user = int(arr[1])
        amount = int(arr[2])
    except:
        embed = discord.Embed(title='？')
        await message.channel.send(embed=embed)
        return
    await bank.earn(guild, user, amount)
    gold = amount//10000
    silver = (amount-gold*10000)//100
    bronze = amount-gold*10000-silver*100
    description = f"<@{user}> "
    description += "獲得"
    if gold != 0:
        description += str(gold) + "<:shingcoin_1:952960803663937577> "
    if silver != 0:
        description += str(silver) + "<:shingcoin_2:952962920940200026> "
    if bronze != 0:
        description += str(bronze) + "<:shingcoin_3:952963842248421466>"
    embed = discord.Embed(description=description,
                          color=discord.Color.greyple())
    await message.channel.send(embed=embed)

async def take(message):
    guild = message.guild
    arr = message.content.split()
    arr[1] = arr[1].replace('<@', '')
    arr[1] = arr[1].replace('>', '')
    # print(arr)
    try:
        user = int(arr[1])
        amount = int(arr[2])
    except:
        embed = discord.Embed(title='？')
        await message.channel.send(embed=embed)
        return
    await bank.pay(guild, user, amount)
    gold = amount//10000
    silver = (amount-gold*10000)//100
    bronze = amount-gold*10000-silver*100
    description = f"<@{user}> "
    description += "失去"
    if gold != 0:
        description += str(gold) + "<:shingcoin_1:952960803663937577> "
    if silver != 0:
        description += str(silver) + "<:shingcoin_2:952962920940200026> "
    if bronze != 0:
        description += str(bronze) + "<:shingcoin_3:952963842248421466>"
    embed = discord.Embed(description=description,
                          color=discord.Color.greyple())
    await message.channel.send(embed=embed)

async def set(message):
    guild = message.guild
    arr = message.content.split()
    arr[1] = arr[1].replace('<@', '')
    arr[1] = arr[1].replace('>', '')
    # print(arr)
    try:
        user = int(arr[1])
        amount = int(arr[2])
    except:
        embed = discord.Embed(title='？')
        await message.channel.send(embed=embed)
        return
    await bank.set(guild, user, amount)
    gold = amount//10000
    silver = (amount-gold*10000)//100
    bronze = amount-gold*10000-silver*100
    description = f"<@{user}> "
    description += "現擁有" + str(gold) + "<:shingcoin_1:952960803663937577> " + str(silver) + "<:shingcoin_2:952962920940200026> " + str(bronze) + "<:shingcoin_3:952963842248421466>！"
    embed = discord.Embed(title="==========Set==========",
                                    description=description,
                                    color=discord.Color.greyple())
    await message.channel.send(embed=embed)

async def log(message, fc):
    logger.info(fc+ " by " + str(message.author) + " from [" + message.guild.name + "#" + str(message.guild.id) + "]")
    return

async def sucess():
    logger.info('Success')
    return
async def failed():
    logger.info('Failed')
    return

def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

result = None
while result is None:
    try:
        # connect
        result = bot.run(token)
    except:
        pass