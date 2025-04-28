import os
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, firestore
from keys import FIREBASE_CREDENTIALS_PATH  

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

def get_user_preferences(user_id):
  
    try:
        doc = db.collection("users").document(str(user_id)).get()
        if doc.exists:
            return doc.to_dict().get("preferences")
        return None
    except Exception as e:
        print(f"Error retrieving preferences for {user_id}: {str(e)}")
        return None

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
        items = [doc.to_dict() for doc in docs]
        return items
    except Exception as e:
        print(f"Error retrieving items from {collection_name}: {str(e)}")
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

def get_user_preferences(user_id):
    try:
        doc = db.collection("users").document(str(user_id)).get()
        if doc.exists:
            return doc.to_dict().get("preferences", {})
        return {}
    except Exception as e:
        print(f"Error retrieving preferences for {user_id}: {str(e)}")
        return {}



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




