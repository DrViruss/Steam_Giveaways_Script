import requests
import os
import configparser
import time
from bs4 import BeautifulSoup


def loadorcreate(settings_path):
    if os.path.exists(settings_path):
        config = read(settings_path)
        if not testckie(config['PHPSESSID'], config['usera']):
            print("Seems like cookie is expired. Lets update it!")
            config.update({'PHPSESSID': cookie_input("Please input your PHPSESSID: \n", config['usera'])})
            save(settings_path, config)
        return config
    else:
        print("Seems like it's your first run. Lets generate settings")
        return generate(settings_path)


def read(settings_path):
    conf = configparser.ConfigParser()
    conf.optionxform = str
    conf.read(settings_path)
    try:
        usera = conf['connection']["User-agent"]
        phpsessid = conf['connection']["PHPSESSID"]
        wishlist = eval(conf['giveaway']["Wishlist"])
        dlcs = eval(conf['giveaway']["DLCs"])
        banner = eval(conf['giveaway']["Banner"])
        recommended = eval(conf['giveaway']["Recommended"])
        new = eval(conf['giveaway']["New"])
        pinned = eval(conf['giveaway']["Pinned"])
        minP = eval(conf['giveaway']["MinP"])
    except Exception as e:
        print("Something goes wrong on settings reading. \nLets create new!")
        return generate(settings_path)
    return {
        "usera": usera,
        "PHPSESSID": phpsessid,
        "wishlist": wishlist,
        "dlcs": dlcs,
        "banner": banner,
        "recommended": recommended,
        "new": new,
        "pinned": pinned,
        "minP": minP
    }


def save(settings_path, configs):
    conf = configparser.ConfigParser()
    conf.optionxform = str
    conf['connection'] = {
        "User-agent": configs['usera'],
        "PHPSESSID": configs['PHPSESSID']
    }
    conf['giveaway'] = {
        "Wishlist": configs['wishlist'],
        "DLCs": configs['dlcs'],
        "Banner": configs['banner'],
        "Recommended": configs['recommended'],
        "New": configs['new'],
        "Pinned": configs['pinned'],
        "MinP": configs['minP']
    }
    with open(settings_path, 'w') as configfile:
        conf.write(configfile)


def generate(settings_path):
    usera = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 " \
            "Safari/537.36 OPR/94.0.0.0"

    config = {
        "usera": usera,
        "PHPSESSID": cookie_input("Please input your PHPSESSID: \n", usera),
        "wishlist": bool_input("Do you want to enter in wishlist giveaways? (True\False)\n"),
        "dlcs": bool_input("Do you want to enter DLC giveaways? (True\False)\n"),
        "banner": bool_input("Do you want to enter banner giveaways? (True\False)\n"),
        "recommended": bool_input("Do you want to enter recommended giveaways? (True\False)\n"),
        "new": bool_input(
            "Do you want to enter in new giveaways? (True\False)\n !!Attention!! It can take all coins!\n"),
        "pinned": bool_input("Do you want to enter pinned giveaways? (True\False)\n"),
        "minP": number_input("Input min of coins:\n")
    }
    if bool_input("Do you want to switch off giveaways with higher level? (True\False)\n"):
        try_change_settings(config)
    save(settings_path, config)
    return config


def bool_input(question):
    while True:
        var = input(question)
        var = var.capitalize()
        if var == 'True' or var == 'False':
            return eval(var)
        else:
            print('Wrong input')
            continue


def number_input(question):
    while True:
        var = input(question)
        if not var.isdigit():
            print('Wrong input')
            continue
        if eval(var) > 0:
            return eval(var)
        else:
            print("value must be > 0")
            continue


def cookie_input(question, usera):
    while True:
        var = input(question)
        if not var.isalnum():
            print('Wrong input')
            continue
        if testckie(var, usera):
            return var


def testckie(cookie, header):
    try:
        r = requests.head("https://www.steamgifts.com/account/settings/profile", cookies={"PHPSESSID": cookie},
                          headers={"user-agent": header}, timeout=120)
    except Exception as e:
        print("Error!\nSteamgift is possibly unavailable or there is no internet connection or PHPSESSID is not valid")
        return False
    if r.status_code == 301 or r.status_code == 302:
        print("Wrong or expired cookies. Try again.")
        return False
    else:
        return True


def try_change_settings(configs):
    counter = 0
    while True:
        if counter > 10:
            print("Cannot change settings. Maybe couse of internet connection. Please check your connection")
            exit(1)
        if change_giveaway_setting(configs):
            break
        time.sleep(160)
        counter += 1


def get_content(link, configs):
    return BeautifulSoup(
        requests.get(link, cookies={"PHPSESSID": configs['PHPSESSID']},
                     headers={"user-agent": configs['usera']}, timeout=120).text, "html.parser")


def change_giveaway_setting(configs):
    content = get_content("https://www.steamgifts.com/account/settings/giveaways", configs)
    params = {}
    for element in content.find_all('input'):
        if element['name'] == "xsrf_token" or \
                element['name'] == "filter_giveaways_exist_in_account" or \
                element['name'] == "filter_giveaways_missing_base_game" or \
                element['name'] == "filter_giveaways_additional_games":
            params.update({element["name"]: element["value"]})
    params.update({"filter_os": content.find('option', selected=True).get("value")})
    params.update({"filter_giveaways_level": 1})
    try:
        r = requests.post("https://www.steamgifts.com/account/settings/giveaways",
                          data=params,
                          cookies={"PHPSESSID": configs['PHPSESSID']},
                          headers={"user-agent": configs['usera']},
                          timeout=120
                          )
    except:
        print("Site is not available...\n Stop app or wait. I'll try again after 2min")
        return False
    if r.status_code == 200:
        print("Account settings successfully changed")
        return True
    else:
        print(
            f"Something goes wrong. Please send this to developer: \n Error on changing settings.\n Code={r.status_code},\n data={params},\n usera={configs['usera']}")
        exit(1)
