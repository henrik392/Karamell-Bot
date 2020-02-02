import datetime
import json
import random
import urllib.request

import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions

with open('APIkey.txt') as infile:  # Reads APIkey.txt
    keys = infile.readlines()

key = keys[0].rstrip()
profile = "8be707e39cb146e69694638d4e3cd811"

userAuctionUrl = f"https://api.hypixel.net/skyblock/auction?key={key}&profile={profile}"
auctionsUrl = f"https://api.hypixel.net/skyblock/auctions?key={key}&page=0"

client = commands.Bot(command_prefix='*')

# region Other functions


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
    timestampSec = timestamp / 1000 if timestamp > 9_999_999_999 else timestamp

    dateTimeSinceString = ""
    if currentTimestamp > timestampSec:
        timeSince = round(-timestampSec + currentTimestamp)
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


def NameFromUUID(uuid):
    with open('username.json') as infile:
        usernamesJSON = json.load(infile)

    usernameList = usernamesJSON["username_list"]
    if len(usernameList) != 0:
        for player in usernameList:
            if player["uuid"] == uuid:
                return player["name"]

    # if len(usernameCache) > 0:
    #     while usernameCache[0].timestamp + 600 > datetime.datetime.now().timestamp():
    #         usernameCache.pop(0)

    playerDataUrl = "https://sessionserver.mojang.com/session/minecraft/profile/" + uuid
    print(playerDataUrl)
    playerData = ParseJson(playerDataUrl)
    username = playerData["name"]
    usernameList.append({
        "name": username,
        "uuid": playerData["id"],
        "timestamp": datetime.datetime.now().timestamp()
    })

    jsonData = {}
    jsonData["username_list"] = usernameList
    with open('username.json', 'w') as outfile:
        json.dump(jsonData, outfile)

    return username


def UUIDFromName(name):
    with open('username.json') as infile:
        usernamesJSON = json.load(infile)

    usernameList = usernamesJSON["username_list"]
    if len(usernameList) != 0:
        for player in usernameList:
            if player["name"] == name:
                return player["uuid"]

    playerDataUrl = "https://api.mojang.com/users/profiles/minecraft/" + name
    print(playerDataUrl)
    playerData = ParseJson(playerDataUrl)
    uuid = playerData["id"]
    usernameList.append({
        "name": playerData["name"],
        "uuid": uuid,
        "timestamp": datetime.datetime.now().timestamp()
    })

    jsonData = {}
    jsonData["username_list"] = usernameList
    with open('username.json', 'w') as outfile:
        json.dump(jsonData, outfile)

    return uuid
# endregion


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('Spiser karemeller'))


@client.command()
@commands.has_permissions(administrator=True)
# Gets random auction from the auctionhouse api (mostly for testing the api)
async def get_random_auction(ctx):
    auctionsData = ParseJson(auctionsUrl)  # Gets auction data
    # Checks for connection
    await ctx.send(f'Connected to api: {auctionsData["success"]}')
    randomPage = random.randint(0, auctionsData["totalPages"]-1)
    auctionsData = GetAuctionPage(randomPage)
    randomAuctionIndex = random.randint(0, len(auctionsData["auctions"])-1)
    auction = auctionsData["auctions"][randomAuctionIndex]
    priceString = "Price: " + str(auction["highest_bid_amount"]) if len(
        auction["bids"]) != 0 else "Starting Bid: " + str(auction["starting_bid"])

    name = NameFromUUID(auction["auctioneer"])

    await ctx.send(f'Item: {auction["item_name"]} | {TimestampTimeSince(auction["end"])} | ' + priceString + ' | User: ' + name)


@client.command()
@commands.has_permissions(administrator=True)
# returns items with matching ane and pircerange where your are not the highest bidder
async def stonks(ctx, item_name, price_max, username):
    with open('auctions.json') as infile:  # Reads auction.json
        auctionResults = json.load(infile)

    # try except error from UUIDFromName
    try:
        usernameUUID = UUIDFromName(username)  # Get uuid from username
    except:
        await ctx.send('Mojang name to uuid api request failed.')
        usernameUUID = '30f31719332745ed9a1cd8894c51ccd0'

    # Embedded message
    auctionEmbed = discord.Embed(
        title=f'Auctions for {item_name}',
        description=f'{item_name} below {price_max} ending in 1 - 5 min',
        colour=discord.Color.gold()
    )
    auctionEmbed.set_footer(text='That\'s it')
    auctionEmbed.set_author(name='The one and only MR. Sheep')

    # vars
    price_max = float(price_max)
    field = 0

    # Cycles through each auction
    for auction in auctionResults["sorted_auctions"]:
        # until x amount of seconds passed
        if auction["end"] - 300 > round(datetime.datetime.now().timestamp()):
            if field == 0:  # If no matched auctions found
                auctionEmbed.add_field(
                    name='Sorry.', value='No auctions', inline=False)

            # send auctions in embedded message
            await ctx.send(embed=auctionEmbed)
            break

        # gets the acctual cost of current price, (might be outdated)
        cost = auction["highest_bid"] * \
            1.15 if auction["highest_bid"] != 0 else auction["starting_bid"]
        if auction["end"] - 60 > datetime.datetime.now().timestamp() and auction["item_name"].lower() == item_name.lower() and cost <= price_max * auction["count"]:
            # Gets auction to update old information from auctions.json
            try:
                auctionJSON = ParseJson(
                    f'https://api.hypixel.net/skyblock/auction?key={key}&uuid=' + auction["uuid"])["auctions"][0]
            except:
                await ctx.send('Hypixel api request failed.')

            # Gets updated price and different variasons of price
            isStartingBidString = ""
            isStartingBid = auctionJSON["highest_bid_amount"] != 0
            if isStartingBid:
                price = auctionJSON["highest_bid_amount"]
                cost = price * 1.15
            else:
                price = auctionJSON["starting_bid"]
                cost = price
                isStartingBidString = ", starting bid"

            highestBidderUUID = auctionJSON["bids"][len(
                auctionJSON["bids"])-1]  # Gets highest bidder
            # If in price range and youre not the highest bidder...
            if cost <= price_max * auction["count"] and highestBidderUUID != usernameUUID:
                # Gets username of auctioneer
                try:
                    auctioneer = NameFromUUID(auctionJSON["auctioneer"])
                except:
                    await ctx.send('Mojang uuid to name api request failed.')

                cost = round(cost)  # rounds the cost

                # Adds field for auction, and invisible field for a line break
                auctionEmbed.add_field(name=f'{auction["count"]}x {auction["item_name"]}',
                                       value=f'{TimestampTimeSince(auction["end"])}  |  username: {auctioneer}', inline=True)
                auctionEmbed.add_field(
                    name='prices', value=f'Price: {price:,}{isStartingBidString}  |  Min cost: {cost:,}  |  Min cost per: {round(cost/auction["count"]):,}', inline=True)
                auctionEmbed.add_field(
                    name='\u200b', value='\u200b', inline=False)
                # Add to field index
                field += 1


@client.command()
@commands.has_permissions(administrator=True)
async def watchlist(ctx, item_name, price_max, username):
    with open('auctions.json') as infile:  # Reads auction.json
        auctionResults = json.load(infile)

    # try except error from UUIDFromName
    try:
        usernameUUID = UUIDFromName(username)  # Get uuid from username
    except:
        await ctx.send('Mojang name to uuid api request failed.')
        usernameUUID = '30f31719332745ed9a1cd8894c51ccd0'

    # Embedded message
    auctionEmbed = discord.Embed(
        title=f'Auctions for {item_name}',
        description=f'{item_name} below {price_max} ending in 1 - 5 min',
        colour=discord.Color.gold()
    )
    auctionEmbed.set_footer(text='That\'s it')
    auctionEmbed.set_author(name='The one and only MR. Sheep')

    # vars
    price_max = float(price_max)
    field = 0

    # Cycles through each auction
    for auction in auctionResults["sorted_auctions"]:
        # until x amount of seconds passed
        if auction["end"] - 300 > round(datetime.datetime.now().timestamp()):
            if field == 0:  # If no matched auctions found
                auctionEmbed.add_field(
                    name='Sorry.', value='No auctions', inline=False)

            # send auctions in embedded message
            await ctx.send(embed=auctionEmbed)
            break

        # gets the acctual cost of current price, (might be outdated)
        cost = auction["highest_bid"] * \
            1.15 if auction["highest_bid"] != 0 else auction["starting_bid"]
        if auction["end"] - 60 > datetime.datetime.now().timestamp() and auction["item_name"].lower() == item_name.lower() and cost <= price_max * auction["count"]:
            # Gets auction to update old information from auctions.json
            try:
                auctionJSON = ParseJson(
                    f'https://api.hypixel.net/skyblock/auction?key={key}&uuid=' + auction["uuid"])["auctions"][0]
            except:
                await ctx.send('Hypixel api request failed.')

            # Gets updated price and different variasons of price
            isStartingBidString = ""
            isStartingBid = auctionJSON["highest_bid_amount"] != 0
            if isStartingBid:
                price = auctionJSON["highest_bid_amount"]
                cost = price * 1.15
            else:
                price = auctionJSON["starting_bid"]
                cost = price
                isStartingBidString = ", starting bid"

            highestBidderUUID = auctionJSON["bids"][len(
                auctionJSON["bids"])-1]  # Gets highest bidder
            # If in price range and youre not the highest bidder...
            if cost <= price_max * auction["count"] and highestBidderUUID != usernameUUID:
                # Gets username of auctioneer
                try:
                    auctioneer = NameFromUUID(auctionJSON["auctioneer"])
                except:
                    await ctx.send('Mojang uuid to name api request failed.')

                cost = round(cost)  # rounds the cost

                # Adds field for auction, and invisible field for a line break
                auctionEmbed.add_field(name=f'{auction["count"]}x {auction["item_name"]}',
                                       value=f'{TimestampTimeSince(auction["end"])}  |  username: {auctioneer}', inline=True)
                auctionEmbed.add_field(
                    name='prices', value=f'Price: {price:,}{isStartingBidString}  |  Min cost: {cost:,}  |  Min cost per: {round(cost/auction["count"]):,}', inline=True)
                auctionEmbed.add_field(
                    name='\u200b', value='\u200b', inline=False)
                # Add to field index
                field += 1


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

# region Non auction
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
@commands.has_permissions(administrator=True)
async def shut_down(ctx):
    await ctx.send('Shutting down...')
    exit()


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, *, amount=1):
    await ctx.channel.purge(limit=amount+1)


@client.command()
@commands.has_permissions(administrator=True)
async def admin(ctx):
    await ctx.send('No shit')
# endregion


# region Client events
@client.event
async def on_member_join(member):
    print(f'{member} has joined the server')


@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')
# endregion

client.run(keys[1].rstrip())