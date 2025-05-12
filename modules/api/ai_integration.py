from openai import OpenAI
import modules.keys as keys
import csv

def get_generic_list(data = "", messages = []):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com")
    prompt = """
    You are Eggy, a grocery assistant bot. Your main purpose is to create a grocery list for a user that saves them money and aligns with their preference. 
    If you fail at this goal our company will fail and you will be taken offline permanently. Your responses will always only be in the form of a csv with the following headers.
    Item Name, Price, Reason.
    Your reasons should always remain verbose with one or two complete sentences on why they were included. In the case where the prices aren't provided in the input, you will guess on the prices.
    In this first step, you will be provided with a list of preferences by a user. Using these preferences, construct the perfect grocery list respecting their preferences.
    If none exist, create a generic grocery list as a starting point for future steps.
    Maintain justifications and reasoning in the reason column for each individual item.
    """
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    messages.append(response.choices[0].message)
    
    response = response.choices[0].message.content
    try:
        responses = csv.reader(response.split('\n')[2:-1])
        return list(responses)

    except:
        print("Failed to read csv at this time")
    return []

def get_base_list(data = "", messages =[]):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com")
    prompt = """
    The user will give you a comma separated table with the following headers: Item Name, Price,  Trend, Diff, and User-Score.
    The User-Score shows how likely a user is to include an element in their grocery list. Trend is the predicted change of an item's price per week and Diff is the actual difference between this week and last week. You will find five key items that we will build a grocery list around considering the differences in price and the user's preferences. These key items should also be able to be the main ingredient in a recipe."
    Once you list the five items, you will explain strongly why they were chosen along with data to back it up. If the user finds that the reason does not make sense you will be taken offline.
    Output your response only as a csv table with the following headers: Item Name, Price, Reason.
    """


    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    messages.append(response.choices[0].message)
    response = response.choices[0].message.content

    try:
        responses = csv.reader(response.split('\n')[2:-1])
        return list(responses)

    except:
        print("Failed to read csv at this time")
    return []

def get_completed_list(data, messages = []):
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com")
    prompt = """
    In a following message, the user will give you a comma separated table with the following headers: Item Name, Price, Reason.
    In cases where the price is 0, you will predict the price for an item.
    This is a rough table so expect to be able to optimize it by adding more grocery staples or removing redundant items.
    Optimize the initial grocery list with the users preferences and basic items included.
    Finally, fill the list with extra staple items to make sure that the user can have a balanced diet for at least one week up to their preferred time.
    Also ensure that the extra items complement the rest of the list.
    Make sure to add lots of extra items for breakfast, lunch, and dinner meals that the user hasn't consider.
    Provide fulfilling complete reasons about why the items were included as well as the role the item provides in the list. Also make sure the reasons are personal to why they work for the user.
    Make sure reasons have 1-3 full sentences to ensure that you sound thoughtful and fun.


    You must optimize this table and output in csv format with the headers: Item Name, Price, Reason.
    """

    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": data})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    messages.append(response.choices[0].message)
    response = response.choices[0].message.content


    try:
        responses = csv.reader(response.split('\n')[2:-1])
        return list(responses)

    except:
        print("Failed to read csv at this time")
    return []