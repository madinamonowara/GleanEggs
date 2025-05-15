from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from modules.api import bls_prices
from modules import process_data
from modules import firebase_connection
from modules.api import recipe_api

import json
import datetime
import math
try:
    import modules.keys as keys
except:
    print('NO KEYS DETECTED')
    exit()

app = Flask(__name__)

def get_session_value(key):
    if not key in session: return ""
    else: return session[key]

@app.route('/login')
def login():
    session["token"] = ""
    session['email'] = ""
    session['name'] = ""
    return render_template('/login.html')

def check_login(location):
    print("HERE")
    if get_session_value("token") != "":
        return location
    else:
        return redirect(url_for("login"))

@app.route('/return')
def login_return():
    session['token'] =  request.args.get("id")
    session['email'] =  request.args.get("email")
    session['name'] =  request.args.get("name")
    return redirect(url_for("home"))

@app.route("/home")
@app.route("/")
def home():
    if not logged_in(): return redirect(url_for("login"))
    list = firebase_connection.get_node("groceryLists", session['email'])
    if not list: return check_login(render_template("/home.html", name=get_session_value("name")))
    grocery_list = []
    for i in range(len(list["items"])):
        grocery_list.append({
            "product": list["items"][i],
            "name": list["items"][i].capitalize().replace("_", " "),
            "price": list["prices"][i],
            "reason": list["reason"][i],
            "img":  recipe_api.get_thumbnail(list["items"][i])
        })
    return check_login(render_template("/home.html", name=get_session_value("name"), list=grocery_list))

def logged_in():
    return 'token' in session

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        user_id = firebase_connection.create_user(email, password, name)

        if user_id:

            firebase_connection.upload_to_firebase("users", {"preferences": {}}, doc_id=email)

            session['token'] = user_id
            session['email'] = email
            session['name'] = name
            return redirect(url_for('home'))
        else:
            return render_template('signup.html', error="Signup failed. Try again.")

    return render_template('signup.html')


@app.route("/preferences", methods=['GET', 'POST'])
def preferences():
    if not logged_in(): return redirect(url_for("home"))
    prefs = firebase_connection.get_node('preferences', session['email'])
    if not prefs: return check_login(render_template("/preferences.html", preferences={}))
    preferences = {}
    for j in prefs:
        preferences[j+"_"+prefs[j]] = "checked"
    if "budget" in prefs: preferences["budget"] = prefs['budget']
    print(preferences)
    return check_login(render_template("/preferences.html", preferences=preferences))

@app.route("/save_preferences", methods=['POST'])
def save_preferences():
    if request.method != 'POST': return ""
    if not logged_in(): return ""

    preferences = {
        "diet": request.form['diet'],
        "allergy": request.form['allergy'],
        "shop": request.form['shop-frequency'],
        "budget": request.form['budget']
    }
    firebase_connection.upload_to_firebase("preferences", preferences, session['email'])
    return 'Data retrieved successfully!'

@app.route("/generate_list", methods=['GET'])
def generate_list():
    if not logged_in(): return "Failure"

    email = session['email']
    returned_list = process_data.generate_grocery_list(email)
    grocery_list = {"items": [], "prices": [], "reason": [], "recipes": [i[0] for i in returned_list[1]]}
    
    for i in returned_list[0]:
        if len(i) != 3: continue
        if "*" in i[0]: continue
        grocery_list["items"].append(i[0])
        grocery_list["prices"].append(i[1])
        grocery_list["reason"].append(i[2])
    
    firebase_connection.upload_to_firebase("groceryLists", grocery_list, email)
    return "Success"

    
def time_y(time):
    return math.sin(time.year+time.month+time.day+datetime.datetime.now().second)
    #return (time.year-2020)*12 + time.month-1

# @app.route('/create_list')
# def populate_data():
#     grocery_list = process_data.generate_grocery_list()
#     return render_template('/grocery_list.html', items=grocery_list)

@app.route('/recipes')
def recipes():
    if not logged_in(): return redirect(url_for("home"))
    
    list = firebase_connection.get_node("groceryLists", session['email'])
    if not list:  return redirect(url_for("home"))
    recipes = []
    for id in list["recipes"]:
        response = recipe_api.get_recipe(id)
        meal = response["meals"][0]
        recipes.append({
            "id": id,
            "image": meal["strMealThumb"],
            "name": meal["strMeal"],
            "area":meal["strArea"],
            "category":meal["strCategory"]
        })



    return check_login(render_template('/recipes.html', recipes=recipes))

@app.route('/product_list')
def product_list():
    if not logged_in(): return redirect(url_for("home"))
    return check_login(render_template('/product_list.html', recipes=recipes))

@app.route('/product')
def products():
    if not logged_in(): return redirect(url_for("home"))
    return check_login(render_template('/product.html', recipes=recipes))


@app.route('/recipe')
def recipe():
    id = request.args.get('id')
    response = recipe_api.get_recipe(id)
    recipe = response["meals"][0]
    recipe["items"] = []
    for i in range(1,21):
        if ("strIngredient"+str(i)) in recipe:
            if recipe['strIngredient'+str(i)] == '': break
            recipe["items"].append({"ingredient": recipe["strIngredient"+str(i)], "measure": recipe["strMeasure"+str(i)]})
        else:  break
    print(recipe)
    return check_login(render_template('/recipe.html', recipe=recipe))

@app.route('/charts', methods=['GET', 'POST'])
def charts():
    if request.method == 'POST':
        price = request.form['price']
        store_name = request.form['store_name']

        add_product_price_and_store(price, store_name)

        return redirect(url_for('charts'))

    return render_template('charts.html')

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        category = request.form['category'] 
        items = firebase_connection.get_items_by_category(category)  

        if items:
            return render_template('/search_results.html', items=items, category=category)  
        else:
            return render_template('/search_results.html', items=[], category=category)  
    return render_template('/search.html')  



@app.route('/product_data', methods=['GET'])
def product_data():
    names = request.args.getlist('name')  
    products = []

    for name in names:
        formatted_name = name.lower().replace(" ", "_")
        price_history = firebase_connection.get_price_history_by_item(formatted_name)

    dates = [entry["date"].strftime("%Y-%m-%d") for entry in price_history]
    prices = [entry["price"] for entry in price_history]
    history = [list(item) for item in zip(dates, prices)]
    item =  firebase_connection.get_node("Grocery_Items", name)
    price = 0.0
    if item:
        price = item["price"]
    product = {"history": history, "lastWeekPrice": 0, "thisWeekPrice": price, "image": recipe_api.get_thumbnail(name)}
    products = [product1, product2]
    return json.dumps(product)

# changed to allow user's inputted price to show in products after being changed
@app.route('/get_products', methods=['GET'])
def get_products():
    returns = firebase_connection.get_all_items_from_collection("Grocery_Items")

    item = []
    for p in returns:
        name = p["name"]
        displayName = name.capitalize().replace("_", " ")
        image = recipe_api.get_thumbnail(name)
        category = p.get("category", "")
        price = p["price"]

        # Check in-store prices
        price_doc = firebase_connection.get_node("in_store_prices", name)
        in_store_price = None
        if price_doc:
            try:
                latest_timestamp = max(price_doc)
                in_store_price = price_doc[latest_timestamp]
            except:
                pass

        item.append({
            "name": name,
            "displayName": displayName,
            "image": image,
            "price": price,
            "category": category,
            "in_store_price": in_store_price
        })

    return json.dumps({"products": item})

# for user to add their own price in product
@app.route('/submit_instore_price', methods=['POST'])
def submit_instore_price():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')

    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    from datetime import datetime
    timestamp = datetime.now().isoformat()

    # This assumes upload_to_firebase supports merge=True for updating a nested dict
    firebase_connection.upload_to_firebase(
        "in_store_prices",
        {timestamp: price},
        doc_id=name,
        merge=True
    )

    return jsonify({"success": True}), 200


# for comparing products when user is in products list page (dummy info for now included)
@app.route('/compare')
def compare():
    selected_names = request.args.getlist('name')

    # Temporary dummy data for now
    dummy_db = {
        "apple": {
            "displayName": "Apple",
            "image": "/static/images/apple.png",
            "price": 1.99,
            "price_dates": ["Apr 1", "Apr 8", "Apr 15", "Apr 22", "Apr 29", "May 6", "May 13"],
            "price_values": [1.89, 1.92, 2.05, 2.10, 2.00, 1.99, 1.99]
        },
        "banana": {
            "displayName": "Banana",
            "image": "/static/images/banana.png",
            "price": 0.69,
            "price_dates": ["Apr 1", "Apr 8", "Apr 15", "Apr 22", "Apr 29", "May 6", "May 13"],
            "price_values": [0.60, 0.65, 0.68, 0.70, 0.69, 0.69, 0.69]
        },
        "milk": {
            "displayName": "Milk",
            "image": "/static/images/milk.png",
            "price": 3.49,
            "price_dates": ["Apr 1", "Apr 8", "Apr 15", "Apr 22", "Apr 29", "May 6", "May 13"],
            "price_values": [3.59, 3.55, 3.50, 3.49, 3.49, 3.49, 3.49]
        }
    }

    products = []
    for name in selected_names:
        if name in dummy_db:
            d = dummy_db[name]
            products.append({
                'name': name,
                'displayName': d['displayName'],
                'image': d['image'],
                'current_price': d['price'],
                'price_history': {
                    'dates': d['price_dates'],
                    'values': d['price_values']
                }
            })
        else:
            products.append({
                'name': name,
                'displayName': name.capitalize(),
                'image': '/static/images/placeholder.png',
                'current_price': 0.00,
                'price_history': {
                    'dates': ["N/A"],
                    'values': [0]
                }
            })

    return render_template("compare.html", products=products)



if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)
