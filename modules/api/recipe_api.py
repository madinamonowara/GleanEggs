import requests
import json
import datetime
from types import SimpleNamespace
import modules.keys as keys
import modules.firebase_connection as firebase_connection
import random

mealdb_url = 'https://www.themealdb.com/api/json/v1/'
def get_base_url():
    return mealdb_url+keys.mealdb_key+"/"

def get_recipe(id):
    response = requests.get(get_base_url()+"lookup.php?i="+str(id))
    return json.loads(response.text)

def get_thumbnail(id):
    url = 'https://www.themealdb.com/images/'
    response = requests.get(url+"ingredients/"+str(id)+".png")
    # remove last character
    print(str(response.status_code)+id)
    if response.status_code == 200: return url+"ingredients/"+str(id)+".png"
    response = requests.get(url+"ingredients/"+str(id[0:-2])+".png")
    if response.status_code == 200: return url+"ingredients/"+str(id[0:-2])+".png"

    item = firebase_connection.get_node("Grocery_Items", id)
    if item and 'img' in item: return item['img']
    
    return "https://www.avasflowers.net/blog/wp-content/uploads/2019/03/The-History-Behind-The-Thanksgiving-Cornucopia.jpg"

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
                ingredients.append([ing, 0, "Necessary for "+r[1]])
    print("ingredients:\n"+str(ingredients))
    return ingredients