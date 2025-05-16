import requests
import json
import io

def get_category(category):
    response = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}")
    r_js = json.loads(response.text)
    output = {}
    for i in r_js["meals"]:
        output[i["strMeal"]] = i["idMeal"]
    with open(f"data/recipes/{category.lower()}_recipes.json", "w") as file:
        file.write(json.dumps(output))
    # json.dumps(output)

response = requests.get(f"https://www.themealdb.com/api/json/v1/1/categories.php")
js = json.loads(response.text)
output = {"categories":[]}
for i in js["categories"]:
    output["categories"].append(i["strCategory"])
    get_category(i["strCategory"])

with open(f"data/recipes/categories.json", "w") as file:
        file.write(json.dumps(output))