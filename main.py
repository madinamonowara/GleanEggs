from flask import Flask, render_template
from modules.api import bls_prices
from modules import process_data
import firebase_admin
import datetime
import math
try:
    import keys
except:
    print('NO KEYS DETECTED')
    exit()

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('/index.html')

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

if __name__ == '__main__':
    app.run(debug=True)