import requests

# Function to fetch live cricket scores using CricAPI
def get_cricket_scores():
    # Replace 'YOUR_API_KEY' with your actual API key from CricAPI
    api_key = "a7794743-47ce-44e5-a6b9-9ce7c3270920"
    url = f"https://cricapi.com/api/matches?apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    if data.get("matches"):
        # Extract the first match's details (you can modify it for more matches)
        match = data["matches"][0]
        match_info = f"{match['team1']} vs {match['team2']} - Status: {match['status']}"
        return match_info
    else:
        return "No live cricket matches available at the moment."

# Function to interact with the user
def provide_cricket_info():
    print("Fetching live cricket scores...")
    cricket_info = get_cricket_scores()
    print(f"Latest match: {cricket_info}")

# Example usage in your bot
def main():
    while True:
        user_input = input("How can I help you? ").lower()
        
        if "cricket" in user_input:
            provide_cricket_info()
        elif "exit" in user_input:
            break
        else:
            print("Sorry, I didn't understand that.")

if __name__ == "__main__":
    main()
