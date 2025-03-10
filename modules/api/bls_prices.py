from get_prices_now import APIPriceConnection

class BLSData(APIPriceConnection):
    #custom function to get BLS data
    def get_price_for(self, item):
        return super().get_price_for()