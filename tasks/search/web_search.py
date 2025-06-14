import webbrowser

def google_search(query):
    print(f"Searching Google for: {query}")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
