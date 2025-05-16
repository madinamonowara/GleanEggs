#from api.bls_prices import BLSData
from modules.data_objects import grocery_items
from modules.api import ai_integration
from modules.api import recipe_api
from modules import firebase_connection
import csv
import io
import json

#2D-array to string containing a csv list for AI processing data
def compile_rough_list(rough_list):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Price", "Reason"])
        for r in rough_list:
            writer.writerow(r)
        return output.getvalue()

def compile_start_list(li):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Price", "Diff", "Trend", "Score"])
        for l in li:
            writer.writerow(l)
        return output.getvalue()

def complile_preferences(preferences):
    s = ""
    for p in preferences:
        s += p+": "+preferences[p]+"\n"
    return s
     
def generate_grocery_list(user):
        messages = []
        print("Starting")
        preferences = json.dumps(firebase_connection.get_user_preferences(user))
        products = json.dumps({"products": firebase_connection.get_all_tracked_items()})
        c_products = []
        for p in products:
            if "price"in p:
                c_products.append(p)
        grocery_list = ai_integration.get_generic_list(f"```json\n{preferences}\n```", messages)
        grocery_list = ai_integration.get_base_list(f"```json\n{c_products}\n```", messages)
        category_output = ai_integration.recipe_suggestion(messages)
        all_recipes = {}
        for i in category_output["categories"]:
            with open(f"data/recipes/{i.lower()}_recipes.json", "r") as file:
                recipe_list = json.load(file)
                for r in recipe_list:
                    all_recipes[r] = recipe_list[r]

        with open(f"data/recipes/miscellaneous_recipes.json", "r") as file:
            recipe_list = json.load(file)
            for r in recipe_list:
                all_recipes[r] = recipe_list[r]

        recipe_list_f ={"recipes": [{"name": i, "id": all_recipes[i]} for i in all_recipes]}
        recipes = ai_integration.recipe_suggestion_2(f"```json\n{json.dumps(recipe_list_f)}\n```", messages)
        recipe_ingredients = recipe_api.get_recipe_ingredients(recipes)
        ingredients_j = json.dumps(recipe_ingredients)

        grocery_list = ai_integration.get_completed_list(ingredients_j, messages)
        print(grocery_list)
        print(recipes)
        return [grocery_list, recipes]

def default_product_record(data):
     product = {"price": data["price"],
                "trend": 0,
                "diff": 0,
                "name": data["name"]}
     return default_product_record()

def upload_prices_to_api(list):
     for l in list:
          item = firebase_connection.get_node("products", l)
          if not item:
               firebase_connection.upload_to_firebase("products")

def check_list():
     pass