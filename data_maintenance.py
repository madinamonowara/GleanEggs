#USING THIS CLASS TO CREATE PROCEDURES IMPORTANT FOR MAINTENANCE OF APPLICATION
import sys
from modules.api import bls_prices
import datetime

def weekly_check():
    if datetime.date.today().weekday == 6:
        bls_prices.api.get_all_prices()
    else:
        print("Incorrect day, can not run.")

if __name__ == "__main__":
    if sys.argv[1] == "weekly_check":
        weekly_check()
