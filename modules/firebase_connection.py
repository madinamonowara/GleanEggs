import firebase_admin

def get_all_tracked_items():
    data = ""
    with open("./testdata.csv", "r") as file:
        data = file.read()
    return data