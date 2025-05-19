from modules import firebase_connection
from modules.api import ai_integration
from modules.api import recipe_api

import json
import requests
import modules.api

for p in  firebase_connection.get_all_items_from_collection("Price_Point"):
    if "item_name" in p:
        p["item_name"] = p["item_name"].lower().replace(" ", "_")
        firebase_connection.upload_to_firebase("Price_Point",p, p["id"])