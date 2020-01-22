import json
import requests
import io
import base64
from time import sleep
from nbt import * # !! sudo pip3 install nbt !!

r = requests.get("https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page=0")
auction_page_json = r.json()

rawBytes="H4sIAAAAAAAAABWNfwqCMBzF36aZG0FH6CxhPyEnZBf4xtYYTA2dUCfyHh4smn++x+d9ngQEmJMAGAd3mu0YVkU3toFLJIFsAnFx2pw82SFSP4m1dsPb01cgvXW9yZctNvP0midfVGVZqRyposZAxLIOvWstJLbHT+hpH2J+jsEM+XKHrH7cr+oMcGQHasiaqMMfWzshTJcAAAA="


def decode_inventory_data(raw):
   data = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
   print(data.pretty_tree() #tags(0)) #["TAG_Compound"]["Count"].value)

decode_inventory_data(rawBytes)

for i in range(0, auction_page_json["totalPages"]):
    r = requests.get(f"https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page={i}")
    auction = r.json()
    auction_str = json.dumps(auction["auctions"][0], indent=2)
    print(auction_str)
    

    data = {
        'item': "brofit",
        'itemAmount': 1,
        "auctionUUID": "fefee",
        "timeStamp": 1579721246009
    }

    sleep(0.5)
# auctions_str = json.dumps(auctions_json["auctions"][0], indent=2)
# print(auctions_str)