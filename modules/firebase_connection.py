import os
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import firebase_admin
# from firebase_admin import auth
from firebase_admin import credentials, firestore
from modules.keys import FIREBASE_CREDENTIALS_PATH  

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
else:
    print("Firebase app already initialized")

db = firestore.client()

def test_firebase_connection():
    try:
        print("Setting test document...")
        test_ref = db.collection("test_collection").document("test_doc")
        test_ref.set({"hello": "world"})
        
        doc = test_ref.get()
        if doc.exists:
            print("Firebase Connection Test:", doc.to_dict())
            return True
        else:
            print("Test document not found!")
            return False
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False


def upload_to_firebase(collection_name, data_dict, doc_id=None):

    try:
        if doc_id:
            db.collection(collection_name).document(str(doc_id)).set(data_dict)
        else:
            db.collection(collection_name).add(data_dict)
        print(f"Data uploaded to {collection_name} successfully!")
    except Exception as e:
        print(f"Error uploading to {collection_name}: {str(e)}")

def get_node(collection, node_id, alias_check = True):
    try:
        print("trying to get")
        doc = db.collection(collection).document(str(node_id)).get()
        print("got")
        if doc.exists:
            check = doc.to_dict()
            if "alias" in check and alias_check:
                print(check["alias"])
                return get_node(collection, check["alias"], False)
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error retrieving {node_id} for {collection}: {str(e)}")
        return None
    

def create_user(email, password, name=None):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        return user.uid
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None

def get_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
    
def get_user_preferences(user_id):
    print(user_id)
    try:
        doc = db.collection("preferences").document(str(user_id)).get()
        print(doc)
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error retrieving preferences for {user_id}: {str(e)}")
        return None

print("HELLO?")
def get_prices(name, date):
    collection_name = "price_points"
    try:
        docs = db.collection(collection_name).where("date", ">", date).where("item_id", "=", name).stream()
        items = [doc.to_dict() for doc in docs]
        return items
    except Exception as e:
        print(f"Error retrieving items from {collection_name}: {str(e)}")
        return []
   

def get_all_items_from_collection(collection_name):
   
    try:
        docs = db.collection(collection_name).stream()
        items = []
        for doc in docs:
            dt = doc.to_dict()
            dt["id"] = doc.id
            items.append(dt)
        # items = [doc.to_dict() for doc in docs]
        return items
    except Exception as e:
        print(f"Error retrieving items from {collection_name}: {str(e)}")
        return []

def get_all_tracked_items():
    try:
        items = get_all_items_from_collection("Grocery_Items")
        return items
    except Exception as e:
        print(e)
        return []

def add_item_by_category(name, price, diff, trend, category):
    data = {
        "name": name,
        "price": price,
        "diff": diff,
        "trend": trend,
        "category": category
    }
    upload_to_firebase("Grocery_Items", data_dict=data, doc_id=name.lower())


def get_items_by_category(category_name):
    try:
        docs = db.collection("Grocery_Items").where("category", "==", category_name).stream()
        
        items = [doc.to_dict() for doc in docs]
        return items
    except Exception as e:
        print(f"Error retrieving items by category '{category_name}': {str(e)}")
        return []
    
def save_user_preferences(user_id, preferences):
    try:
        db.collection("users").document(str(user_id)).set({
            "preferences": preferences
        }, merge=True)
        print(f"Preferences saved for user {user_id}")
        return True
    except Exception as e:
        print(f"Error saving preferences for {user_id}: {str(e)}")
        return False


def add_product_price_and_store(price, store_name):
    try:
        data = {
            "price": price,  
            "store_name": store_name,  
            "timestamp": firestore.SERVER_TIMESTAMP  
        }
        
        upload_to_firebase("Store_Prices", data_dict=data)
        print("Product price and store name successfully uploaded!")
    
    except Exception as e:
        print(f"Error uploading product price and store name: {str(e)}")

def get_price_history_by_item(item_name):
    try:
        collection_name = "Price_Point"
        docs = db.collection(collection_name).where("item_name", "==", item_name).order_by("date").stream()

        price_history = [{"date": doc.to_dict()["date"], "price": doc.to_dict()["price"], "type": doc.to_dict()["type"]} for doc in docs]
        
        return price_history
    except Exception as e:
        print(f"Error retrieving price history for item '{item_name}': {str(e)}")
        return []
    

def add_to_grocery_list(user_email, item_name):
    try:
        user_doc = db.collection("groceryLists").document(user_email).get()
        if user_doc.exists:
            data = user_doc.to_dict()
            items = data.get("items", [])
            prices = data.get("prices", [])
            reasons = data.get("reason", [])
        else:
            items, prices, reasons = [], [], []
        item_name = item_name.replace("_", " ").title()
        if item_name in items:
            print(f"{item_name} already in grocery list")
            return False

        item_data = get_node("Grocery_Items", item_name.lower().replace(" ","_"))
        if not item_data:
            print(f"{item_name} not found in Grocery_Items")
            return False
        
        items.append(item_name)
        prices.append(item_data["price"])
        reasons.append("user added")

        db.collection("groceryLists").document(user_email).set({
            "items": items,
            "prices": prices,
            "reason": reasons
        }, merge=True)
        print(f"{item_name} added to {user_email}'s grocery list")
        return True

    except Exception as e:
        print(f"Error adding to grocery list: {str(e)}")
        return False


def remove_from_grocery_list(user_email, item_name):
    try:
        user_doc = db.collection("groceryLists").document(user_email).get()
        if not user_doc.exists:
            print(f"No grocery list found for {user_email}")
            return False
        
        data = user_doc.to_dict()
        items = data.get("items", [])
        prices = data.get("prices", [])
        reasons = data.get("reason", [])
        item_name = item_name.capitalize().replace("_", " ")

        if not item_name.replace("_", " ").title() in items:
            print(f"{item_name} not found in list")
            return False

        index = items.index(item_name)
        items.pop(index)
        prices.pop(index)
        reasons.pop(index)

        db.collection("groceryLists").document(user_email).set({
            "items": items,
            "prices": prices,
            "reason": reasons
        }, merge=True)
        print(f"{item_name} removed from grocery list")
        return True

    except Exception as e:
        print(f"Error removing from grocery list: {str(e)}")
        return False



if __name__ == "__main__":
    print("Running Firebase test connection...")
 
    if test_firebase_connection():
        print("Firebase is connected and operational!")
    else:
        print("There was an issue with the Firebase connection.")

    sample_data = {"item_name": "Broccoli", "price": 2.49, "category": "Vegetable"}
    upload_to_firebase("items", sample_data)


    user_preferences = get_user_preferences("user_1")
    if user_preferences:
        print("User Preferences:", user_preferences)

    
    all_items = get_all_items_from_collection("items")
    print("All Items in 'items' Collection:", all_items)


    print("\nAdding new grocery item with category...")
    add_item_by_category(
        name="carrot",
        price="1.29",
        diff="-0.05",
        trend="0.102",
        category="Vegetable"
    )




def write_multiple_objects_batch(data_list, collection_name):
    """Writes multiple objects to Firestore using a batched write."""
    batch = db.batch()
    for data in data_list:
        doc_ref = db.collection(collection_name).document(data["name"])  # Automatically generate unique IDs
        batch.set(doc_ref, data)
    batch.commit()
    print(f"Successfully wrote {len(data_list)} objects using batched write.")