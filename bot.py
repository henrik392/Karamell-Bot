import discord, urllib.request, json, random
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

userAuctionUrl = "https://api.hypixel.net/skyblock/auction?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&profile=8be707e39cb146e69694638d4e3cd811"

with urllib.request.urlopen(userAuctionUrl) as url:
    data = json.loads(url.read().decode())

print("success:", data["success"])

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith(('hello').lower()):
#         await message.channel.send('Hello!')
    
#     if message.content.startswith(('krle').lower()):
#         #await message.channel.send('KRLE = Kjedelig')
#         await message.channel.send('KRLE = Kristendom, religion, livssyn og etikk')
    
#     if message.content.startswith(('oof').lower()):
#         await message.channel.send('...')


@client.command()
async def ping(ctx):
    await ctx.send(f'bruh {round(client.latency * 1000)}ms')

@client.command(aliases=['8ball', 'test'])
async def magic_glass_block(ctx, *, question):
    responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, *, amount=1):
    await ctx.channel.purge(limit=amount+1)

@client.command()
@commands.has_permissions(administrator=True)
async def admin(ctx):
    await ctx.send('No shit')

@client.command()
@commands.has_permissions(administrator=True)
async def get_last_auctions(ctx):
    await ctx.send(f'success: {data["success"]}')
    for auction in data["auctions"]:
        if auction["claimed"] == False:
            await ctx.send(f'Item: {auction["item_name"]}')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server')
 
@client.event
async def on_member_remove(member):
    print(f'{member} has left a server')



client.run('NjUyNTkwODc1MDMzMjA2Nzg1.XeuavQ.0eHnIuNT1BWLowOoXKZNbctlUvo')