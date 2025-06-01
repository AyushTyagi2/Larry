import requests

def find_places(city_name):
    API_KEY = "AIzaSyB0uzvLo7l9Z9GJcTM7j-SHJwXEJtHFlso"  # Replace with your Google Places API key
    BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Prepare the search query
    query = f"tourist attractions in {city_name}"
    
    # Set up parameters for the API call
    params = {
        'query': query,
        'key': API_KEY
    }

    # Make the API call
    response = requests.get(BASE_URL, params=params)
    
    # Parse the response
    data = response.json()
    
    if data['status'] == 'OK':
        # List the top 5 tourist places
        print(f"Top tourist attractions in {city_name}:")
        for place in data['results'][:5]:
            name = place['name']
            address = place.get('formatted_address', 'Address not available')
            print(f"- {name}: {address}")
    else:
        print("No results found or error occurred. Please check the city name and try again.")
