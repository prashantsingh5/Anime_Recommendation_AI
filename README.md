# Anime Recommendation AI

## Project Description

Anime Recommendation AI is an interactive chatbot application designed to provide personalized anime recommendations and details based on user input. Using a dataset of anime titles, genres, and descriptions, this application employs content-based filtering techniques to suggest anime tailored to user preferences.

## Features

- **Personalized Recommendations**: Users can receive anime suggestions based on their favorite genres or specific titles.
- **Detailed Information**: Users can inquire about specific anime titles and receive information such as descriptions and genres.
- **User-Friendly Interface**: A simple conversational interface allows users to easily interact with the bot.
- **Fuzzy Matching**: The application employs fuzzy matching to identify user-input titles, ensuring accurate recommendations even with minor typos.
- **Data Preprocessing**: Includes data cleaning and preprocessing steps to handle missing values and ensure high-quality input data.

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/prashantsingh5/Anime_Recommendation_AI.git
   cd anime_recommendation_ai
   
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   
3. Update the dataset path in user_interface.py to point to your local dataset file.

## Usage

Interact with the chatbot through the terminal. You can ask for anime recommendations, details about specific titles, or specify genres you like.
1. Reach the directory:
   ```bash
   cd src
2. Run the main script:
   ```bash
   python main.py

## Example Interaction

Agent: Hi! Do you want some anime recommendations or details about a specific show?
User: I want some anime recommendations.
Agent: Would you like recommendations by genre or based on a specific anime title?
User: I'd like recommendations by genre.
Agent: Great! What genres do you like? (e.g., action, fantasy, romance)
User: I love action and adventure anime.
Agent: Here are some anime you might like:

## Example Image

![Screenshot 2024-10-10 170434](https://github.com/user-attachments/assets/4f4f3e59-705f-43b1-a77b-320cea4798d2)
