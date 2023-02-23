import requests
import settings
import re
from bs4 import BeautifulSoup
import time
import random


def get_games_list(content):
    games = list()
    if not configs['pinned']:
        content.find(class_="pinned-giveaways__outer-wrap").decompose()
    for row in content.find_all(class_="giveaway__row-outer-wrap"):
        if row.find(class_="is-faded") is None:
            games.append(row.find_next(class_="giveaway_image_thumbnail").get("href"))
    return games


def check_banner(content):
    link = content.find(class_="global__image-outer-wrap global__image-outer-wrap--game-xlarge").get("href")
    enter_giveaway(link)


def check_page(type):
    print(f"Checking for {type.title()} page for something interesting..")
    page = 1
    while True:
        content = get_content(f"https://www.steamgifts.com/giveaways/search?page={page}&type={type}")
        if configs['banner']:
            check_banner(content)
        if content.find(class_="pagination__results").text == "No results were found.":
            print(f"{type.title()} page done. (or its empty)")
            return True
        for game in get_games_list(content):
            if not enter_giveaway(game):
                print("Something goes wrong..(may be need higher level) Skipping this game")
        print(f"Page {page} done")
        page += 1
    # return True
    # pass


def enter_giveaway(link):  # ex /giveaway/lzpGm/magical-swordmaiden
    content = get_content(f"https://www.steamgifts.com{link}")
    if content.find(class_="sidebar__entry-insert is-hidden") is not None:
        return True
    coins = get_coins(content)
    gcost = content.find(class_="featured__heading__small").get_text()
    if (coins - eval(re.findall(r'\d+', gcost)[0])) <= configs["minP"]:
        print(
            f"Cannot enter to giveaway [https://www.steamgifts.com{link}].\nCoins will descent less then minimum alowed.\nStopping..")
        exit(1)
    params = {}
    for element in content.find_all('input'):
        if element['name'] == "xsrf_token" or element['name'] == "code":
            params.update({element["name"]: element["value"]})
    params.update({"do": "entry_insert"})
    try:
        r = requests.post("https://www.steamgifts.com/ajax.php",
                          data=params,
                          cookies={"PHPSESSID": configs['PHPSESSID']},
                          headers={"user-agent": configs['usera']},
                          timeout=120
                          )
        result = r.json()
    except:
        print("Site is not available...")
        time.sleep(20)
        return False
    if result["type"] == "success":
        coins = result["points"]
        game_name = link.split('/')
        print(f"You just entered to giveaway of {game_name[3].replace('-', ' ').title()}\nCurrent coins = {coins}")
        time.sleep(random.randint(2, 60))
        return True
    return False


def get_content(link):
    return BeautifulSoup(
        requests.get(link, cookies={"PHPSESSID": configs['PHPSESSID']},
                     headers={"user-agent": configs['usera']}, timeout=120).text, "html.parser")


def get_coins(soup, cl_="nav__points"):
    return eval(soup.find(class_=cl_).get_text())


print("Welcome!\nLets start..")
time.sleep(3)
configs = settings.loadorcreate("./settings.cfg")
if configs['minP'] >= get_coins(get_content("https://www.steamgifts.com")):
    print("Current coins less then min. Please start script later.")
    exit(1)
if configs["wishlist"]:
    check_page("wishlist")
if configs["recommended"]:
    check_page("recommended")
if configs["new"]:
    check_page("new")

print("Work done. Bye!")
exit(0)

# TODO:
#  *add dlcs
