from recommendation_engine import RecommendationEngine
from data_preprocessing import load_data, preprocess_data
from utilities import fuzzy_match_title
from fuzzywuzzy import process

# Load and preprocess data
df = load_data(r'C:\Users\pytorch\Desktop\anime_recommendation_ai\data\anime_dataset_new.csv')  # Update with your actual path
df = preprocess_data(df)

# Initialize the recommendation engine
recommendation_engine = RecommendationEngine(df)

# Updated keywords to handle common input variations
keywords = {
    'recommendation': ['recommendation', 'recommend', 'recommedation', 'suggestion', 'suggest', 'recommendations', 'suggestions', 'recomendation', 'recomend'],
    'details': ['details', 'detail', 'info', 'information', 'anime info', 'show info', 'show details']
}

def fuzzy_match_request(user_input):
    """Fuzzy match the user's input to detect if they are asking for recommendations or details."""
    all_keywords = keywords['recommendation'] + keywords['details']
    best_match, confidence = process.extractOne(user_input, all_keywords)
    
    if confidence > 60:  # Set a confidence threshold for fuzzy matching
        if best_match in keywords['recommendation']:
            return 'recommendation'
        elif best_match in keywords['details']:
            return 'details'
    
    return None

feedback_keywords = {
    'positive': ['yes', 'yep', 'yeah', 'liked it', 'it was good', 'liked', 'love', 'satisfied', 'happy', 'great'],
    'negative': ['no', 'nope', 'didn\'t like', 'bad', 'unsatisfied', 'not happy', 'didn\'t enjoy', 'disappointed']
}

def fuzzy_match_feedback(user_input):
    """
    Fuzzy match the user's feedback to determine if it's positive or negative.
    """
    all_feedback = feedback_keywords['positive'] + feedback_keywords['negative']
    best_match, confidence = process.extractOne(user_input, all_feedback)
    
    if confidence > 60:  # Set a confidence threshold for fuzzy matching
        if best_match in feedback_keywords['positive']:
            return 'positive'
        elif best_match in feedback_keywords['negative']:
            return 'negative'
    
    return None

# Updated decision handling based on fuzzy matching for continuation or exit
def fuzzy_match_decision(user_input):
    """
    Fuzzy match the user's decision to detect if they want to continue or exit the conversation.
    """
    continuation_keywords = ['yes', 'sure', 'why not', 'okay', 'of course', 'continue', 'go ahead', 'more', 'next']
    exit_keywords = ['exit', 'quit', 'no', 'stop', 'end', 'goodbye', 'leave', 'done']
    
    all_decisions = continuation_keywords + exit_keywords
    best_match, confidence = process.extractOne(user_input, all_decisions)
    
    if confidence > 60:  # Set a confidence threshold for fuzzy matching
        if best_match in continuation_keywords:
            return 'continue'
        elif best_match in exit_keywords:
            return 'exit'
    
    return None  # Return None if no clear match

def ask_for_feedback():
    """Ask the user for feedback on the response and whether they want to continue."""
    print("Agent: Did you find the suggestions helpful? (Type 'yes' or 'no')")
    feedback = input("User: ").lower()

    # Use fuzzy matching to determine if the feedback is positive or negative
    feedback_type = fuzzy_match_feedback(feedback)
    
    if feedback_type == 'positive':
        print("Agent: I'm glad you liked it! Would you like more recommendations or details about another anime? (Type 'yes' or 'exit' to end the conversation)")
    elif feedback_type == 'negative':
        print("Agent: I'm sorry to hear that! Would you like me to help with more recommendations or details? (Type 'yes' or 'exit' to end the conversation)")
    else:
        print("Agent: Hmm, I didn't quite get that. Did you like the suggestions? (Please type 'yes' or 'no')")
        return ask_for_feedback()  # Retry if the input is unclear

    # Handle user's decision to continue or exit using fuzzy matching
    user_decision = input("User: ").lower()
    decision = fuzzy_match_decision(user_decision)
    
    if decision == 'continue':
        start_conversation()  # Start a new conversation
    elif decision == 'exit':
        print("Agent: Thank you! Feel free to ask me anytime for anime recommendations. Goodbye!")
    else:
        print("Agent: I'm not sure I understood that. Would you like more recommendations or details? (Type 'yes' to continue or 'exit' to end the conversation)")
        ask_for_feedback()  # Retry if unclear
  # Retry if unclear

def start_conversation():
    """Start the main conversation loop with the user."""
    print("Agent: Hey there! I'm your anime assistant. Would you like anime recommendations or details about a specific show today?")
    user_input = input("User: ").lower()

    # Use fuzzy matching to determine whether the user is asking for recommendations or details
    request_type = fuzzy_match_request(user_input)
    
    if request_type == 'recommendation':
        ask_for_genre_or_title()
    elif request_type == 'details':
        ask_for_anime_details()
    else:
        print("Agent: Hmm, I didn't quite catch that. Would you like recommendations or details about a specific anime?")
        start_conversation()  # Loop back if the input wasn't understood

# Define the possible keywords for genre or title
keywords_genre = {
    'genre': ['genre', 'ganre', 'type', 'category', 'genres', 'categories'],
    'title': ['title', 'ttle', 'anime name', 'show title', 'name of anime', 'specific anime']
}

def fuzzy_match_genre_or_title(user_input):
    """Fuzzy match the user's input to detect if they are asking for genre-based or title-based recommendations."""
    all_keywords = keywords_genre['genre'] + keywords_genre['title']
    best_match, confidence = process.extractOne(user_input, all_keywords)
    
    if confidence > 60:  # Set a confidence threshold for fuzzy matching
        if best_match in keywords_genre['genre']:
            return 'genre'
        elif best_match in keywords_genre['title']:
            return 'title'
    
    return None

def ask_for_genre_or_title():
    """Ask the user whether they prefer genre-based or title-based recommendations."""
    print("Agent: Awesome! Would you prefer recommendations by genre or based on a specific anime title?")
    user_input = input("User: ").lower()

    # Use fuzzy matching to determine whether the user means genre or title
    matched_request = fuzzy_match_genre_or_title(user_input)
    
    if matched_request == 'genre':
        ask_for_genre()
    elif matched_request == 'title':
        ask_for_anime_title()
    else:
        print("Agent: I'm sorry, I didn't understand. Do you want suggestions by genre or by title?")
        ask_for_genre_or_title()  # Re-prompt the user if input wasn't clear

def ask_for_genre():
    """Ask the user for their preferred genres."""
    print("Agent: Cool! Tell me which genres you're into. You can type something like 'action' or 'fantasy'.")
    genres = input("User: ").lower()
    confirm_genres(genres)

def ask_for_anime_title():
    """Ask the user for a specific anime title and provide recommendations."""
    print("Agent: Sure! What's the name of the anime you're thinking of?")
    anime_title = input("User: ").lower()
    recommendations = recommendation_engine.recommend_anime(anime_title)

    if isinstance(recommendations, str):
        print(f"Agent: {recommendations}")
    else:
        print("Agent: Here are some anime you might enjoy based on that title:")
        print(recommendations)

    ask_for_feedback()

def confirm_genres(genres):
    """Confirm the selected genres and provide recommendations."""
    print(f"Agent: Got it! Let me find some top anime in the {genres} genre for you...")
    recommendations = recommendation_engine.recommend_anime_by_genre(genres)

    if isinstance(recommendations, str):
        print(f"Agent: {recommendations}")
    else:
        print("Agent: Here's what I found:")
        print(recommendations)

    ask_for_feedback()

def ask_for_anime_details():
    """Ask the user for anime details they are interested in."""
    print("Agent: Please provide the anime title and the details you're interested in (e.g., genres, description).")
    anime_request = input("User: ").lower()
    
    # Make sure to pass the DataFrame (df) to the fetch_anime_details function
    details = fetch_anime_details(anime_request, df)

    if isinstance(details, str):
        print(f"Agent: {details}")
    else:
        print(f"Agent: Here is the information I found:")
        print(details)

    ask_for_feedback()

def fetch_anime_details(user_input, df):
    """Fetch specific details about an anime based on user input."""
    requested_info = {}
    keywords_mapping = {
        'description': ['description', 'desc', 'describe', 'plot', 'summary'],
        'year': ['year', 'release', 'released', 'when was it released'],
        'genres': ['genres', 'genre', 'categories', 'category']
    }

    for key, synonyms in keywords_mapping.items():
        if any(synonym in user_input.lower() for synonym in synonyms):
            title_query = user_input.lower()
            for synonym in synonyms:
                title_query = title_query.replace(synonym, '').strip()

            matched_title = fuzzy_match_title(title_query, df)
            if matched_title is None:
                return f"No anime found matching the title '{title_query}'"

            anime_info = df[df['Title (English)'] == matched_title]
            if not anime_info.empty:
                requested_info[key.capitalize()] = anime_info[key.capitalize()].values[0]  # Adjust the key here if needed
            else:
                return f"No anime found matching the title '{title_query}'"

    if requested_info:
        return {key: requested_info[key] for key in requested_info.keys() if requested_info[key]}
    
    return "No specific information requested."

def extract_title(user_input):
    """Extract the title from the user's input."""
    return user_input  # Placeholder logic
