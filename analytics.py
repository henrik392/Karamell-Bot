import json
import requests
from time import sleep
 

r = requests.get("https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page=0")
package_page_json = r.json()

for i in range(0, package_page_json["totalPages"]):
    r = requests.get(f"https://api.hypixel.net/skyblock/auctions?key=49e3e277-19e8-44e6-9d9d-0230ff58092e&page={i}")
    package = r.json()
    package_str = json.dumps(package["auctions"][0], indent=2)
    print(package_str)
    sleep(0.5)


# packages_str = json.dumps(packages_json["auctions"][0], indent=2)
# print(packages_str)