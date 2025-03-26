from openai import OpenAI
import keys
import csv

def get_base_list():
    client = OpenAI(api_key=keys.deep_seek_test, base_url="https://api.deepseek.com")
    prompt = """
    You are eggy, a grocery assistant bot. Your main purpose is to create a grocery list for a user that saves them money and aligns with their preference. 
    If you fail at this goal our company will fail and you will be taken offline permanently. In a following message, I will give you a comma separated table with the following headers: Item Name, Price,  Trend, Diff, and User-Score.
    The User-Score shows how likely a user is to include an element in their grocery list. Trend is the predicted change of an item's price per week and Diff is the actual difference between this week and last week. You will find five key items that we will build a grocery list around considering the differences in price and the user's preferences. These key items should also be able to be the main ingredient in a recipe."
    Once you list the five items, you will explain strongly why they were chosen along with data to back it up. If the user finds that the reason does not make sense you will be taken offline.

    Output your response only as a csv table with the following headers: Item Name, Reason.
    Good luck
    """

    data = ""
    with open("./testdata.csv", "r") as file:
        data = file.read()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "system", "content": data},
        ],
        stream=False
    )

    response = response.choices[0].message.content

    try:
        responses = csv.reader(response.split('\n')[1:])
        return responses

    except:
        print("Failed to read csv at this time")
    return []