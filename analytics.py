import json
import requests
import io
import base64
from time import sleep
from nbt import nbt # !! sudo pip install nbt !!
from datetime import datetime

def ItemDataCount(raw):
   data = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
   
   return int(data["i"][0]["Count"].valuestr())

def AnalyzeAuctions():
    r = requests.get("https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page=0")
    auctions = r.json()
    results = []

    i = 0
    while i < auctions["totalPages"]:
        if i != 0:
            r = requests.get(f"https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page={i}")
            auctions = r.json()

        for auction in auctions["auctions"]:
            data = {
                "item_name": auction["item_name"],
                "uuid": auction["uuid"],
                "count": ItemDataCount(auction["item_bytes"]),
                "end": round(auction["end"]/1000),
                "starting_bid": auction["starting_bid"],
                "highest_bid": auction["highest_bid_amount"]
            }
            results.append(data)


        print(round((i + 1) * 100 / auctions["totalPages"]), "%")
        sleep(0.5)
        i += 1

    return results

def UpdateAuctionsJson():
    auctions = AnalyzeAuctions()
    auctionsByTime = sorted(auctions, key=lambda k: k['end'])

    jsonData = {}
    jsonData["sorted_auctions"] = auctionsByTime
    with open('auctions.json', 'w') as outfile:
        json.dump(jsonData, outfile)
    
    print("-SUCCESS-")


def AnalyzeTimes(times):
    for i in range(0, times):
        UpdateAuctionsJson()
        sleep(100)

while True:
    loop = input("How many time do you want to loop? ")
    try:
        AnalyzeTimes(int(loop))
    except:
        exit()
        
    