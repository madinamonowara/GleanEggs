from api.bls_prices import BLSData
from data_objects import grocery_items
from api import ai_integration
from api import recipe_api
import firebase_connection
#Main pipe and filter methods

blsapi = BLSData()
apis = []

def item_sort(a, b):
    if a[1] < b[1]:
        return -1
    elif a[1] > b[1]:
        return 1
    return 0


#Mainly using the user account but we may include different parameters in the future
def generate_grocery_list(account, recipes, special_parameters)->list:
    item_arr = firebase_connection.get_all_tracked_items()
    
    sorted_list = []
    for i in item_arr:
        sorted_list.append((i, grocery_items.calculate_score(i, account)))
    
    sorted_list.sort(item_sort)

    grocery_list = sorted_list[0:account.get_items()]

    return grocery_list

def generate_recipes():
    g_list = generate_grocery_list()
    recipes = get_rec