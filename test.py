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
for i in ret["meals"]:
    img = f'https://www.themealdb.com/images/ingredients/{format_name(i["strIngredient"])}.png'
    if i["strType"] == None or i["strType"] == "null":
        i["strType"] = "Misc"
    # response = requests.get(url+"ingredients/"+str(id)+".png")
    data.append({"name": format_name(i["strIngredient"]), "image": img, "category": i["strType"], "price": 0})

firebase_connection.write_multiple_objects_batch(data, "Grocery_Items")



# print("Stopping")

