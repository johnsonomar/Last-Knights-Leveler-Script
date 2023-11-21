from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from secrets import pw_LastKnights, user
import heapq
import re

options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)
link = "https://lastknights.com/"
driver.get(link)
driver.implicitly_wait(5)
#def main():


def login():
    login_ref = "/html/body/tlk-root/div/div/div/div/ng-component/div/div/div/form/div[1]/div[1]/input"
    pw_ref = "/html/body/tlk-root/div/div/div/div/ng-component/div/div/div/form/div[1]/div[2]/input"
    button_name = "button"
    login_field = driver.find_element(by=By.XPATH, value=login_ref)
    pw_field = driver.find_element(by=By.XPATH, value=pw_ref)
    login_button = driver.find_element(by=By.CLASS_NAME, value=button_name)
    ActionChains(driver) \
        .click(login_field) \
        .pause(1) \
        .send_keys_to_element(login_field, user) \
        .pause(1) \
        .click(pw_field) \
        .pause(1) \
        .send_keys_to_element(pw_field, pw_LastKnights) \
        .pause(1) \
        .click(login_button) \
        .pause(1) \
        .perform()


def battleBehavior():  # if above certain level, stop recruiting troops, and start promoting current troops
    levels = ["Private", "Lance Corporal", "Corporal", "Sergeant", "Master Sergeant", "Sergeant-Major",
              "Ensign", "Second Lieutenant", "Lieutenant", "Captain", "Major", "Lieutenant-Colonel", "Colonel"]
    # code something to dynamically grab levels possible, as levels differ depending on map
    if levelCheck() in levels:
        goTrain()
    else:
        print(f"{levelCheck()}  {terrainCheck()}")
        # eventually go border
        # must account for other types of battles


def goTrain():
    t_sub = "battle/training"
    driver.get(link + t_sub)


def goMap():
    m_sub = "map"
    driver.get(link + m_sub)


def goCityCenter():
    c_sub = "city"
    driver.get(link + c_sub)


def goCamp():
    e_sub = "city/encampment"
    driver.get(link + e_sub)


def levelCheck():
    level_ref = "/html/body/tlk-root/tlk-userbar/div[2]/div[1]/div/span"
    level = driver.find_element(by=By.XPATH, value=level_ref).text
    return level


def cityCheck():
    if driver.current_url != "https://lastknights.com/city":
        goCityCenter()
    driver.implicitly_wait(1)
    city_ref = "CityName"
    current_city = driver.find_element(by=By.ID, value=city_ref).text
    return current_city


def mapCheck():
    flag_ref = "/html/body/tlk-root/tlk-userbar/div[2]/div[1]/div/tlk-country-flag/a/img"
    flag_img = driver.find_element(by=By.XPATH, value=flag_ref).get_attribute("src").split("/")[-2]
    return flag_img


def mapTerrain():
    map_check = mapCheck().lower()
    map_terrain = []
    if map_check == "asia":
        map_terrain = ["desert", "forest", "jungle", "mountains", "plains"]
    if map_check == "rome":
        map_terrain = []
    if map_check == "africa":
        map_terrain = []
    if map_check == "europe":
        map_terrain = []
    if map_check == "america":
        map_terrain = []
    return map_terrain


def bestTerrainCheck():
    goCamp()
    best_terrain = ""
    best_terrain_val = 0
    terrains: dict = {}
    values = []
    for i in range(1, 6):
        t_ref = f"/html/body/tlk-root/div/div/div/div/tlk-encampment/div[1]/div[2]/div[1]/div[2]/div[3]/div/div[{i}]/tlk-terrainbonus/span/img"
        v_ref = f"/html/body/tlk-root/div/div/div/div/tlk-encampment/div[1]/div[2]/div[1]/div[2]/div[3]/div/div[{i}]/tlk-terrainbonus/span/span"
        t = str(driver.find_element(by=By.XPATH, value=t_ref).get_attribute("src").split("/")[-1:])
        t = t.split("_")[0]
        t = re.sub("[^A-Za-z]", "", t)
        v = float(driver.find_element(by=By.XPATH, value=v_ref).text.split("%")[0])
        terrains[v] = t
    max1 = heapq.nlargest(1, terrains.keys())[0]
    max2 = heapq.nlargest(2, terrains.keys())[1]
    best_terrain = terrains.get(max1)
    second_best_terrain = terrains.get(max2)
    goCityCenter()
    return best_terrain, second_best_terrain


def borderCities():  # returns list of city options with terrain
    goCityCenter()
    city_options = []
    move_city_ref = ".RedButton"
    movable_cities_ref = ""
    movable_cities = 0
    move_city_button = driver.find_element(by=By.CSS_SELECTOR, value=move_city_ref)
    ActionChains(driver) \
        .move_to_element(move_city_button) \
        .pause(1) \
        .click(move_city_button) \
        .pause(1) \
        .perform()
    while True:
        for i in range(4, 14):
            try:
                movable_cities_ref = f"/html/body/tlk-root/div/div/div/div/tlk-city-center/div/div/div/div[3]/tlk-travel-box/div[2]/div/div/span[{i}]"
                movable_city = driver.find_element(by=By.XPATH, value=movable_cities_ref)
                movable_cities += 1
            except:
                break
        break
    for i in range(4, movable_cities + 4):  # number of border cities changes
        city_options_ref = (f"/html/body/tlk-root/div/div/div/div/tlk-city-center/div/div/div/div["
                            f"3]/tlk-travel-box/div[2]/div/div/span[{i}]/input")
        city_options += [driver.find_element(by=By.XPATH, value=city_options_ref).get_attribute("title")]
    return city_options


def moveBestTerrain():  # WIP
    best_terrain, second_best_terrain = bestTerrainCheck()
    best_terrain = best_terrain.lower()
    second_best_terrain = second_best_terrain.lower()
    current_terrain = terrainCheck().lower()
    border_cities: list = borderCities()
    border_terrains: list = []
    for i, terrain in enumerate(border_cities):
        border_terrain: str = terrain.split(" ")[-1]
        border_terrain = re.sub("[()]", "", border_terrain)
        border_terrains = border_terrains + [border_terrain.lower()]
    print(f"Best Terrain: {best_terrain}")
    print(f"Current Terrain: {current_terrain}")
    if best_terrain == current_terrain:
        print("Current city is optimal for training")
        goTrain()
    elif (best_terrain != current_terrain) and (best_terrain in border_terrains):
        print("There is an optimal city for training at the border")
        while True:  # make this into a function???
            for i in range(4, 14):
                try:
                    movable_cities_ref = f"/html/body/tlk-root/div/div/div/div/tlk-city-center/div/div/div/div[3]/tlk-travel-box/div[2]/div/div/span[{i}]/input"
                    movable_city_button_ref = ""
                    movable_city = driver.find_element(by=By.XPATH, value=movable_cities_ref)
                    movable_city_val = movable_city.get_attribute("class")[0:-6].lower()
                    if movable_city_val == best_terrain:
                        ActionChains(driver) \
                            .move_to_element(movable_city) \
                            .pause(1) \
                            .click() \
                            .perform()
                except:
                    break
            break
        goTrain()
    if best_terrain not in border_terrains:
        print("No viable cities for battle on the border, train at the second best for now!")
        if second_best_terrain == current_terrain:
            print(f"Current city has the second best terrain")
            goTrain()
        elif (second_best_terrain != current_terrain) and (second_best_terrain in border_terrains):
            print("There is an optimal city for training at the border")
            while True:  # make this into a function
                for i in range(4, 14):
                    try:
                        movable_cities_ref = f"/html/body/tlk-root/div/div/div/div/tlk-city-center/div/div/div/div[3]/tlk-travel-box/div[2]/div/div/span[{i}]/input"
                        movable_city_button_ref = ""
                        movable_city = driver.find_element(by=By.XPATH, value=movable_cities_ref)
                        movable_city_val = movable_city.get_attribute("class")[0:-6].lower()
                        if movable_city_val == second_best_terrain:
                            ActionChains(driver) \
                                .move_to_element(movable_city) \
                                .pause(1) \
                                .click() \
                                .perform()
                    except:
                        break
                break
        # check for second-best terrain and move to city with it


def advMoveBestTerrain():
    goMap()
    print("No viable cities for battle on the border, we must search for optimal terrain!")
    city = cityCheck()
    city_ref = ("/html/body/tlk-root/div/div/div/div/tlk-map/div/tlk-panzoom/div/div/svg/g[128]/g/g/title"
                "/html/body/tlk-root/div/div/div/div/tlk-map/div/tlk-panzoom/div/div/svg/g[129]/g/g/title")


def terrainCheck():
    if driver.current_url != "https://lastknights.com/city":
        goCityCenter()
    driver.implicitly_wait(1)
    terrain_ref = "/html/body/tlk-root/div/div/div/div/tlk-city-center/div/tlk-city-title/div/div[4]/span"
    current_terrain = driver.find_element(by=By.XPATH, value=terrain_ref).text
    return current_terrain


def duel():  # WIP
    attack_ref = "/html/body/tlk-root/div/div/div/div/tlk-training/div/div[3]/div[1]"
    heal_ref = "/html/body/tlk-root/div/div/div/div/tlk-training/div/div[3]/div[2]/ul/li[1]"
    attack_button = driver.find_element(by=By.XPATH, value=attack_ref)
    heal_button = driver.find_element(by=By.XPATH, value=heal_ref)
    injury_ref = "/html/body/tlk-root/div/div/div/div/tlk-training/div/div[2]/div[3]/div/div[2]/tlk-battle-injuries/div/div"
    injured = 0
    promotion = False
    while True:
        try:
            injury = driver.find_element(by=By.XPATH, value=injury_ref)
            injured += 1
            break
        except:
            ActionChains(driver) \
                .move_to_element(attack_button) \
                .click(attack_button) \
                .perform()
        #        while not(promotion):
    while injured > 0:
        try:
            ActionChains(driver) \
                .move_to_element(heal_button) \
                .click(heal_button) \
                .perform()
            injury = driver.find_element(by=By.XPATH, value=injury_ref)
        except:
            injured -= 1
            break


# NEED FUNCTION TO RECRUIT TROOPS


def leveler():
    moveBestTerrain()
    promotion_ref = "tlk-promotion-event.ng-star-inserted"
    while True:
        duel()
        for i in range():
            try:
                promotion = driver.find_element(by=By.CSS_SELECTOR, value=promotion_ref)
                print(promotion.text)
                if promotion:
                    break
            except:
                continue
            break

#main()
login()
driver.implicitly_wait(1)
leveler()
