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

def generate_grocery_list():
        data = compile_start_list(firebase_connection.get_all_tracked_items())
        
        suggested_list = ai_integration.get_base_list(data)
        recipes = recipe_api.get_recipes_for_items(suggested_list)
        recipe_ingredients = recipe_api.get_recipe_ingredients(recipes)
        rough_list = []
        
        print("ROUGH LIST")
        for s in suggested_list:
            rough_list.append(s)
        
        for i in recipe_ingredients:
            rough_list.append(i)
        
        rl_data = compile_rough_list(rough_list)
        full_list = ai_integration.get_completed_list(rl_data)
        print("FULL LIST")
        
        for f in full_list:
            print(f)
        return [full_list, recipes]
