import requests

def get_weather(city):
    # Make the request to the wttr.in API
    url = f"https://wttr.in/{city}?format=3"  # Simple weather output format
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        print(f"Weather in {city}: {response.text}")
    else:
        print("Sorry, I couldn't fetch the weather right now. Please try again later.")
