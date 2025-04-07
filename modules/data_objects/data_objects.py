class ItemObject:
    def __init__(self, item_name, item_id, price, trend, weekly_diff):
        self.item_name = item_name
        self.item_id = item_id
        self.price = price
        self.trend = trend
        self.weekly_diff = weekly_diff

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "item_id": self.item_id,
            "price": self.price,
            "trend": self.trend,
            "weekly_diff": self.weekly_diff
        }

class Price:
    def __init__(self, item_id, value, source, datetime):
        self.item_id = item_id
        self.value = value
        self.source = source
        self.datetime = datetime

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "value": self.value,
            "source": self.source,
            "datetime": self.datetime
        } 

class Account:
    def __init__(self, user_id, preferences):
        self.user_id = user_id
        self.preferences = preferences

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "preferences": self.preferences
        }

class groceryList:
    def __init__(self, user_id, items):
        self.user_id = user_id
        self.items = items

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "items": self.items
        }
