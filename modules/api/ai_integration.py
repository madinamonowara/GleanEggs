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


def generate_single_item_description_json(item_display_name: str, user_preferences_json_string: str = "{}", existing_messages_for_ai_context=None):
    """
    Generates an AI description for a single grocery item and aims to return it 
    in a JSON structure {"description": "text..."} compatible with the existing get_message function.

    Args:
        item_display_name (str): The display name of the item (e.g., "Olive Oil").
        user_preferences_json_string (str): A JSON string of user preferences for context. Defaults to "{}".
        existing_messages_for_ai_context (list, optional): Not typically used for a fresh, single-item query.
                                                            Kept for signature consistency if needed, but usually None.

    Returns:
        dict: A dictionary parsed by get_message, hopefully like {"description": "AI generated text..."},
              or {"description": None} or an empty dict {} on failure.
    """
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com/beta")
    
    # For a single, targeted description, it's often best to craft a fresh message list.
    messages = []

    system_prompt = """
You are a helpful grocery assistant. Your task is to provide a concise and useful 1-2 line description 
or common use case for the single grocery item provided by the user. This description will be shown 
to the user in their grocery list.
If user preferences are provided, consider them for context if they are relevant to describing the item's use.
You MUST respond with ONLY a JSON object containing a single key "description" with the generated text as its value.
Do not include any other text, explanations, or markdown formatting outside of the JSON object.

Example of your ONLY valid output format:
```json
{"description": "A versatile cooking oil, great for salads and light frying."}
```
"""
    messages.append({"role": "system", "content": system_prompt})
    
    user_content = f"Grocery Item: '{item_display_name}'"
    if user_preferences_json_string and user_preferences_json_string != "{}":
        try:
            # Validate and pretty print preferences for the prompt if they are valid JSON
            prefs_dict = json.loads(user_preferences_json_string)
            user_content += f"\nUser Preferences (for context, if relevant): {json.dumps(prefs_dict, indent=2)}"
        except json.JSONDecodeError:
            print(f"Warning: Could not parse user_preferences_json_string for AI prompt: {user_preferences_json_string}")
            # Optionally, you could pass the raw string if parsing fails, or omit it.
            # user_content += f"\nUser Preferences (raw): {user_preferences_json_string}"
            pass # Or omit preferences if they are not valid JSON

    messages.append({"role": "user", "content": user_content})
    
    # Your get_message function appends the AI's response to 'messages' and also
    # appends an assistant prefix '```json\n' before the call.
    # We will pass a copy of messages to get_message if it modifies the list,
    # or if the prefix logic is handled there.
    # For this specific call, we want the AI to *produce* the ```json block.
    # The `get_message` function expects the AI response to be JSON, and `clean_json` handles the ```.

    print(f"AI Request for single item description. Item: '{item_display_name}'. Messages being prepared for AI: {messages}")
    
    # Create a messages list specifically for this call, as get_message might modify it.
    # Your get_message also adds an assistant prefix, which is good.
    messages_for_this_call = messages.copy()
    # Add the assistant prefix that your get_message function expects the AI to complete
    # This is crucial if your get_message and clean_json rely on it.
    messages_for_this_call.append({"role": "assistant", "content": '```json\n', "prefix": True})


    try:
        ai_response_object = client.chat.completions.create(
            model="deepseek-chat", # Or your preferred model
            messages=messages_for_this_call, # Use the specifically prepared messages
            stop=["```"], # Crucial to stop the AI after the JSON block
            max_tokens=100, # Max length for a short description + JSON overhead
            temperature=0.6 # Adjust for creativity vs. factuality
        )
        # Use your existing get_message to parse the response.
        # get_message will append the AI's actual response to messages_for_this_call
        # and then try to parse it.
        parsed_response = get_message(ai_response_object, messages_for_this_call)
        
        if isinstance(parsed_response, dict) and "description" in parsed_response:
            if parsed_response["description"] is None or not str(parsed_response["description"]).strip():
                print(f"AI returned an empty or null description for '{item_display_name}'.")
                return {"description": None} # Explicitly return None for description
            return parsed_response # Should be {"description": "text..."}
        else:
            print(f"AI response for '{item_display_name}' was not in the expected format (missing 'description' key or not a dict). Response: {parsed_response}")
            return {"description": None} # Indicate failure to get a valid description
            
    except Exception as e:
        print(f"Error calling AI for single item description for '{item_display_name}': {e}")
        return {"description": None} # Return a dict with None to indicate failure gracefully