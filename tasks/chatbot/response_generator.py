def get_response(user_input, context=None):
    """
    Generate a response to user input, optionally using context
    
    Args:
        user_input (str): The user's input text
        context (list, optional): List of context strings to consider
        
    Returns:
        tuple: (response_text, context_used)
    """
    
    # Initialize response and context tracking
    response = ""
    context_used = None
    
    # Prevent the current input from being treated as context
    if context:
        # Filter out any context that is exactly the current input
        context = [ctx for ctx in context if not (user_input in ctx and ctx.startswith("User:"))]
    
    # Simple greeting responses
    if any(greeting in user_input.lower() for greeting in ["hello", "hi", "hey", "hlo"]):
        response = "Hello! How can I help you today?"
    
    elif "how are you" in user_input.lower():
        response = "I'm doing well, thank you for asking! What can I do for you?"
    
    elif "your name" in user_input.lower():
        response = "I'm Larry, your personal assistant bot. How can I help you?"
    
    elif "my name" in user_input.lower() and "is" in user_input.lower():
        # Extract name after "is"
        name_parts = user_input.lower().split("is")
        if len(name_parts) > 1:
            name = name_parts[1].strip()
            response = f"Nice to meet you, {name.title()}! How can I help you today?"
    
    elif "my name" in user_input.lower() and any(q in user_input.lower() for q in ["what", "who"]):
        # Check context for stored name
        name_context = None
        if context:
            for ctx in context:
                if "nice to meet you" in ctx.lower():
                    name_context = ctx
                    break
        
        if name_context:
            # Try to extract name from previous greeting
            response = "Based on our conversation, I believe I greeted you earlier, but I don't store personal information."
        else:
            response = "I don't store personal information between conversations, so I don't know your name."
    
    # Use context if provided
    elif context:
        # Look for relevant information in the context
        relevant_context = []
        for ctx in context:
            # Enhanced relevance check: look for significant word overlap
            user_words = [word.lower() for word in user_input.split() if len(word) > 3]
            ctx_words = ctx.lower().split()
            
            # Count matching significant words
            overlap = sum(1 for word in user_words if any(word in ctx_word for ctx_word in ctx_words))
            if overlap > 0:
                relevant_context.append((ctx, overlap))
        
        # Sort by relevance (overlap count)
        relevant_context.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_context:
            # Use the most relevant context to generate a response
            context_used = relevant_context[0][0]
            
            # Check if the context relates to specific topics
            if any(topic in context_used.lower() for topic in ["email", "message", "send"]):
                response = "I see you've been working with emails. Would you like to send a new email or check your inbox?"
            
            elif any(topic in context_used.lower() for topic in ["task", "todo", "reminder"]):
                response = "I notice you've been managing tasks. Would you like to add a new task or check your existing ones?"
            
            elif any(topic in context_used.lower() for topic in ["weather", "forecast"]):
                response = "I see you checked the weather earlier. Would you like to check the weather for another location?"
            
            elif any(topic in context_used.lower() for topic in ["meeting", "calendar", "schedule"]):
                response = "Based on your calendar activity, would you like to schedule a new meeting or review upcoming events?"
            
            elif any(topic in context_used.lower() for topic in ["news", "article", "headline"]):
                response = "I notice you were checking news earlier. Would you like me to find the latest headlines for you?"
            
            elif any(identity in context_used.lower() for identity in ["i'm larry", "personal assistant"]):
                response = "Yes, I'm Larry, your personal assistant bot. How can I help you today?"
            
            elif "nice to meet you" in context_used.lower():
                response = "Is there anything specific I can help you with today?"
            
            else:
                # Generic context response - avoid using exact user input as context
                if not context_used.startswith("User:"):
                    response = f"Based on our previous conversation, can I help you with something related to {context_used[:30]}...?"
                else:
                    response = "How can I assist you today?"
        else:
            # No relevant context found
            response = "I don't see any relevant previous activities. How can I assist you today?"
    
    # Topic-specific responses without context
    elif any(word in user_input.lower() for word in ["weather", "temperature", "forecast"]):
        response = "Would you like me to check the weather for you? Please specify a location."
    
    elif any(word in user_input.lower() for word in ["time", "date", "day"]):
        response = "Do you need information about the current time or date?"
    
    elif any(word in user_input.lower() for word in ["remind", "reminder", "schedule", "task"]):
        response = "Would you like me to set a reminder or add a task to your list?"
    
    elif any(word in user_input.lower() for word in ["search", "find", "look up"]):
        response = "What would you like me to search for?"
    
    elif "thank" in user_input.lower():
        response = "You're welcome! Feel free to ask if you need anything else."
    
    elif any(word in user_input.lower() for word in ["bye", "goodbye", "see you"]):
        response = "Goodbye! Have a great day!"
    
    # Identity questions
    elif any(q in user_input.lower() for q in ["who are you", "who're you", "who you are"]):
        response = "I'm Larry, your personal assistant bot. I can help with tasks, weather, reminders, and more."
    
    # Handle questions
    elif user_input.lower().startswith(("what", "who", "when", "where", "why", "how")):
        response = "That's a good question. To give you the best answer, could you provide more details?"
    
    # Default response for unhandled inputs
    else:
        response = "I'm not sure how to respond to that. Could you rephrase your request or ask me something specific?"
    
    return response, context_used