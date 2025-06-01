# tasks/knowledge/wikipedia.py
import requests
import textwrap

def search_wikipedia(query, max_results=5):
    try:
        # First get search results
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results
        }
        
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()
        
        if "query" in search_data and "search" in search_data["query"]:
            results = search_data["query"]["search"]
            
            if not results:
                print(f"No Wikipedia articles found for '{query}'")
                return None
            
            print(f"\nWikipedia results for '{query}':")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
            
            # Ask which article to view
            choice = input("\nEnter the number of the article to view (or 0 to cancel): ")
            
            try:
                choice = int(choice)
                if choice == 0:
                    return None
                
                if 1 <= choice <= len(results):
                    article_title = results[choice-1]["title"]
                    return get_wikipedia_summary(article_title)
                else:
                    print("Invalid selection.")
                    return None
            except ValueError:
                print("Please enter a valid number.")
                return None
        else:
            print(f"Could not perform Wikipedia search for '{query}'")
            return None
            
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return None

def get_wikipedia_summary(title):
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        page_id = list(data["query"]["pages"].keys())[0]
        
        if page_id == "-1":
            print(f"No Wikipedia article found for '{title}'")
            return None
        
        extract = data["query"]["pages"][page_id]["extract"]
        
        print(f"\n=== {title} ===\n")
        
        # Format and print the text nicely with wrapping
        wrapper = textwrap.TextWrapper(width=80)
        paragraphs = extract.split("\n")
        
        for paragraph in paragraphs:
            if paragraph.strip():
                print(wrapper.fill(paragraph))
                print()
        
        print(f"Read more: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
        
        return extract
            
    except Exception as e:
        print(f"Error fetching Wikipedia summary: {e}")
        return None