import requests
import pprint
from bs4 import BeautifulSoup
import re
import urllib3
import sqlite3
from sqlite3 import Error
import random

db = sqlite3.connect("mealtime.sqlite")
c = db.cursor()

WeeklyCalorieCount = []
desiredcount = 24500
meal = 0
maxcooktime = 60
WeeklyCalorieCount.append(meal)
CalorieLimit = []
CalorieLimit.append(desiredcount)
i=0
shoppinglist = []
recipeids = []

while WeeklyCalorieCount[i] <= desiredcount:

    querystem = """SELECT DISTINCT r.recipeID
    FROM Recipes r
             JOIN NutritionValues nut ON r.RecipeID = nut.RecipeID
    WHERE nut.Calories <= (?) AND nut.Calories != 0
    ORDER BY RANDOM() LIMIT 1"""

    titlequerystem = """SELECT DISTINCT r.Recipe_name
    FROM Recipes r
    WHERE r.RecipeID = ?"""

    caloriequerystem = """SELECT DISTINCT nut.Calories
    FROM NutritionValues nut
             JOIN Recipes r ON nut.RecipeID = r.RecipeID
    WHERE r.RecipeID = ?"""

    servingsizequerystem = """SELECT DISTINCT r.Recipe_serves
        FROM Recipes r
        WHERE r.RecipeID = ?"""

    ingredientquerystem = """SELECT DISTINCT ing.IngredientString
    FROM main.RecipeIngredients ing
             JOIN Recipes r ON ing.RecipeID = r.RecipeID
    WHERE r.RecipeID = ?"""

    recipe = c.execute(querystem, ([CalorieLimit[i]]))
    recipe = c.fetchall()
    print(recipe)

    service = []
    c.execute(caloriequerystem, recipe[0])
    calories = c.fetchall()
    c.execute(servingsizequerystem, recipe[0])
    serves = c.fetchone()
    serves = serves[0]
    for cal in calories:
        cally = (int(cal[0]))
        cally = cally*serves
        print(cally)

    WeeklyCalorieCount.append(WeeklyCalorieCount[i]+cally)
    CalorieLimit.append(desiredcount-WeeklyCalorieCount[i])

    andthen = c.execute(titlequerystem, recipe[0])
    for n in andthen:
        print(n[0])
        print(calories[0])
        answer = input("Do you want it?")
        if answer == "y":
            pass
            recipeids.append(recipe)
        if answer == "n":
            recipe = c.execute(querystem, ([CalorieLimit[i]]))
            recipe = c.fetchall()
            c.execute(caloriequerystem, recipe[0])
            calories = c.fetchall()
            andthen = c.execute(titlequerystem, recipe[0])

    i=i+1


    for r in recipe:
        ingredients = c.execute(ingredientquerystem, r)
        for ingredient in ingredients:
            #print(ingredient)
            shoppinglist.append(ingredient)

print(shoppinglist)
print(recipeids)