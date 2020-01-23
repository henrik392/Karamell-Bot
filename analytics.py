import json
import requests
import io
import base64
from time import sleep
from nbt import * # !! sudo pip install nbt !!

r = requests.get("https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page=0")
auction_page_json = r.json()


def ItemDataCount(raw):
   data = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
   
   return data["i"][0]["Count"]

results = []

for i in range(0, auction_page_json["totalPages"]):
    r = requests.get(f"https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page={i}")
    auctions = r.json()
    
    for auction in auctions["auctions"]:
        data = {
        "name": auction["item_name"],
        "uuid": auction["uuid"],
        "count": ItemDataCount(auction["item_bytes"]),
        "end": auction["end"]
        }
        results.append(data)
    sleep(0.6)

timeSortedResults = sorted() results

# auctions_str = json.dumps(auctions_json["auctions"][0], indent=2)
# print(auctions_str)