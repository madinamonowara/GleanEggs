import modules.firebase_connection
# User Accounts for our app
#
#
class Account:
    # Our defined item_id, price adjusted for weight, unix_timestamp
    def __init__(self, name, preferences):
        self.name = name
        self.preferences = preferences    
        pass