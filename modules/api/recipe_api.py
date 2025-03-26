import requests
import json
import datetime
from types import SimpleNamespace
import keys
import random

mealdb_url = 'www.themealdb.com/api/json/v1/'
def get_base_url():
    return mealdb_url+mealdb_key+"/"

def get_recipes_for_items(items, num_items = 3):
    recipes = []
    for i in items:
        url = get_base_url()+"filter.php?i="+i[0]
        response_raw = requests.get(url)
        response = json.loads(response_raw.text)
        for r in response:
            recipes.append(r)

    while recipes.size() > num_items:
        r = int(random.random() * len(recipes))
        recipes.remove(recipes[r])

    return recipes