import json
import discord

# balance

async def balance(message):
    guild = message.guild
    user = message.author
    await create_account(guild, user)
    
    users = await get_bank_data()
    wallet_amount = users[str(guild.id)][str(user.id)]['wallet']
    embed = discord.Embed(title="恆生")
    embed.add_field(name = "成Coin結餘", value = wallet_amount)
    await message.channel.send(embed=embed)



#create account

async def create_account(guild, user):
    users = await get_bank_data()
    
    if type(user) is discord.member.Member:
        if str(guild.id) in users:
            if str(user.id) in users[str(guild.id)]:
                return False
        else:
            users[str(guild.id)] = {}
        users[str(guild.id)][str(user.id)] = {}
        users[str(guild.id)][str(user.id)]['wallet'] = 0
    if type(user) is int:
        if str(guild.id) in users:
            if str(user) in users[str(guild.id)]:
                return False
        else:
            users[str(guild.id)] = {}
        users[str(guild.id)][str(user)] = {}
        users[str(guild.id)][str(user)]['wallet'] = 0
    
    with open('bank.json', 'w') as f:
        json.dump(users, f)
        return



async def get_bank_data():
    with open('bank.json', 'r') as f:
        users = json.load(f)
    return users

async def earn(guild, user, amount):
    await create_account(guild, user)

    if type(user) is discord.member.Member:
        users = await get_bank_data()
        users[str(guild.id)][str(user.id)]['wallet'] += amount
    if type(user) is int:
        users = await get_bank_data()
        users[str(guild.id)][str(user)]['wallet'] += amount
    
    with open('bank.json', 'w') as f:
        json.dump(users, f)
        return

async def pay(guild, user, amount):
    await create_account(guild, user)

    if type(user) is discord.member.Member:
        users = await get_bank_data()
        if users[str(guild.id)][str(user.id)]['wallet'] > 0:
            users[str(guild.id)][str(user.id)]['wallet'] -= amount
    if type(user) is int:
        users = await get_bank_data()
        if users[str(guild.id)][str(user)]['wallet'] > 0:
            users[str(guild.id)][str(user)]['wallet'] -= amount
    
    with open('bank.json', 'w') as f:
        json.dump(users, f)
        return