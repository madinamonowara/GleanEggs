import requests
import json
import datetime
from types import SimpleNamespace
import keys
import random

mealdb_url = 'https://www.themealdb.com/api/json/v1/'
def get_base_url():
    return mealdb_url+keys.mealdb_key+"/"

def get_recipe(id):
    response = requests.get(get_base_url()+"lookup.php?i="+str(id))
    return json.loads(response.text)

def get_recipes_for_items(items, num_items = 3):
    recipes = []
    for i in items:
        url = get_base_url()+"filter.php?i="+i[0]
        print(url)
        response_raw = requests.get(url)
        response = json.loads(response_raw.text)
        try:
            for r in response["meals"]:
                recipes.append([r["idMeal"], r["strMeal"]])
        except:
            continue
        
    print(recipes)
    while len(recipes) > num_items:
        r = int(random.random() * len(recipes))
        recipes.remove(recipes[r])

    return recipes

def get_recipe_ingredients(recipes):
    ingredients = []
    ing_tracker= []
    for r in recipes:
        url = get_base_url()+"lookup.php?i="+r[0]
        response_raw = requests.get(url)
        response = json.loads(response_raw.text)
        for i in range(1, 20):
            ing = response["meals"][0]["strIngredient"+str(i)]
            if (ing == '' or ing == None): continue
            if not(ing in ing_tracker):
                ing_tracker.append(ing)
                ingredients.append([ing, "Necessary for "+r[1]])
    print("ingredients:\n"+str(ingredients))
    return ingredients