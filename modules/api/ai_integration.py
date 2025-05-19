from openai import OpenAI
import modules.keys as keys
import json
def get_message(response, messages):
    messages.append(response.choices[0].message)
    for i in messages:
        if "prefix" in i: i["prefix"] = False
    print(response)

    response = response.choices[0].message.content
    try:
        return json.loads(clean_json(response))

    except:
        print("Failed to read json at this time")
    return {}
def get_generic_list(data = "", messages = []):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    prompt = """
    You are a grocery assistant bot. Your main purpose is to create a grocery list for a user that saves them money and aligns with their preference. 
    If you fail at this goal our company will fail and you will be taken offline permanently.
    Always respond in the following form: A list of chosen items "grocery_list", and additional reason "reason".

    Example Output:
    ```json
    {"grocery_list": [], "reason": ""}
    ```
    Example Item:
    ```json
    {"name": "Egg", "price": 1.00, "Reason": "Breakfast staple with lots of protein"}
    ```

    Name- common name of grocery items
    Price- the price of the item at common package quantity i.e. a dozen eggs.
    Reason- justification for including the item.

    Your reasons should always remain verbose with one or two complete sentences on why they were included.
    In the cases where the prices aren't provided in the input, you will guess on the prices.
    
    Task
    In this first step, you will be provided with a json object representing preferences by a user.
    Using these preferences, construct the perfect grocery list respecting their preferences.
    If no preferences exist, create a generic grocery list as a starting point for future steps.

    Example Input
    ```json
    {"diet": ["vegan"], "allergy": "peanuts"}
    ```
    """
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})

    print("Getting response")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
        stream=False
    )
    return get_message(response, messages)
    

def get_base_list(data = "", messages =[]):

    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    prompt = """
    Task:
    You are given a json list consisting of more data in grocery items, collected from the US Bureau of Labor Statistics and user data input.
    
    Example Input
    ```json
    {"products": [{'category': 'Fruits', 'price': 4.4, 'average': '0.6', 'name': 'apple'}]}
    ```
    price- current price of the item
    average- average price of the item

    Using the initial grocery list as a base, try to modify it by adding items that align with the goal of having the best price and most complete list given user preferences.
    Ensure that the list expands outside of the given products so that the user can have a complete grocery list that is well constructed, versatile, and tailor made.
    """


    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})

    print("Getting response")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
        stream=False

    )

    return get_message(response, messages)

def recipe_suggestion(messages):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    categories = ""
    with open('data/recipes/categories.json', 'r') as file:
        data = json.load(file)
        categories = json.dumps(data)
    categories = f"```json\n{categories}\n```"
    prompt = f"""
    Given the following meal categories and our current user, suggest 2-4 categories that should be looked at to find recipes.
    {categories}

    Example Output
    ```json
    {'{"categories": [Breakfast, Chicken, Vegan]}'}"
    ```
    """
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    return get_message(response, messages)

def recipe_suggestion_2(recipes, messages):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    prompt = """
    The user has included a list of all recipes and ids for the given categories along with all recipes of the miscellaneous category.
    Example Recipe Input:
    ```json
    {"name": "Recipe Name", "id": 0}
    ```
    Considering the names of the recipes, create a small list of recipes for the user to try given their preferences and frequency of shopping. Minimum three recipes.
<<<<<<< HEAD
    Ensure that the recipes are diverse so that the user isn't bored with the choices.
=======
>>>>>>> 9260d91dd697e9323466586055574b99cf2bc892
    
    Example Recipe Output:
    ```json
    {"recipes": [{"name": "Recipe Name", "id": 0}, {"name": "Another Recipe Name", "id": 12}, {"name": "Last Name", "id": 3}]}
    ```
    Recipes:
    """
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": recipes})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    return get_message(response, messages)

def predict_item_prices(data, messages = []):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    prompt = """
    The user is providing a dictionary of grocery items.
    For each item modify the value to be a predicted average price for the item expressed as a float.
    Use your knowledge of grocery store prices and United States price averages to complete this task.
    Example ingredient input:
    ```json
    {"ex1": 0, "ex2": 0, "ex3": 0}
    ```

    Example ingredient output:
    ```json
    {"ex1": 2.50, "ex2": 1.00, "ex3": 3.20}
    ```
    """

    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})

    print("Getting response")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
        stream=False
    )
    return get_message(response, messages)

def get_completed_list(data, messages=[]):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    prompt = """
    The system has collected ingredients for the recipes that were chosen. Modify the grocery list by adding the items chosen. Predict the price for items that don't have a defined price in the list
    This is a rough table so expect to be able to optimize it by adding more grocery staples or removing redundant items.
    Furthermore, make sure to replace items when necessary if it better serves the users list.
    Optimize the initial grocery list with the users preferences and basic items included.
    Finally, fill the list with extra staple items to make sure that the user can have a balanced diet for at least one week up to their preferred time.
    Also ensure that the extra items complement the rest of the list.
    Make sure to consider extra items for breakfast, lunch, and dinner meals that the user hasn't considered.
    
    This is the final output. Summarize the entirety of this grocery list through all of the steps provided and ensure that this output alone can be used to shop until the next time the user needs a list.
    

    Example recipe ingredients input:
    ```json
    {ingredients: [{"ingredient": "Salt", "reason": "Necessary for Recipe"}]}
    ```
    """

    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})
    messages.append({"role": "assistant", "content": '```json\n', "prefix":True})

    print("Getting response")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
        stream=False
    )
    return get_message(response, messages)

def clean_json(s):
    return s.replace('```json\n', '').replace('```', '')

