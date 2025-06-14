# Enhanced implementation for tasks/context/context_manager.py

import json
import os
import datetime
from collections import deque
import re

# Maximum number of context items to store
MAX_CONTEXT_SIZE = 100

# File to store context between sessions
CONTEXT_FILE = "context_history.json"

# In-memory context storage
context_history = deque(maxlen=MAX_CONTEXT_SIZE)

def initialize_context():
    """Initialize the context manager, loading previous context if available"""
    global context_history
    
    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, 'r') as f:
                saved_context = json.load(f)
                # Convert to deque with maxlen
                context_history = deque(saved_context[-MAX_CONTEXT_SIZE:], maxlen=MAX_CONTEXT_SIZE)
            print(f"Loaded {len(context_history)} context items from previous sessions")
        except Exception as e:
            print(f"Error loading context: {e}")
            context_history = deque(maxlen=MAX_CONTEXT_SIZE)
    else:
        context_history = deque(maxlen=MAX_CONTEXT_SIZE)
    
    # Add session start marker
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context_history.append({"text": f"New session started", "timestamp": timestamp, "type": "system"})

def save_context():
    """Save context to persistent storage"""
    try:
        with open(CONTEXT_FILE, 'w') as f:
            json.dump(list(context_history), f)
    except Exception as e:
        print(f"Error saving context: {e}")

def update_context(text, context_type="general"):
    """
    Add new information to the context history
    
    Args:
        text (str): The text to add to context
        context_type (str): Type of context - can be 'user', 'system', 'email', 'task', etc.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create context item with metadata
    context_item = {
        "text": text,
        "timestamp": timestamp,
        "type": context_type
    }
    
    # Determine additional metadata based on content
    if "user:" in text.lower():
        context_item["type"] = "user_input"
    elif "assistant response:" in text.lower():
        context_item["type"] = "assistant_response"
    elif "error" in text.lower():
        context_item["type"] = "error"
    
    # Detect topics in the text
    topics = detect_context_topics(text)
    if topics:
        context_item["topics"] = topics
    
    # Add to history
    context_history.append(context_item)
    
    # Save periodically (every 10 items)
    if len(context_history) % 10 == 0:
        save_context()

def get_context(limit=5, context_type=None):
    """
    Get recent context entries
    
    Args:
        limit (int): Maximum number of context items to return
        context_type (str, optional): Filter by context type
        
    Returns:
        list: List of context texts (not the full objects)
    """
    if context_type:
        filtered = [item["text"] for item in list(context_history) if item["type"] == context_type]
        return filtered[-limit:]
    else:
        return [item["text"] for item in list(context_history)][-limit:]

def get_related_context(query, max_items=5):
    """
    Find context related to the query
    
    Args:
        query (str): The query to find related context for
        max_items (int): Maximum number of items to return
        
    Returns:
        list: List of related context texts
    """
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Get query words for matching (ignore common words)
    stopwords = ["the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "of", "and", "or"]
    query_words = [w for w in query_lower.split() if w not in stopwords and len(w) > 2]
    
    # Find relevant items based on text content
    scores = []
    for i, item in enumerate(context_history):
        item_text = item["text"].lower()
        
        # Calculate relevance score
        score = 0
        
        # Exact phrase matching
        if query_lower in item_text:
            score += 10
        
        # Word matching
        for word in query_words:
            if word in item_text:
                score += 2
                
                # Bonus for word appearing in topics
                if "topics" in item and word in [t.lower() for t in item["topics"]]:
                    score += 3
        
        # Context type matching
        if query_lower in item.get("type", ""):
            score += 5
        
        # Recent items get a small boost
        recency_boost = max(0, 1 - (len(context_history) - i) / len(context_history))
        score += recency_boost
        
        if score > 0:
            scores.append((score, item["text"]))
    
    # Sort by score and return text
    scores.sort(reverse=True)
    return [text for _, text in scores[:max_items]]

def clear_context():
    """Clear the context history"""
    global context_history
    context_history.clear()
    save_context()

def detect_context_topics(text):
    """
    Detect potential topics in a context entry
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: List of detected topics
    """
    topics = []
    
    # Topic detection patterns
    topic_patterns = {
        "email": r"email|gmail|message|send|recipient|subject|body",
        "weather": r"weather|temperature|forecast|rain|sunny|cloud",
        "task": r"task|todo|to do|to-do|reminder|complete",
        "event": r"event|calendar|meeting|appointment|schedule",
        "file": r"file|document|folder|directory|search file|rename|move",
        "note": r"note|memo|write down|remember",
        "search": r"search|google|find information|look up",
        "password": r"password|secure|login|credential",
        "translate": r"translate|language|english|spanish|french",
        "pdf": r"pdf|document|merge|extract|rotate",
        "preference": r"prefer|like|want|don't want|choose"
    }
    
    # Check for matches
    text_lower = text.lower()
    for topic_name, pattern in topic_patterns.items():
        if re.search(pattern, text_lower):
            topics.append(topic_name)
    
    return topics

# Initialize context when module is imported
initialize_context()