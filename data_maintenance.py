#USING THIS CLASS TO CREATE PROCEDURES IMPORTANT FOR MAINTENANCE OF APPLICATION
import sys
from modules.api import bls_prices
from modules import firebase_connection
from modules.api import recipe_api
import datetime

def weekly_check():
    # if datetime.date.today().weekday != 6: return
    for p in firebase_connection.get_all_tracked_items():
        print(p)
        get_product(p["name"])
        if "bls" in p:
            prices = bls_prices.api.get_price_for(p["bls"].strip())
            
            for pi in prices:
                id = f"bls_{p['name'].lower().replace(' ', '_')}_{pi['date'].isoformat()}"
                price_point = {
                    "item_name": p["name"],
                    "price": pi["price"],
                    "date": str(pi["date"].date()),
                    "timestamp": pi["date"].isoformat(),
                    "type": "bls"
                }
                firebase_connection.upload_to_firebase("Price_Point", price_point, id)

    

# if __name__ == "__main__":
#     if sys.argv[1] == "weekly_check":
#         weekly_check()

def get_product(name):
    formatted_name = name.lower().replace(" ", "_")
    price_history = firebase_connection.get_price_history_by_item(formatted_name)
    item =  firebase_connection.get_node("Grocery_Items", formatted_name)
    if not item:
        print(name)
        quit()
        return
    
    # dates = [entry["date"] for entry in price_history]
    # prices = [entry["price"] for entry in price_history]
    last_verified = 0.00
    d_dict = {}
    for entry in price_history:
        print(entry)
        if not entry["date"] in d_dict:
            d_dict[entry["date"]] = []
        d_dict[entry["date"]].append(float(entry["price"]))
        if entry["type"] != "user":
            last_verified = entry["price"]
        if last_verified:
            for i in range(15):
                d_dict[entry["date"]].append(float(last_verified))
    dates = d_dict.keys()
    prices = [sum(d_dict[k])/len(d_dict[k]) for k in d_dict.keys()]
    history = [list(item) for item in zip(dates, prices)]
    price = 0.0
    if item:
        price = item["price"]
        print(price)
    if "name" in item:
        item["name"] = item["name"].capitalize().replace("_", " ")
    if len(history) == 0:
        return
    item["average"] = item["average"] if len(prices) <= 0 else sum(prices)/max(len(prices), 1)
    item["price"] = item["price"] if len(prices) <= 0 else prices[-1]
    firebase_connection.upload_to_firebase("Grocery_Items",item, name.lower().replace(" ", "_"))

weekly_check()        