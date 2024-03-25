import os
import json
import discord

bank_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "bank.json")

# get bank data
async def get_bank_data():
    with open(bank_path, 'r') as f:
        bank = json.load(f)
    return bank


# info

async def info_season(message):
    guild_id = message.guild.id
    # print(message.guild)
    # print(message.guild.id)
    user_id = message.author.id
    await create_account(message.guild, user_id)
    
    bank = await get_bank_data()
    for user in bank[str(guild_id)]:
        if user['ID'] == user_id:
            season_wallet = user['wallet']
            arena_playcount = user['arena_playcount']
            win_count = user['win_count']
            eightD_count = user['8D_count']
            break
    
    season_gold = season_wallet//10000
    season_silver = (season_wallet-season_gold*10000)//100
    season_bronze = season_wallet-season_gold*10000-season_silver*100

    value_season_wallet = ""
    if season_wallet > 0:
        if season_gold != 0:
            value_season_wallet += str(season_gold) + "<:shingcoin_1:952960803663937577> "
        if season_silver != 0:
            value_season_wallet += str(season_silver) + "<:shingcoin_2:952962920940200026> "
        if season_bronze != 0:
            value_season_wallet += str(season_bronze) + "<:shingcoin_3:952963842248421466>"
    else:
        value_season_wallet = "<:hand_r2:971325523471003668>"

    embed = discord.Embed(title="本月成績")
    embed.add_field(name = "成Coin結餘", value = value_season_wallet)
    embed.add_field(name = "Arena參與次數", value = arena_playcount)
    if arena_playcount >0:
        ratio = round(float(win_count)/arena_playcount*100, 2)
        embed.add_field(name = "Arena勝率", value = str(ratio) + "%")
    embed.add_field(name = "8D次數", value = eightD_count)
    return embed


# info_total

async def info_total(message):
    guild_id = message.guild.id
    user_id = message.author.id
    await create_account(message.guild, user_id)
    
    bank = await get_bank_data()
    for user in bank[str(guild_id)]:
        if user['ID'] == user_id:
            wallet = user['total_wallet']+user['wallet']
            total_arena_playcount = user['total_arena_playcount']
            total_win_count = user['total_win_count']
            total_eightD_count = user['total_8D_count']
            break
    
    gold = wallet//10000
    silver = (wallet-gold*10000)//100
    bronze = wallet-gold*10000-silver*100

    value_wallet = ""
    if wallet > 0:
        if gold != 0:
            value_wallet += str(gold) + "<:shingcoin_1:952960803663937577> "
        if silver != 0:
            value_wallet += str(silver) + "<:shingcoin_2:952962920940200026> "
        if bronze != 0:
            value_wallet += str(bronze) + "<:shingcoin_3:952963842248421466>"
    else:
        value_wallet = "<:hand_r2:971325523471003668>"

    embed = discord.Embed(title= "總成績")
    embed.add_field(name = "成Coin結餘", value = value_wallet)
    embed.add_field(name = "Arena參與次數", value = total_arena_playcount)
    if total_arena_playcount >0:
        ratio = round(float(total_win_count)/total_arena_playcount*100, 2)
        embed.add_field(name = "Arena勝率", value = str(ratio) + "%")
    embed.add_field(name = "8D次數", value = total_eightD_count)
    return embed



#create account

async def create_account(guild, user_id):
    bank = await get_bank_data()
    # print(guild.id)
    
    if type(user_id) is discord.member.Member:
        if str(guild.id) in bank:
            for search in bank[str(guild.id)]:
                if search['ID'] == user_id.id:
                    return False
            bank[str(guild.id)].append({
                "ID": user_id.id,
                "wallet": 0,
                "arena_playcount": 0,
                "win_count": 0,
                "8D_count": 0,
                "total_wallet": 0,
                "total_arena_playcount": 0,
                "total_win_count": 0,
                "total_8D_count": 0
                })
            
    if type(user_id) is int:
        if str(guild.id) in bank:
            for search in bank[str(guild.id)]:
                if search['ID'] == user_id:
                    return False
            bank[str(guild.id)].append({
                "ID": user_id,
                "wallet": 0,
                "arena_playcount": 0,
                "win_count": 0,
                "8D_count": 0,
                "total_wallet": 0,
                "total_arena_playcount": 0,
                "total_win_count": 0,
                "total_8D_count": 0
                })

    with open(bank_path, 'w') as f:
        json.dump(bank, f, indent=4)
        return

async def ranking_check(message):
    guild = message.guild
    with open(bank_path, 'r') as f:
        bank = json.load(f)
    
    ranking = []
    gold = [None] * 3
    silver = [None] * 3
    bronze = [None] * 3

    for i in range(3):
        wallet_amount = -1
        for user in bank[str(guild.id)]:
            wallet = user['total_wallet'] + user['wallet']
            if wallet > wallet_amount:
                richman = user
                wallet_amount = wallet
        ranking.append(richman['ID'])
        bank[str(guild.id)].remove(richman)
        # print(bank[str(guild.id)])
        gold[i] = wallet_amount//10000
        silver[i] = (wallet_amount-gold[i]*10000)//100
        bronze[i] = wallet_amount-gold[i]*10000-silver[i]*100

    embed = discord.Embed(title="恆生富豪榜")
    if wallet_amount > 0:
        description = ""
        for i in range(3):
            description += "No." + str(i+1) + f" <@{ranking[i]}>\n"
            if gold != 0:
                description += str(gold[i]) + "<:shingcoin_1:952960803663937577> "
            if silver != 0:
                description += str(silver[i]) + "<:shingcoin_2:952962920940200026> "
            if bronze != 0:
                description += str(bronze[i]) + "<:shingcoin_3:952963842248421466>"
            description +=  "\n\n"
        embed = discord.Embed(title="恆生富豪榜",
                              description=description,
                              color=discord.Color.greyple())
    else:
        description = "你地都冇錢<:hand_r2:971325523471003668>"
        embed = discord.Embed(title="恆生富豪榜",
                              description=description,
                              color=discord.Color.greyple())
    await message.channel.send(embed=embed)
    return

async def ranking(message, string, label):
    guild = message.guild
    with open(bank_path, 'r') as f:
        bank = json.load(f)
    
    
    ranking = []
    gold = [None] * 3
    silver = [None] * 3
    bronze = [None] * 3
    prize = [None] * 3
    for i in range(3):
        value_amount = -1
        if string.find('ratio') == -1:
            for user in bank[str(guild.id)]:
                if string == 'total_wallet':
                    value = user[string]+user[string[6:]]
                else:
                    value = user[string]
                if value > value_amount:
                    richman = user
                    value_amount = value
            ranking.append(richman['ID'])
            bank[str(guild.id)].remove(richman)
            # print(bank[str(guild.id)])
            if string.find('wallet') != -1:
                gold[i] = value_amount//10000
                silver[i] = (value_amount-gold[i]*10000)//100
                bronze[i] = value_amount-gold[i]*10000-silver[i]*100
            else:
                prize[i] = value_amount
        else:
            for user in bank[str(guild.id)]:
                if string.startswith('total_'):
                    try:
                        value = round(float(user['total_win_count'])/user['total_arena_playcount']*100, 2)
                    except:
                        value = 0
                else:
                    try:
                        value = round(float(user['win_count'])/user['arena_playcount']*100, 2)
                    except:
                        value = 0
                if value > value_amount:
                    richman = user
                    value_amount = value
            ranking.append(richman['ID'])
            bank[str(guild.id)].remove(richman)
            prize[i] = value_amount


    if value_amount > 0:
        description = ""
        for i in range(3):
            description += "No." + str(i+1) + f" <@{ranking[i]}>\n"
            if string.find('wallet') != -1:
                if gold != 0:
                    description += str(gold[i]) + "<:shingcoin_1:952960803663937577> "
                if silver != 0:
                    description += str(silver[i]) + "<:shingcoin_2:952962920940200026> "
                if bronze != 0:
                    description += str(bronze[i]) + "<:shingcoin_3:952963842248421466>"
            elif string.find('ratio') != -1:
                description += str(prize[i])+'%'
            else:
                description += str(prize[i])
            description +=  "\n\n"
        embed = discord.Embed(title=label+"榜",
                              description=description,
                              color=discord.Color.greyple())
    else:
        description = "<:hand_l2:971325453879115797><:hand_r2:971325523471003668>"
        embed = discord.Embed(title=label+"榜",
                              description=description,
                              color=discord.Color.greyple())
    await message.channel.send(embed=embed)
    return


async def entry(guild, user_id, string):
    await create_account(guild, user_id)
    bank = await get_bank_data()
    if string.startswith('total_'):
        if type(user_id) is discord.member.Member:
            for user in bank[str(guild.id)]:
                if user['ID'] == user_id.id:
                    user[string] += 1
                    user[string[6:]] += 1
                    print("success.")
                    break
        if type(user_id) is int:
            for user in bank[str(guild.id)]:
                if user['ID'] == user_id:
                    user[string] += 1
                    user[string[6:]] += 1
                    print("success.")
                    break
    else:
        if type(user_id) is discord.member.Member:
            for user in bank[str(guild.id)]:
                if user['ID'] == user_id.id:
                    user[string] += 1
                    print("success.")
                    break
        if type(user_id) is int:
            for user in bank[str(guild.id)]:
                if user['ID'] == user_id:
                    user[string] += 1
                    print("success.")
                    break
   
    
    with open(bank_path, 'w') as f:
        json.dump(bank, f, indent=4)
        return    

async def earn(guild, user_id, amount):
    await create_account(guild, user_id)
    bank = await get_bank_data()

    if type(user_id) is discord.member.Member:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id.id:
                user['wallet'] += amount
                print("earn success.")
                break
    if type(user_id) is int:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id:
                user['wallet'] += amount
                print("earn success.")
                break
   
    
    with open(bank_path, 'w') as f:
        json.dump(bank, f, indent=4)
        return

async def pay(guild, user_id, amount):
    await create_account(guild, user_id)
    bank = await get_bank_data()

    if type(user_id) is discord.member.Member:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id.id:
                if user['wallet'] > amount:
                    user['wallet'] -= amount
                else:
                    user['wallet'] = 0
                break
    if type(user_id) is int:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id:
                if user['wallet'] > amount:
                    user['wallet'] -= amount
                else:
                    user['wallet'] = 0
                break
    
    with open(bank_path, 'w') as f:
        json.dump(bank, f, indent=4)
        return

async def set(guild, user_id, amount):
    await create_account(guild, user_id)
    bank = await get_bank_data()

    if type(user_id) is discord.member.Member:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id.id:
                user['total_wallet'] = amount
                break
    if type(user_id) is int:
        for user in bank[str(guild.id)]:
            if user['ID'] == user_id:
                user['total_wallet'] = amount
                break
    
    with open(bank_path, 'w') as f:
        json.dump(bank, f, indent=4)
        return

