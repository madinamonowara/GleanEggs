from flask import Flask, render_template, request, session, redirect, url_for
from modules.api import bls_prices
from modules import process_data
import firebase_admin
from modules import firebase_connection
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

@app.route("/preferences")
def preferences():
    return check_login(render_template("/preferences.html"))

@app.route('/bls')
def bls_data():
    #bls_prices.api.read_queries()
    prices = [1.1, 1.3, 1.5, 1.4, 1, 1.2]
    dates = [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 2, 1), datetime.datetime(2024, 3, 1), datetime.datetime(2024, 4, 1),
             datetime.datetime(2024, 5, 1), datetime.datetime(2024, 6, 1)]
    nd = []
    for d in dates:
        nd.append(time_y(d))
    return render_template('/product.html', date=dates, price=nd)

def time_y(time):
    return math.sin(time.year+time.month+time.day+datetime.datetime.now().second)
    #return (time.year-2020)*12 + time.month-1

@app.route('/create_list')
def populate_data():
    grocery_list = process_data.generate_grocery_list()
    return render_template('/grocery_list.html', items=grocery_list)

@app.route('/recipes')
def recipes():
    return check_login(render_template('/recipes.html'))

@app.route('/charts')
def populate():
    return render_template('/charts.html')

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


if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)
