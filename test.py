from modules import firebase_connection
from modules.api import ai_integration
from modules.api import recipe_api

import json
import requests
import modules.api

def format_name(s):
    return s.lower().replace(" ", "_")
response = requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list")

ret = json.loads(response.text)
data = []
item_names = {}
n_item_names = {}

with open("test.json", "r") as file:
    item_names = json.load(file)
print(item_names)
for i in ret["meals"]:
    img = f'https://www.themealdb.com/images/ingredients/{format_name(i["strIngredient"])}.png'
    price = 0
    if format_name(i["strIngredient"]) in item_names:
        price = item_names[format_name(i["strIngredient"])]
    if i["strType"] == None or i["strType"] == "null":
        i["strType"] = "Misc"
    # response = requests.get(url+"ingredients/"+str(id)+".png")
    data.append({"name": format_name(i["strIngredient"]), "image": img, "category": i["strType"], "price": price, "average": price})

firebase_connection.write_multiple_objects_batch(data, "Grocery_Items")



# print("Stopping")

