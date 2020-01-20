import discord, urllib.request, json, random, datetime
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

key = "49e3e277-19e8-44e6-9d9d-0230ff58092e"
profile = "8be707e39cb146e69694638d4e3cd811"

userAuctionUrl = f"https://api.hypixel.net/skyblock/auction?key={key}&profile={profile}"
auctionsUrl = f"https://api.hypixel.net/skyblock/auctions?key={key}&page=0"

class UsernameChache:
    name = ""
    uuid = ""
    timestamp = 0

    def __init__(self, name, uuid, timestamp):
        self.name = name
        self.uuid = uuid
        self.timestamp = timestamp


usernameCache = []

#if self.timestamp + 600 > datetime.datetime.now().timestamp():
#    pass

def TimestampDate(timestamp):
    return datetime.datetime.fromtimestamp(round(timestamp/1000))
    

def SecondsToDateTime(sec):
    time = [0, 0, 0, 0]
    time[0] = sec // (24 * 3600)
    sec = sec % (24 * 3600)
    time[1] = sec // 3600
    sec %= 3600

    time[2] = sec // 60
    sec %= 60
    time[3] = sec
    return time

def TimestampTimeSince(timestamp):
    currentTimestamp = datetime.datetime.now().timestamp()
    timestampSec = timestamp / 1000

    dateTimeSinceString = ""
    if round(currentTimestamp - timestampSec) > 0:
        timeSince = round(currentTimestamp - timestampSec)
        dateTimeSinceString = "Ended: "
    else:
        timeSince = round(timestampSec - currentTimestamp)
        dateTimeSinceString = "Ends: "

    timeSinceDT = SecondsToDateTime(timeSince)
    dateTimeSinceString += f"{timeSinceDT[0]}d : {timeSinceDT[1]}h : {timeSinceDT[2]}m : {timeSinceDT[3]}s"

    return dateTimeSinceString


def ParseJson(jsonUrl):
    with urllib.request.urlopen(jsonUrl) as url:
        return json.loads(url.read().decode())

def GetAuctionPage(auctionPage):
    pageUrl = f"https://api.hypixel.net/skyblock/auctions?key={key}&page={auctionPage}"
    return ParseJson(pageUrl)


client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
    userAuctionData = ParseJson(userAuctionUrl)
    await ctx.send(f'success: {userAuctionData["success"]}')
    for auction in userAuctionData["auctions"]:
        if auction["claimed"] == False:
            await ctx.send(f'Item: {auction["item_name"]}')

@client.command()
@commands.has_permissions(administrator=True)
async def get_last_claimed_auctions(ctx):
    userAuctionData = ParseJson(userAuctionUrl)
    await ctx.send(f'success: {userAuctionData["success"]}')
    for auction in userAuctionData["auctions"]:
        if auction["claimed"]:
            await ctx.send(f'Item: {auction["item_name"]} |-|BROFIT|-| Price: {auction["highest_bid_amount"]}')

@client.command()
@commands.has_permissions(administrator=True)
async def get_random_auction(ctx):
    auctionsData = ParseJson(auctionsUrl)
    await ctx.send(f'Connected to api: {auctionsData["success"]}')
    randomPage = random.randint(0, auctionsData["totalPages"]-1)
    auctionsData = GetAuctionPage(randomPage)
    randomAuctionIndex = random.randint(0, len(auctionsData["auctions"])-1)
    auction = auctionsData["auctions"][randomAuctionIndex]
    priceString = "Price: " + str(auction["highest_bid_amount"]) if len(auction["bids"]) != 0 else "Starting Bid: " + str(auction["starting_bid"])
    
    inCache = False
    if len(UsernameChache) != 0:
        for player in usernameCache:
            if player.uuid == auction["auctioneer"]:
                inCache = True

    if not inCache:
        while usernameCache[0].timestamp + 600 > datetime.datetime.now().timestamp():
            usernameCache.pop(0)
        playerDataUrl = "https://sessionserver.mojang.com/session/minecraft/profile/" + auction["auctioneer"]
        print(playerDataUrl)
        playerData = ParseJson(playerDataUrl)
        name = playerData["name"]
        usernameCache.append(UsernameChache(name, playerData["uuid"], datetime.datetime.now().timestamp()))

    await ctx.send(f'Item: {auction["item_name"]} | {TimestampTimeSince(auction["end"])} | ' + priceString + ' | User: ' + name)


@client.event
async def on_member_join(member):
    print(f'{member} has joined a server')
 
@client.event
async def on_member_remove(member):
    print(f'{member} has left a server')



client.run('NjUyNTkwODc1MDMzMjA2Nzg1.XeuavQ.0eHnIuNT1BWLowOoXKZNbctlUvo')