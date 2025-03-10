<<<<<<< HEAD
from modules import firebase_connection
import datetime

def calculate_score(item, account):
    score = 1.0
    #given user preferences and pricing data calculate score using different weights
    return score

BLS_WEIGHT  = 100

def calculate_price(item):
    prices = firebase_connection.get_prices(item, "0")
    count = 0
    price_counter = 0.0
    if not prices:
        return 0.0
    for p in prices:
        weight = 1 if p["source"] != "bls" else BLS_WEIGHT
        count += weight
        price_counter = p["price"] * weight
    
    avg_price = price_counter/float(count)
    return avg_price

        
=======
def calculate_score(item, account):
    score = 1.0
    #given user preferences and pricing data calculate score using different weights
    return score
>>>>>>> 23c49e2 (Initial commit)
