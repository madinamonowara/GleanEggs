#from api.bls_prices import BLSData
from modules.data_objects import grocery_items
from modules.api import ai_integration
from modules.api import recipe_api
from modules import firebase_connection
import csv
import io

#2D-array to string containing a csv list for AI processing data
def compile_rough_list(rough_list):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Reason"])
        for r in rough_list:
            writer.writerow(r)
        return output.getvalue()

def generate_grocery_list():
        data = firebase_connection.get_all_tracked_items()
        suggested_list = ai_integration.get_base_list(data)
        #suggested_list = [["chicken", ""], ["rice", ""], ["eggs", ""], ["avocado", ""] , ["chickpeas", ""]]
        
        recipes = recipe_api.get_recipes_for_items(suggested_list)
        recipe_ingredients = recipe_api.get_recipe_ingredients(recipes)
        rough_list = []
        print("ROUGH LIST")
        for s in suggested_list:
            print(s)
            rough_list.append(s)
        for i in recipe_ingredients:
            print(i)
            rough_list.append(i)
        
        rl_data = compile_rough_list(rough_list)
        full_list = ai_integration.get_completed_list(rl_data)
        
        print("FULL LIST")
        for f in full_list:
            print(f)
        return full_list

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
               firebase_connection.upload_to_firebase("products", )

def check_list():
     pass