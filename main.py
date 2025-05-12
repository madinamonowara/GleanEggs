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
    returned_list = process_data.generate_grocery_list()
    grocery_list = {"items": [], "prices": [], "reason": [], "recipes": [i[0] for i in returned_list[1]]}
    
    for i in returned_list[0]:
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

        item = firebase_connection.get_node("Grocery_Items", formatted_name)
        price = item["price"] if item else 0.0

        product = {
            "name": name,
            "history": history,
            "lastWeekPrice": 0,
            "thisWeekPrice": price,
            "image": recipe_api.get_thumbnail(formatted_name)
        }

        products.append(product)

    return jsonify(products)



@app.route('/get_products', methods=['GET'])
def get_products():
    returns = firebase_connection.get_all_items_from_collection("Grocery_Items")

    item = []
    for p in returns:
        item.append({"name": p["name"], "displayName":   p["name"].capitalize().replace("_", " "), "image": recipe_api.get_thumbnail(p["name"]) , "price": p["price"],"category":p["category"]})
    output = {"products": item}
    return json.dumps(output)


if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)
