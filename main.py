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

@app.route('/')
def hello():
    return render_template('/index.html')

if __name__ == '__main__':
    app.secret_key = 'SECRET KEY'
    app.run(debug=True)

