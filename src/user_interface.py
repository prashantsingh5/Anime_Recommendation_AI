# user_interface.py
from recommendation_engine import RecommendationEngine
from data_preprocessing import load_data, preprocess_data
from utilities import fuzzy_match_title  # Adjust the import based on your project structure

# Load and preprocess data
df = load_data(r'C:\Users\pytorch\Desktop\anime_recommendation_ai\data\anime_dataset_new.csv')  # Update with your actual path
df = preprocess_data(df)

# Initialize the recommendation engine
recommendation_engine = RecommendationEngine(df)

def ask_for_feedback():
    print("Agent: I hope you found the suggestions helpful. Would you like more recommendations or details on another anime? (Type 'exit' to end the conversation)")
    feedback = input("User: ").lower()

    if 'yes' in feedback:
        start_conversation()  # Ensure start_conversation is accessible here
    elif 'exit' in feedback:
        print("Agent: Thank you! Feel free to ask me anytime for anime recommendations. Goodbye!")
        return  # Exit the conversation
    else:
        print("Agent: Okay, let me know if you need anything else!")
        ask_for_feedback()  # Ask again for feedback



def start_conversation():
    print("Agent: Hi! Do you want some anime recommendations or details about a specific show?")
    user_input = input("User: ").lower()

    if 'recommendations' in user_input:
        ask_for_genre_or_title()
    elif 'details' in user_input:
        ask_for_anime_details()
    else:
        print("Agent: I didn't get that. Please ask for recommendations or anime details.")
        start_conversation()

def ask_for_genre_or_title():
    print("Agent: Would you like recommendations by genre or based on a specific anime title?")
    user_input = input("User: ").lower()
    
    if 'genre' in user_input:
        ask_for_genre()
    elif 'title' in user_input:
        ask_for_anime_title()
    else:
        print("Agent: I didn't get that. Please choose genre or title.")
        ask_for_genre_or_title()

def ask_for_genre():
    print("Agent: Great! What genres do you like? (e.g., action, fantasy, romance)")
    genres = input("User: ").lower()
    confirm_genres(genres)

def ask_for_anime_title():
    print("Agent: Please provide the name of an anime you're interested in.")
    anime_title = input("User: ").lower()
    recommendations = recommendation_engine.recommend_anime(anime_title)

    if isinstance(recommendations, str):
        print(f"Agent: {recommendations}")
    else:
        print("Agent: Here are some anime you might like:")
        print(recommendations)

    ask_for_feedback()

def confirm_genres(genres):
    print(f"Agent: Got it! You like {genres}. Let me find the best anime for you...")
    recommendations = recommendation_engine.recommend_anime_by_genre(genres)

    if isinstance(recommendations, str):
        print(f"Agent: {recommendations}")
    else:
        print("Agent: Here are some anime you might like:")
        print(recommendations)

    ask_for_feedback()

def ask_for_anime_details():
    print("Agent: Please provide the anime title and the details you're interested in (e.g., year, genres, description).")
    anime_request = input("User: ").lower()
    
    # Make sure to pass the DataFrame (df) to the fetch_anime_details function
    details = fetch_anime_details(anime_request, df)  # Update this line

    if isinstance(details, str):
        print(f"Agent: {details}")
    else:
        print(f"Agent: Here is the information I found:")
        print(details)

    ask_for_feedback()


def fetch_anime_details(user_input, df):
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

    print("Requested info:", requested_info)  # Debug print
    if requested_info:
        return {key: requested_info[key] for key in requested_info.keys() if requested_info[key]}
    
    return "No specific information requested."


def extract_title(user_input):
    # Implement your logic for extracting the title from user input
    return user_input  # Placeholder
