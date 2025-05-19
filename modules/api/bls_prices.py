from modules.api import get_prices_now
import requests
import json
import datetime
from types import SimpleNamespace
import modules.keys
bls_url_base = 'https://api.bls.gov/publicAPI/v2/timeseries/data/{id}?registrationkey='+ modules.keys.bls_api_key

class BLSData(get_prices_now.APIPriceConnection):
    #custom function to get BLS data
    def get_price_for(self, item):
        print(bls_url_base)
        resp = requests.get(bls_url_base.format(id =item))
        
        jr = json.loads(resp.text)
        
        price_points = []        
        for result in jr["Results"]["series"][0]["data"]:
            print(result)            
            ""
            date = datetime.datetime(int(result["year"]), int(result["period"][1:].lstrip('0')), 1)
            price = result["value"]
            price_points.append({"date": date, "price": price})
        return price_points
    
    def read_queries(self):
        with open('./static/bls_data_map.csv', "r") as file:
            rows = []
            for line in file:
                rows.append(line.split(','))
            
            output = {}
            #skip header
            for row in rows[1:]:
                item_name = row[0]
                bls_id = row[1]
                our_id = row[2]
                prices = self.get_price_for(bls_id)
                output[our_id] = prices[0]
        return output
    
    def get_all_prices(self):
        for o in self.read_queries():
            #CHECK IF O EXISTS IN FIREBASE: DATETIME
                #UPLOAD O to Firebase
            pass
        self.read_queries()
        

api = BLSData()