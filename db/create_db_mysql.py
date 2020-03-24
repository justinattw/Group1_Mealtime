"""


@author: Danny Wallis (

Note: Don't touch. Not intended for final use, but for migration of SQLite database to MySQL.
"""

import re
import time

import mysql.connector
import requests
from bs4 import BeautifulSoup

start_time = time.time()

conn = mysql.connector.connect(
    host="localhost",
    user="username",  # Replace with your MySQL user name
    passwd="pwd",  # Replace with your MySQL password
    port=5000  # Replace with your port number
)

c = conn.cursor()

c.execute("CREATE DATABASE IF NOT EXISTS mealtime DEFAULT CHARACTER SET 'utf8'")
c.execute("USE mealtime")

sql = '''CREATE TABLE IF NOT EXISTS `Recipes` (
                                    `recipe_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `recipe_name` varchar(40) NOT NULL,
                                    `photo` varchar(40) NOT NULL,
                                    `serves` integer,
                                    `cook_time` integer,
                                    `prep_time` integer,
                                    `total_time` integer,
                                    PRIMARY KEY (`recipe_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `RecipeIngredients` (
                                    `recipe_ingredient_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `recipe_id` integer NOT NULL,
                                    `ingredient` varchar(40) NOT NULL,                                    
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    PRIMARY KEY (`recipe_ingredient_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `NutritionValues` (
                                    `nutrition_value_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `recipe_id` integer NOT NULL,
                                    `calories` float, 
                                    `fats` float,
                                    `saturates` float,
                                    `carbs` float,
                                    `sugars` float,
                                    `fibres` float,
                                    `proteins` float,
                                    `salts` float,                                
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    PRIMARY KEY (`nutrition_value_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `RecipeInstructions` (
                                    `recipe_instruction_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `recipe_id` integer NOT NULL,
                                    `step_num` integer NOT NULL,
                                    `step_description` varchar(40) NOT NULL,                                    
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    PRIMARY KEY (`recipe_instruction_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `DietTypes` (
                                    `diet_type_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `diet_name` varchar(40),                                    
                                    PRIMARY KEY (`diet_type_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

values = [(1, 'classic'),
          (2, 'pescatarian'),
          (3, 'vegetarian'),
          (4, 'vegan')]
sql = ("INSERT INTO DietTypes (diet_type_id, diet_name) VALUES (%s, %s)")
c.executemany(sql, values)

sql = '''CREATE TABLE IF NOT EXISTS `Allergies` (
                                    `allergy_id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `allergy_name` varchar(40) NOT NULL,                                    
                                    PRIMARY KEY (`allergy_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

values = [(1, 'celery'),
          (2, 'gluten'),
          (3, 'seafood'),
          (4, 'eggs'),
          (5, 'lupin'),
          (6, 'mustard'),
          (7, 'tree_nuts'),
          (8, 'peanuts'),
          (9, 'sesame_seeds'),
          (10, 'soybeans'),
          (11, 'dairy')]
sql = ("INSERT INTO Allergies (allergy_id, allergy_name) VALUES (%s, %s)")
c.executemany(sql, values)

sql = '''CREATE TABLE IF NOT EXISTS `RecipeDietTypes` (
                                    `recipe_id` integer NOT NULL UNIQUE,
                                    `diet_type_id` integer NOT NULL,
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    FOREIGN KEY (`diet_type_id`) REFERENCES `DietTypes` (`diet_type_id`),
                                    PRIMARY KEY (`allergy_id`, `diet_type_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `RecipeAllergies` (
                                    `recipe_id` integer NOT NULL,
                                    `allergy_id` integer NOT NULL,
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    FOREIGN KEY (`allergy_id`) REFERENCES `Allergies` (`allergy_id`),
                                    PRIMARY KEY (`recipe_id`, `allergy_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

# Delete all recipe images
from os.path import dirname, abspath, join

CWD = dirname(abspath(__file__))
recipe_img_dir = join(CWD, '../app/static/img/recipe_images')
try:
    import shutil

    shutil.rmtree(recipe_img_dir)
    import os

    os.mkdir(recipe_img_dir)
except:
    pass

URL = "https://www.bbcgoodfood.com/recipes/category/healthy"
page = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
print(page)
soup = BeautifulSoup(page.content, 'html.parser')

items = soup.find_all('div', class_='row pad-left pad-right content-recipe-categories')
print(items)

for item in items:
    links = item.find_all('a')
    print(links)

first_urls = []
second_urls = []

for link in links:
    data = str(link).split('"')
    first_urls.append('https://www.bbcgoodfood.com/' + data[1])

for url in first_urls:
    URL = url
    page = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    meals = soup.find_all('article', class_='node node-recipe node-teaser-item clearfix')
    tags = soup.find_all('div', class_='teaser-item__info')

    for meal in meals:
        name = meal.find('h3', class_='teaser-item__title')
        tag = meal.find('div', class_='teaser-item__info')
        links = meal.find_all('a')
        for link in links:
            data = str(link).split('"')
            second_urls.append('https://www.bbcgoodfood.com/' + data[1])

second_urls = set(second_urls)
three = []
nutritionalinfo = []
methodology = []
n = 0
recipeidindex = 0
recipestepsindex = 0
ingredientindex = 0
nutritionindex = 0

for url in second_urls:

    interim_time = time.time()

    queryrecipes = ("INSERT INTO Recipes VALUES (%s, %s, %s, %s, %s, %s, %s)")
    queryingredients = ("INSERT INTO RecipeIngredients VALUES (%s, %s, %s)")
    querynutrition = ("INSERT INTO NutritionValues values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    queryinstructions = ("INSERT INTO RecipeInstructions VALUES (%s, %s, %s, %s)")
    queryrecipeallergies = ("INSERT INTO RecipeAllergies VALUES (%s, %s)")
    queryrecipediettypes = ("INSERT INTO RecipeDietTypes VALUES (%s, %s)")

    ingredient_list = []
    URL = url
    page = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find('h1', class_='recipe-header__title')
    times = soup.find('div', class_='recipe-details__text')
    serves = soup.find('section', class_='recipe-details__item recipe-details__item--servings')
    ingredients = soup.find_all('li', class_='ingredients-list__item')
    method = soup.find_all('li', class_='method__item')
    nutrition = soup.find_all('ul', class_='nutrition')
    serving = serves.find('span', class_='recipe-details__text')
    name = title.text

    preptimes = []
    cooktimes = []
    t = str(times.text).split('Cook')
    if len(t) == 0:
        pass
    if len(t) == 1:
        hyphened = str(times.text).split('-')
        if len(hyphened) == 1:
            split = str(times.text).split()
            for item in split:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    preptimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    preptimes.append(float(x) * 60)
                i = i + 1

        elif len(hyphened) == 2:
            split = hyphened[1]
            for item in split:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    preptimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    preptimes.append(float(x) * 60)
                i = i + 1

    if len(t) == 2:

        before = t[0]
        after = t[1]
        beforesplit = before.split('-')
        aftersplit = after.split('-')
        print(beforesplit)
        print(aftersplit)
        if len(beforesplit) == 1:
            bsplit = before.split()
            for item in bsplit:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    preptimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    preptimes.append(float(x) * 60)

        if len(beforesplit) == 2:
            bsplit = beforesplit[1]
            b1split = bsplit.split()
            for item in b1split:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    preptimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    preptimes.append(float(x) * 60)
                i = i + 1

        if len(aftersplit) == 2:
            asplit = aftersplit[1]
            a1split = asplit.split()
            for item in a1split:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    cooktimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    cooktimes.append(float(x) * 60)
                i = i + 1

        if len(aftersplit) == 1:
            asplit = after.split()
            for item in asplit:
                i = 0
                if item.isdigit():
                    x = item
                if "m" in item:
                    cooktimes.append(float(x))
                elif "h" in item:
                    print("gotcha")
                    cooktimes.append(float(x) * 60)

    print(t)
    print(preptimes)
    print(cooktimes)
    y = 0
    z = 0
    for x in preptimes:
        y = y + x
    for x in cooktimes:
        z = z + x
    total = y + z
    plz = serves.text.split()
    why = 0.0
    for item in plz:
        if item.isdigit():
            why = float(item)
    print(why)

    if total < 200 and total != 0 and why != 0:

        pic_url = soup.find('div', class_='recipe-header__media').find("img")
        if pic_url is not None:
            pic_url = str(pic_url).split('"')
            pic_url = pic_url[7]
            pic_url = "https:" + pic_url
        print(pic_url)
        file_path = 'app/static/img/recipe_images/'
        pic_name = file_path + str(recipeidindex) + '.jpg'
        file_name = str(recipeidindex) + '.jpg'
        with open(pic_name, 'wb') as handle:
            response = requests.get(pic_url, headers={'User-Agent': 'Mozilla/5.0'})

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        # steps for database
        stepnum = 1
        for meth in method:
            met = str(meth)
            one = met.split('<p>')
            two = str(one[1]).split('</p>')
            if '</a>' in two[0]:
                three = str(two[0]).split('<a')
                four = str(three[1]).split('</a>')
                final = (str(three[0]) + str(four[1]))
                methodology.append(final)

            else:
                final = two[0]
                three = []
                methodology.append(final)
            if len(three) > 2:
                print('THREE!')
                final = ''
            # c.execute(queryinstructions, (int(recipestepsindex), int(recipeidindex), int(stepnum), str(final)))
            c.execute(queryinstructions, (int(recipestepsindex), int(recipeidindex), int(stepnum), str(final)))
            recipestepsindex = recipestepsindex + 1
            stepnum = stepnum + 1

        dairy_allergy_added = False
        dairies = ["butter", "milk", "yogurt", "yoghurt", "yak", "whey", "sarasson", "semifreddo", "ayran",
                   "curd", "custard", "crème fraîche", "eggnog", "fromage", "gelato", "mozzarella", "parmesan",
                   "ricotta", "cheese"]
        celery_allergy_added = False
        gluten_allergy_added = False
        glutens = ["pasta", "ravioli", "dumpling", "couscous", "gnocchi",
                   "ramen", "udon", "soba", "chow mein",
                   "croissant", "pita", "naan", "bagel", "flatbread", "cornbread", "bread",
                   "granola", "pancake", "panko breadcrumb", "soy sauce", "barley", "malt",
                   "bulger", "graham flour", "oatmeal", "flour", "rye", "semolina", "spelt",
                   "wheat", "spaghetti", "lasagne"]
        seafood_allergy_added = False
        seafoods = ["fish", "squid", "octopus", "fish", "snail", "mussel", "clam", "oyster", "scallop", "whelk",
                    "crab", "shrimp", "lobster", "prawn", "krill", "barnacle", "cod", "salmon", "trout",
                    "tuna", "haddock", "plaice", "ceviche", "anchovies", "sardine", "worcestershire sauce",
                    "calamari", "miso", "dashi", "takoyaki", "mackarel", "mackerel", "sea bass", "shark", "caviar",
                    "snapper", "sole"]
        egg_allergy_added = False
        lupin_allergy_added = False
        mustard_allergy_added = False
        tree_nuts_allergy_added = False
        tree_nuts = ["almond", "brazil", "cashew", "chestnut", "filbert", "hazelnut", "hickory", "macadamia", "pecan",
                     "pine", "pistachio", "walnut"]
        peanuts_allergy_added = False
        sesame_seeds_allergy_added = False
        soybeans_allergy_added = False

        for ingredient in ingredients:
            ing = str(ingredient).split('"')
            ingredient_list.append(ing[3])
            ingred = str(ing[3])
            print(ingred)
            c.execute(queryingredients, (int(ingredientindex), int(recipeidindex), str(ingred)))

            # dairy_free: id=1
            if "dairy-free" not in name.lower():
                for dairy in dairies:
                    if dairy_allergy_added:
                        break
                    if str(dairy) in ingred.lower():
                        c.execute(queryrecipeallergies, (int(recipeidindex), 1))
                        dairy_allergy_added = True

            # gluten_free: id=2
            if "gluten-free" not in name.lower():
                for gluten in glutens:
                    if gluten_allergy_added:
                        break
                    if str(gluten) in ingred.lower():
                        c.execute(queryrecipeallergies, (int(recipeidindex), 2))
                        gluten_allergy_added = True

            # seafood_free: id=3
            for seafood in seafoods:
                if seafood_allergy_added:
                    break
                if str(seafood) in ingred.lower():
                    c.execute(queryrecipeallergies, (int(recipeidindex), 3))
                    seafood_allergy_added = True

            # egg_free: id=4
            if ("egg" in ingred.lower()) and (egg_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 4))
                egg_allergy_added = True
            # lupin_free: id=5
            if ("lupin" in ingred) and (lupin_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 5))
                lupin_allergy_added = True
            # mustard_free: id=6
            if ("mustard" in ingred) and (mustard_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 6))
                mustard_allergy_added = True

            # tree_nuts_free: id=7
            for nut in tree_nuts:
                if tree_nuts_allergy_added:
                    break
                if str(nut) in ingred.lower():
                    c.execute(queryrecipeallergies, (int(recipeidindex), 7))
                    tree_nuts_allergy_added = True

            # peanuts_free: id=8
            if ("peanut" in ingred.lower()) and (peanuts_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 8))
                peanuts_allergy_added = True
            # sesame_seed_free: id=9
            if ("sesame" in ingred.lower()) and (sesame_seeds_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 9))
                sesame_seeds_allergy_added = True
            # soybeans_free: id=10
            if ("soy" in ingred.lower()) and (soybeans_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 10))
                soybeans_allergy_added = True
            # celery_free: id=11
            if ("celery" in ingred.lower()) and (celery_allergy_added == False):
                c.execute(queryrecipeallergies, (int(recipeidindex), 11))
                celery_allergy_added = True

            ingredientindex = ingredientindex + 1

        is_classic = False
        is_vegan = False
        is_vegetarian = False
        is_pescatarian = False

        banned_for_pescatarians = ["meat", "pork", "beef", "lamb", "kangaroo", "chicken", "turkey", "duck", "goose",
                                   "sausage", "bone", "wing", "mutton", "leg", "thigh", "belly", "quail",
                                   "ostrich", "ham", "mince", "crocodile", "dog", "cat", "horse", "lamb", "mutton",
                                   "deer", "venison", "boar", "veal", "bovrin", "steak", "chorizo", "bacon"]
        banned_for_vegetarians = seafoods

        banned_for_vegans = dairies
        banned_for_vegans.extend(
            ["egg", "dairy", "mayonnaise", "honey", "beeswax", "gelatin", "tapenade", "pesto", "carmine", "isinglass"]
        )

        ingred_list = []
        for ingredient in ingredients:
            ing = str(ingredient).split('"')
            ingred = str(ing[3])
            ingred_list.append(ingred.lower())

        if "vegan" in name.lower():
            c.execute(queryrecipediettypes, (int(recipeidindex), 4))
            is_vegan = True

        # Is classic?
        if (is_vegan is False) and (is_classic is False):
            for ingred in ingred_list:
                for item in banned_for_pescatarians:
                    if item in ingred:
                        c.execute(queryrecipediettypes, (int(recipeidindex), 1))
                        is_classic = True
                    if is_classic:
                        break  # break loop if diet type is decided
                if is_classic:
                    break

        # Is pescatarian?
        if (is_vegan is False) and (is_classic is False) and (is_pescatarian is False):
            for ingred in ingred_list:
                for item in banned_for_vegetarians:
                    if item in ingred:
                        c.execute(queryrecipediettypes, (int(recipeidindex), 2))
                        is_pescatarian = True
                    if is_pescatarian:
                        break  # break loop if diet type is decided
                if is_pescatarian:
                    break

        # Is vegetarian?
        if (is_vegan is False) and (is_classic is False) and (is_pescatarian is False) and (is_vegetarian is False):

            for ingred in ingred_list:
                for item in banned_for_vegans:
                    if item in ingred:
                        c.execute(queryrecipediettypes, (int(recipeidindex), 3))
                        is_vegetarian = True
                    if is_vegetarian:
                        break  # break for loop if diet type is decided
                if is_vegetarian:
                    break

        # If after all ingredients are checked and no diet type is assigned, then recipe is vegan
        if (is_classic is False) and (is_pescatarian is False) and (is_vegetarian is False) and (is_vegan is False):
            c.execute(queryrecipediettypes, (int(recipeidindex), 4))
            is_vegan = True

        c.execute(queryrecipes, (int(recipeidindex), str(name), file_name, why, z, y, total))

        for nut in nutrition:
            types = nut.find_all('span', class_='nutrition__label')
            values = nut.find_all('span', class_='nutrition__value')
            if len(types) == len(values):
                print(title.text + ': ' + serving.text + '-->' + times.text)
                print(ingredient_list)
                print(methodology)
                for i in range(len(types)):
                    thisvalue = (values[i].text)
                    thistype = (types[i].text)
                    nutritionalinfo.append(thisvalue + ' ' + thistype)
                    print(thisvalue + ' ' + thistype)

            else:
                print('fail!')
        methodology = []

        c1 = values[0].text
        f = values[1].text
        s = values[2].text
        c2 = values[3].text
        s1 = values[4].text
        f1 = values[5].text
        p = values[6].text
        s2 = values[7].text
        calnum = re.split('[-|g|kcal]', c1)
        fatnum = re.split('[-|g|kcal]', f)
        satnum = re.split('[-|g|kcal]', s)
        carbnum = re.split('[-|g|kcal]', c2)
        sugnum = re.split('[-|g|kcal]', s1)
        fibnum = re.split('[-|g|kcal]', f1)
        pronum = re.split('[-|g|kcal]', p)
        salnum = re.split('[-|g|kcal]', s2)
        if calnum[0] == '':
            c1 = 0
        elif calnum[0] != None:
            c1 = float(calnum[0])
        else:
            c1 = 0
        if fatnum[0] == '':
            f = 0
        elif fatnum[0] != None:
            f = float(fatnum[0])
        else:
            f = 0
        if satnum[0] == '':
            s = 0
        elif satnum[0] != None:
            s = float(satnum[0])
        else:
            s = 0
        if carbnum[0] == '':
            c2 = 0
        elif carbnum[0] != None:
            c2 = float(carbnum[0])
        else:
            c2 = 0
        if sugnum[0] == '':
            s1 = 0
        elif sugnum[0] != None:
            s1 = float(sugnum[0])
        else:
            s1 = 0
        if fibnum[0] == '':
            f1 = 0
        elif fibnum[0] != None:
            f1 = float(fibnum[0])
        else:
            f1 = 0
        if pronum[0] == '':
            p = 0
        elif pronum[0] != None:
            p = float(pronum[0])
        else:
            p = 0
        if salnum[0] == '':
            s2 = 0
        elif salnum[0] != None:
            s2 = float(salnum[0])
        else:
            s2 = 0

        c.execute(querynutrition, (int(nutritionindex), int(recipeidindex), c1, f, s, c2, s1, f1, p, s2))

        recipeidindex = recipeidindex + 1
        recipestepsindex = recipestepsindex + 1
        nutritionindex = nutritionindex + 1

        # functions below to keep track of progress

        print(
            f"\n{int(recipeidindex)} / {len(second_urls)} ({round(100 * (int(recipeidindex) / len(second_urls)), 3)}%) complete")

        current_time = time.time()

        recipes_left = len(second_urls) - int(recipeidindex)

        total_time_elapsed = round(current_time - start_time, 3)
        one_iter_time = current_time - interim_time
        eta_time_to_complete = round(one_iter_time * recipes_left, 3)

        print(f"Time elapsed: {total_time_elapsed} seconds/ {round(total_time_elapsed / 60, 3)} minutes")
        print(f"ETA: complete in {eta_time_to_complete} seconds/ {round((eta_time_to_complete / 60), 3)} minutes")
        print(
            "--------------------------------------------------------------------------------------------------------\n")

sql = '''CREATE TABLE IF NOT EXISTS `Users` (
                                    `id` integer NOT NULL AUTO_INCREMENT UNIQUE,
                                    `first_name` varchar(40) NOT NULL,
                                    `last_name` varchar(40) NOT NULL,
                                    `email` varchar(40) integer,
                                    `password` varchar(200) integer,
                                    PRIMARY KEY (`id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `UserDietPreferences` (
                                    `user_id` integer NOT NULL UNIQUE,
                                    `diet_type_id` integer NOT NULL DEFAULT 1,
                                    FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`),
                                    FOREIGN KEY (`diet_type_id`) REFERENCES `DietTypes` (`diet_type_id`),
                                    PRIMARY KEY (`user_id`, `diet_type_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `UserAllergies` (
                                    `user_id` integer NOT NULL,
                                    `allergy_id` integer NOT NULL,
                                    FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`),
                                    FOREIGN KEY (`allergy_id`) REFERENCES `Allergies` (`allergy_id`),
                                    PRIMARY KEY (`user_id`, `allergy_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `MealPlans` (
                                    `mealplan_id` integer NOT NULL UNIQUE,
                                    `user_id` integer NOT NULL,
                                    `created_at` datetime,
                                    FOREIGN KEY (`mealplan_id`) REFERENCES `MealPlans` (`mealplan_id`),
                                    FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`),
                                    PRIMARY KEY (`user_id`, `mealplan_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `MealPlanRecipes` (
                                    `mealplan_id` integer NOT NULL,
                                    `recipe_id` integer NOT NULL,
                                    `selected_servings` integer DEFAULT 2,
                                    FOREIGN KEY (`mealplan_id`) REFERENCES `MealPlans` (`mealplan_id`),
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    PRIMARY KEY (`mealplan_id`, `recipe_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS `UserFavouriteRecipes` (
                                    `user_id` integer NOT NULL,
                                    `recipe_id` integer NOT NULL,
                                    FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`),
                                    FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
                                    PRIMARY KEY (`user_id`, `recipe_id`)
                                    ) ENGINE=InnoDB'''
c.execute(sql)

# sql = '''CREATE TABLE IF NOT EXISTS `Nutrition` (
#                                     `nutrition_id` integer NOT NULL,
#                                     `nutrition_name` varchar(40) NOT NULL,
#                                     `unit` varchar(10),
#                                     PRIMARY KEY (`nutrition_id`)
#                                     ) ENGINE=InnoDB'''
# c.execute(sql)

# sql = '''CREATE TABLE IF NOT EXISTS `RecipeNutritionValues` (
#                                     `recipe_id` integer NOT NULL,
#                                     `nutrition_id` integer NOT NULL,
#                                     `nutrition_value` float NOT NULL,
#                                     FOREIGN KEY (`recipe_id`) REFERENCES `Recipes` (`recipe_id`),
#                                     FOREIGN KEY (`nutrition_id`) REFERENCES `Nutritions` (`nutrition_id`),
#                                     PRIMARY KEY (`recipe_id`, `nutrition_id`)
#                                     ) ENGINE=InnoDB'''
# c.execute(sql)



conn.commit()

c.close()
conn.close()