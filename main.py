from flask import Flask, render_template, request, session, redirect, url_for
from modules.api import bls_prices
from modules import process_data
from modules import firebase_connection
from modules.api import recipe_api

import datetime
import math
try:
    import keys
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

@app.route("/")
def home():
    return check_login(render_template("/home.html", name=get_session_value("name")))

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
    if not logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get('email')
    
    if request.method == 'POST':
        preferences = {
            "diet": {
                "vegan": "vegan" in request.form.getlist("diet"),
                "vegetarian": "vegetarian" in request.form.getlist("diet"),
                "glutenfree": "glutenfree" in request.form.getlist("diet"),
                "keto": "keto" in request.form.getlist("diet")
            },
            "allergies": {
                "peanuts": "peanuts" in request.form.getlist("allergy"),
                "dairy": "dairy" in request.form.getlist("allergy"),
                "soy": "soy" in request.form.getlist("allergy"),
                "shellfish": "shellfish" in request.form.getlist("allergy")
            },
            "shopping": {
                "frequency": request.form.get("shop-frequency"),
                "budget": request.form.get("budget", "10")
            }
        }
        
        firebase_connection.save_user_preferences(user_id, preferences)
        return redirect(url_for("home"))
    

    existing_prefs = firebase_connection.get_user_preferences(user_id)

    template_prefs = {

        "diet_vegan_checked": "checked" if existing_prefs.get("diet", {}).get("vegan") else "",
        "diet_vegetarian_checked": "checked" if existing_prefs.get("diet", {}).get("vegetarian") else "",
        "diet_glutenfree_checked": "checked" if existing_prefs.get("diet", {}).get("glutenfree") else "",
        "diet_keto_checked": "checked" if existing_prefs.get("diet", {}).get("keto") else "",

        "allergy_peanuts_checked": "checked" if existing_prefs.get("allergies", {}).get("peanuts") else "",
        "allergy_dairy_checked": "checked" if existing_prefs.get("allergies", {}).get("dairy") else "",
        "allergy_soy_checked": "checked" if existing_prefs.get("allergies", {}).get("soy") else "",
        "allergy_shellfish_checked": "checked" if existing_prefs.get("allergies", {}).get("shellfish") else "",

        "freq_1x_checked": "checked" if existing_prefs.get("shopping", {}).get("frequency") == "1x" else "",
        "freq_2x_checked": "checked" if existing_prefs.get("shopping", {}).get("frequency") == "2x" else "",
        "freq_biweekly_checked": "checked" if existing_prefs.get("shopping", {}).get("frequency") == "biweekly" else "",
        "freq_monthly_checked": "checked" if existing_prefs.get("shopping", {}).get("frequency") == "monthly" else "",
        
        "budget_value": existing_prefs.get("shopping", {}).get("budget", "10")
    }
    
    return render_template("preferences.html", **template_prefs)



def time_y(time):
    return math.sin(time.year+time.month+time.day+datetime.datetime.now().second)
    #return (time.year-2020)*12 + time.month-1

@app.route('/create_list')
def populate_data():
    grocery_list = process_data.generate_grocery_list()
    return render_template('/grocery_list.html', items=grocery_list)

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

@app.route('/product/<item_name>', methods=['GET'])
def product(item_name):
    price_history = firebase_connection.get_price_history_by_item(item_name)

    if not price_history:
        return redirect(url_for('home'))

    dates = [entry["date"].strftime("%Y-%m-%d") for entry in price_history]
    prices = [entry["price"] for entry in price_history]

    return render_template('product.html', item_name=item_name, price_history=zip(dates, prices))



if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)
