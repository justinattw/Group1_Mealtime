import requests
import pprint
from bs4 import BeautifulSoup
import re
import urllib3
import sqlite3
from sqlite3 import Error

db = sqlite3.connect("mealtime.sqlite", isolation_level=None)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS Recipes (
                                        recipe_id integer unique NOT NULL,
                                        recipe_name varchar(40) NOT NULL,
                                        photo varchar(40),
                                        serves integer,
                                        cook_time integer,
                                        prep_time integer,
                                        total_time integer,
                                        PRIMARY KEY (recipe_id)
                                        );""")

# TODO: Add amount and unit to recipe ingredients
c.execute("""CREATE TABLE IF NOT EXISTS RecipeIngredients (
                                        recipe_ingredient_id integer unique NOT NULL,
                                        recipe_id integer NOT NULL,
                                        ingredient varchar(40),
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        PRIMARY KEY (recipe_ingredient_id)
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS NutritionValues (
                                        nutrition_value_id integer,
                                        recipe_id integer NOT NULL,
                                        calories float, 
                                        fats float,
                                        saturates float,
                                        carbs float,
                                        sugars float,
                                        fibres float,
                                        proteins float,
                                        salts float,
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        PRIMARY KEY (nutrition_value_id)
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS RecipeInstructions (
                                        recipe_instruction_id integer NOT NULL,
                                        recipe_id integer NOT NULL,
                                        step_num integer NOT NULL,
                                        step_description varchar(40) NOT NULL,
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        PRIMARY KEY (recipe_instruction_id, step_num)
                                        );""")

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

    queryrecipes = "insert into Recipes values (?, ?, ?, ?, ?, ?, ?)"
    queryingredients = "insert into RecipeIngredients values (?, ?, ?)"
    querynutrition = "insert into NutritionValues values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    queryinstructions = "insert into RecipeInstructions values (?, ?, ?, ?)"

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

    for ingredient in ingredients:
        ing = str(ingredient).split('"')
        ingredient_list.append(ing[3])
        ingred = str(ing[3])
        print(ingred)
        c.execute(queryingredients, (int(ingredientindex), int(recipeidindex), str(ingred)))
        ingredientindex = ingredientindex + 1

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
    for item in plz:
        if item.isdigit():
            why = float(item)
    print(why)
    c.execute(queryrecipes, (int(recipeidindex), str(name), "", why, z, y, total))

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

print(nutritionalinfo)

# Ingredients is working


# method is mostly working (except for multiple links in methods)

c.execute("""CREATE TABLE IF NOT EXISTS Users (
                                        id integer unique NOT NULL,
                                        first_name varchar(40) NOT NULL,
                                        last_name varchar(40) NOT NULL,
                                        email varchar(40) NOT NULL,
                                        password varchar(40) NOT NULL,
                                        PRIMARY KEY (id)
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS DietTypes (
                                        diet_type_id integer unique NOT NULL,
                                        diet_name varchar(40),
                                        PRIMARY KEY (diet_type_id)
                                        );""")

sql = "INSERT INTO DietTypes (diet_type_id, diet_name) VALUES (?, ?)"
values = [(1, 'classic'),
          (2, 'pescatarian'),
          (3, 'vegetarian'),
          (4, 'vegan')]
c.executemany(sql, values)

c.execute("""CREATE TABLE IF NOT EXISTS UserDietPreferences (
                                        user_id integer NOT NULL,
                                        diet_type_id integer NOT NULL default 1,
                                        FOREIGN KEY (user_id) References Users (id),
                                        FOREIGN KEY (diet_type_id) References DietTypes (diet_type_id),
                                        PRIMARY KEY (user_id, diet_type_id)
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS Allergies (
                                        allergy_id integer unique NOT NULL,
                                        allergy_name varchar(40) NOT NULL,
                                        PRIMARY KEY (allergy_id)
                                        );""")

sql = "INSERT INTO Allergies (allergy_id, allergy_name) VALUES (?, ?)"
values = [(1, 'celery_free'),
          (2, 'gluten_free'),
          (3, 'seafood_free'),
          (4, 'eggs_free'),
          (5, 'lupin_free'),
          (6, 'mustard_free'),
          (7, 'tree_nuts_free'),
          (8, 'peanuts_free'),
          (9, 'sesame_seeds_free'),
          (10, 'soybeans_free'),
          (11, 'sulphur_sulphites_free')]
c.executemany(sql, values)

c.execute("""CREATE TABLE IF NOT EXISTS UserAllergies (
                                        user_id integer NOT NULL,
                                        allergy_id integer NOT NULL,
                                        FOREIGN KEY (user_id) References Users (id),
                                        FOREIGN KEY (allergy_id) References Allergies (allergy_id), 
                                        PRIMARY KEY (user_id, allergy_id)
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS MealPlans (
                                        mealplan_id integer unique NOT NULL,
                                        user_id integer NOT NULL,
                                        created_at varchar(40),
                                        FOREIGN KEY (user_id) References Users (id),
                                        PRIMARY KEY (mealplan_id) 
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS MealPlanRecipes (
                                        mealplan_id integer NOT NULL,
                                        recipe_id integer NOT NULL,
                                        selected_servings integer default 2,
                                        FOREIGN KEY (mealplan_id) References MealPlans (mealplan_id),
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        PRIMARY KEY (mealplan_id, recipe_id) 
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS RecipeDietTypes (
                                        recipe_id integer NOT NULL UNIQUE,
                                        diet_type_id integer NOT NULL,
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        FOREIGN KEY (diet_type_id) References DietTypes (diet_type_id),
                                        PRIMARY KEY (recipe_id, diet_type_id) 
                                        );""")

c.execute("""CREATE TABLE IF NOT EXISTS RecipeAllergies (
                                        recipe_id integer NOT NULL,
                                        allergy_id integer NOT NULL,
                                        FOREIGN KEY (recipe_id) References Recipes (recipe_id),
                                        FOREIGN KEY (allergy_id) References Allergies (allergy_id),
                                        PRIMARY KEY (recipe_id, allergy_id) 
                                        );""")

# c.execute("""CREATE TABLE IF NOT EXISTS Nutrition (
#                                         nutrition_id integer NOT NULL PRIMARY KEY,
#                                         nutrition_name varchar(40),
#                                         unit varchar(10)
#                                         );""")

# c.execute("""CREATE TABLE IF NOT EXISTS RecipeNutritionValues (
#                                         recipe_id integer NOT NULL PRIMARY KEY,
#                                         nutrition id integer NOT NULL PRIMARY KEY,
#                                         nutrition_value float NOT NULL
#                                         FOREIGN KEY recipe_id References Recipes (recipe_id),
#                                         FOREIGN KEY allergy_id References Allergies (allergy_id)
#                                         );""")

db.commit

db.close()
