from modules.api import get_prices_now
import requests
import json
import datetime
from types import SimpleNamespace

bls_url_base = 'https://api.bls.gov/publicAPI/v2/timeseries/data/{id}'

class BLSData(get_prices_now.APIPriceConnection):
    #custom function to get BLS data
    def get_price_for(self, item):
        resp = requests.get(bls_url_base.format(id =item))
        
        jr = json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        
        print("hello"+str(jr))
        price_points = []
        for result in jr.Results:
            date = datetime.datetime(result.year, result.period[1:].ltrim('0'), 1)
            price = result.value
            price_points.append({"date": date, "price": price})
        return price_points
    
    def read_queries(self):
        with open('./static/bls_data_map.csv', "r") as file:
            rows = []
            for line in file:
                rows.append(line.split(','))
            
            #skip header
            for row in rows[1:]:
                item_name = row[0]
                bls_id = row[1]
                our_id = row[2]

                prices = self.get_price_for(bls_id)
                print(prices)
            
            

api = BLSData()