import requests

# Replace this with your own API key from TheSportsDB
API_KEY = "3"

# Function to fetch live football scores
def get_football_scores():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/liveevents.php"
    response = requests.get(url)
    data = response.json()
    
    if data['events']:
        match = data['events'][0]  # Fetch the first match (you can loop through for more matches)
        match_info = f"{match['strHomeTeam']} vs {match['strAwayTeam']} - Status: {match['strStatus']}"
        return match_info
    else:
        return "No live football matches available at the moment."

# Function to fetch live cricket scores
def get_cricket_scores_db():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/cricketmatches.php"
    response = requests.get(url)
    data = response.json()
    
    if data['matches']:
        match = data['matches'][0]  # Fetch the first cricket match (you can loop for more)
        match_info = f"{match['strTeam1']} vs {match['strTeam2']} - Status: {match['strStatus']}"
        return match_info
    else:
        return "No live cricket matches available at the moment."

# Function to interact with the user and display live scores
def provide_sports_info():
    sport_choice = input("Which sport would you like information about? (football/cricket): ").lower()
    
    if sport_choice == "football":
        print("Fetching live football scores...")
        football_info = get_football_scores()
        print(f"Latest football match: {football_info}")
    elif sport_choice == "cricket":
        print("Fetching live cricket scores...")
        cricket_info = get_cricket_scores_db()
        print(f"Latest cricket match: {cricket_info}")
    else:
        print("Sorry, I don't have information for that sport.")

# Main function to run your bot
def main():
    while True:
        user_input = input("How can I help you? ").lower()
        
        if "sports" in user_input or "score" in user_input:
            provide_sports_info()
        elif "exit" in user_input:
            break
        else:
            print("Sorry, I didn't understand that.")

if __name__ == "__main__":
    main()
