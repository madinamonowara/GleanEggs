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
    print("TRY")
    print(logged_in())
    if not logged_in(): return redirect(url_for("login"))
    print("here")
    list = firebase_connection.get_node("groceryLists", session['email'])
    print(list)
    if not list: return check_login(render_template("/home.html", name=get_session_value("name")))
    grocery_list = []
    all_images = {}
    for i in firebase_connection.get_all_tracked_items():
        all_images[i["name"]] = i
    print(all_images)
    for i in range(len(list["items"])):
        list["items"][i] = list["items"][i].lower().replace(" ", "_")
        img = all_images[list["items"][i]]["image"] if list["items"][i] in all_images else recipe_api.get_thumbnail(list["items"][i])
        grocery_list.append({
            "product": list["items"][i],
            "name": list["items"][i].capitalize().replace("_", " "),
            "price": list["prices"][i],
            "reason": list["reason"][i],
            "img":  img})
    return check_login(render_template("/home.html", name=get_session_value("name"), list=grocery_list, reason=list["full_reason"]))

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

    
    preferences = request.form
    firebase_connection.upload_to_firebase("preferences", preferences, session['email'])
    return 'Data retrieved successfully!'

@app.route("/generate_list", methods=['GET'])
def generate_list():
    if not logged_in(): return "Failure"

    email = session['email']
    returned_list = process_data.generate_grocery_list(email)
    returned_list[0] = {k.lower(): v for k, v in returned_list[0].items()}
    grocery_list = {"items": [], "prices": [], "reason": [], "recipes": [i['id'] for i in returned_list[1]['recipes']], "full_reason": returned_list[0]['reason']}
    
    for i in returned_list[0]["grocery_list"]:
        # if "*" in i[0]: continue
        grocery_list["items"].append(i["name"])
        grocery_list["prices"].append(i['price'])
        grocery_list["reason"].append(i['Reason'])
    
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
            recipe["items"].append({"ingredient": recipe["strIngredient"+str(i)], "measure": recipe["strMeasure"+str(i)], "name": recipe["strIngredient"+str(i)].lower().replace(" ", "_")})
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
    name = request.args.get('name')  
    print("HERE")
    return json.dumps(get_product(name))
    # for name in names:

def get_product(name):
    formatted_name = name.lower().replace(" ", "_")
    price_history = firebase_connection.get_price_history_by_item(formatted_name)
    
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
            last_verified = float(entry["price"])
        if last_verified:
            for i in range(15):
                d_dict[entry["date"]].append(last_verified)
    dates = d_dict.keys()
    prices = [sum(d_dict[k])/len(d_dict[k]) for k in d_dict.keys()]
    history = [list(item) for item in zip(dates, prices)]
    item =  firebase_connection.get_node("Grocery_Items", name)
    price = 0.0
    if item:
        price = item["price"]
        print(price)
    if "name" in item:
        item["name"] = item["name"].capitalize().replace("_", " ")
    if len(history) == 0:
        history.append([0,0])
    if not "image" in item:
        item["image"] = recipe_api.get_thumbnail(item["name"])
    avg = item["average"] if len(prices) <= 0 else sum(prices)/max(len(prices), 1)
    price = item["price"] if len(prices) <= 0 else prices[-1]
    product = {"history": history, "averagePrice": float(avg), "currentPrice": float(price), "image": item["image"], "name": item["name"]}
    # products = [product1, product2]
    return product

# changed to allow user's inputted price to show in products after being changed
@app.route('/get_products', methods=['GET'])
def get_products():
    returns = firebase_connection.get_all_tracked_items()
    print("Call?")
    item = []
    for p in returns:
        if not "price" in p:
            p["price"] = 0
        if not "image" in p:
            p["image"] = recipe_api.get_thumbnail(p["name"])
        if not "average" in p:
            p["average"] = p["price"]
        item.append({"name": p["name"], "displayName":   p["name"].capitalize().replace("_", " "), "image": p["image"], "price": p["price"],"category":p["category"] ,"average":p["average"]})
    output = {"products": item}
    print(f"ITEMS: {len(output['products'])}")
    return json.dumps(output)

    #     # Check in-store prices
    #     price_doc = firebase_connection.get_node("in_store_prices", name)
    #     in_store_price = None
    #     if price_doc:
    #         try:
    #             latest_timestamp = max(price_doc)
    #             in_store_price = price_doc[latest_timestamp]
    #         except:
    #             pass

    #     item.append({
    #         "name": name,
    #         "displayName": displayName,
    #         "image": image,
    #         "price": price,
    #         "category": category,
    #         "in_store_price": in_store_price
    #     })

    # return json.dumps({"products": item})

# for user to add their own price in product
@app.route('/submit_instore_price', methods=['POST'])
def submit_instore_price():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    print(data)

    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    from datetime import datetime
    timestamp = datetime.now().isoformat()

    # This assumes upload_to_firebase supports merge=True for updating a nested dict
    firebase_connection.upload_to_firebase(
        f"Price_Point",
        {"timestamp": timestamp, "price": price, "type": "user", "item_name": name, "date": str(datetime.now().date())},
        doc_id=f"user_{timestamp}"
    )

    return jsonify({"success": True}), 200


# for comparing products when user is in products list page (dummy info for now included)
@app.route('/compare')
def compare():
    selected_names = request.args.getlist('name')
    dummy_db = {}
    products = []
    for n in selected_names:
        products.append(get_product(n))

    return render_template("compare.html", products=products)


# for linking product page to ingredients in a recipe
@app.route('/api/products')
def get_product_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Missing name"}), 400

    formatted_name = name.lower().replace(" ", "_")
    item = firebase_connection.get_node("Grocery_Items", formatted_name)

    if not item:
        return jsonify({"error": f"Product '{name}' not found"}), 404

    # Fallback if no price history exists
    price_history = firebase_connection.get_price_history_by_item(formatted_name) or []
    prices = [entry["price"] for entry in price_history]
    last_price = prices[-2] if len(prices) > 1 else item.get("price", 0.0)
    this_price = prices[-1] if prices else item.get("price", 0.0)

    product = {
        "name": name,
        "image": recipe_api.get_thumbnail(formatted_name),
        "lastWeekPrice": last_price,
        "thisWeekPrice": this_price,
        "history": prices[-7:] if prices else [this_price] * 7
    }

    return jsonify(product)


if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)
