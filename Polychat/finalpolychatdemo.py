import io
import os
import pygame
from gtts import gTTS
from googletrans import Translator
import mysql.connector
import speech_recognition as sr
import pyttsx3
import webbrowser
from serpapi import GoogleSearch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from PyDictionary import PyDictionary

# Mapping between language names and language codes
LANGUAGE_CODES = {
    'hindi': 'hi',
    'marathi': 'mr',
    'korean': 'ko',
    'japanese': 'ja',
    'english': 'en',
    'kannada': 'kn',
    'gujarati': 'gu',
    'tamil': 'ta',
    'telugu': 'te'
}

analyzer = SentimentIntensityAnalyzer()

def open_polychat():
    # Open Polychat web application in default web browser
    webbrowser.open("http://localhost/ChatApp/users.php")
    return True  # Return True indicating Polychat is opened

# Function to check if "open polychat" is said
def is_open_polychat(text):
    return "open poly chat" in text.lower()

class Speaking:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

class GFG:
    def __init__(self):
        self.speak = Speaking()
        pygame.init()
    
    def translate_to_marathi(self, text):
        translator = Translator()
        translated_text = translator.translate(text, src='en', dest='mr')
        return translated_text.text

    def Dictionary(self):
        dic = PyDictionary()

        # Ask user for the word
        self.speak.speak("Enter a word:")
        query = input("Enter a word: ")

        # Look up the meaning of the word
        word_meaning = dic.meaning(query)

        if word_meaning:
            meaning = word_meaning.get('Noun')
            if meaning:
                marathi_meaning = self.translate_to_marathi(meaning[0])
                self.speak.speak(f"The meaning of '{query}' in Marathi is: {marathi_meaning}")
            else:
                self.speak.speak(f"Sorry, no meaning found for '{query}'")
        else:
            self.speak.speak(f"Sorry, '{query}' not found in the dictionary")

def translate_text(text, dest_language='en'):
    # Translate the text
    translator = Translator()
    translated_text = translator.translate(text, dest=dest_language).text
    print("Translated text:", translated_text)
    return translated_text

def read_text(text, dest_language='en'):
    # Create a gTTS object
    tts = gTTS(text=text, lang=dest_language)

    # Save the audio to a file-like object
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    # Load the audio data
    pygame.mixer.music.load(audio_data)
    pygame.mixer.init()

    # Play the audio
    pygame.mixer.music.play()

    # Wait until the audio has finished playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
def ask_language1():
    print("In what language do you want to send the message?")
    read_text("In what language do you want to send the message?")
    language = recognize_language()
    if language in LANGUAGE_CODES:
        return LANGUAGE_CODES[language]
    else:
        print("Language not supported. Please try again.")
        read_text("Language not supported. Please try again.")
        return ask_language1()
    
def ask_language():
    print("In what language do you want to read the message?")
    read_text("In what language do you want to read the message?")
    language = recognize_language()
    if language in LANGUAGE_CODES:
        return LANGUAGE_CODES[language]
    else:
        print("Language not supported. Please try again.")
        read_text("Language not supported. Please try again.")
        return ask_language()

def recognize_language():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    return None

def send_message(sender_unique_id, receiver_unique_id=None, receiver_name=None):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="chatapp"
    )
    cursor = conn.cursor()

    # If receiver name is not provided, take user input for receiver names (comma-separated)
    if not receiver_name:
        print("Enter the receiver's name:")
        read_text("Enter the receiver's name:")
        receiver_name = recognize_speech()
        print("You said:", receiver_name)

    # Check if the entered receiver name exists in the database
    query = "SELECT unique_id FROM users WHERE fname = %s"
    cursor.execute(query, (receiver_name,))
    row = cursor.fetchone()
    if not row:
        print("No contact found for:", receiver_name)
        read_text("No contact found for:", receiver_name)
        return

    receiver_unique_id = row[0]

    # Ask the user for the language in which to send the message
   # print("In what language do you want to send the message?")
    #read_text("In what language do you want to send the message?")
    dest_language = ask_language1()

    # Translate the message content to English
    print("Enter your message:")
    read_text("Enter your message:")
    message_content = recognize_speech()
    print("You said:", message_content)

    # Translate the message to the destination language if it's not English
    if dest_language != 'en':
        translated_message = translate_text(message_content, dest_language)
    else:
        translated_message = message_content

    # Insert the translated message into the database
    query = "INSERT INTO messages (incoming_msg_id, outgoing_msg_id, msg) VALUES (%s, %s, %s)"
    cursor.execute(query, (receiver_unique_id, sender_unique_id, translated_message))
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    # Respond to the message indicating successful message delivery
    success_message = f"Message sent successfully to: {receiver_name}"
    read_text(success_message, 'en')
    # If the message is sent successfully, respond to the sender
    #respond_to_message(receiver_unique_id, dest_language, response=translated_message)

def recognize_speech():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        read_text("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    return None

def respond_to_message(receiver_unique_id, sender_unique_id, dest_language='en', incoming_msg_id=None):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="chatapp"
    )
    cursor = conn.cursor()

    # Fetch the message content based on incoming_msg_id
    query = "SELECT msg FROM messages WHERE msg_id = %s"
    cursor.execute(query, (incoming_msg_id,))
    message_row = cursor.fetchone()
    if message_row:
        message_content = message_row[0]
    else:
        print("Message not found.")
        cursor.close()
        conn.close()
        return

    # Generate response using simple_chatbot function
    response = simple_chatbot(message_content)
    if response:
        print("Response found:", response)
    else:
    
        print("No response found in simple_chatbot, generating response using VADER...")
        sentiment_scores = analyze_sentiment_vader(message_content)
        response = generate_response_vader(sentiment_scores, message_content)
        print("VADER generated response:", response)

    # If response is not found in simple_chatbot, use VADER to generate response

    # Translate the response to the destination language if it's not English
    if dest_language != 'en':
        translated_response = translate_text(response, dest_language)
    else:
        translated_response = response

    # Insert the translated response into the database
    query = "INSERT INTO messages (incoming_msg_id, outgoing_msg_id, msg) VALUES (%s, %s, %s)"
    cursor.execute(query, (sender_unique_id, receiver_unique_id, translated_response))
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    # Respond to the user indicating successful response
    success_message = "Response sent successfully!"
    print(success_message)
    read_text(success_message, 'en')


def read_and_translate_messages(receiver_unique_id, dest_language='en'):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="chatapp"
    )
    cursor = conn.cursor()

    # Execute SQL query to select messages sent to the specified receiver unique ID
    query = """
            SELECT sender_info.fname, sender_info.unique_id, m.msg, m.msg_id
            FROM messages m
            JOIN users sender_info ON m.outgoing_msg_id = sender_info.unique_id
            JOIN users receiver_info ON m.incoming_msg_id = receiver_info.unique_id
            WHERE m.incoming_msg_id = %s AND m.read_status = 0
            """
    cursor.execute(query, (receiver_unique_id,))
    rows = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    # Translate and read out messages sent to the specified receiver unique ID
    if rows:
        for row in rows:
            sender_name = row[0]
            sender_unique_id = row[1]
            message_content = row[2]
            message_id = row[3]
            message_to_translate = f"Message from {sender_name}: {message_content}"

            # Read the message
            translated_message = translate_text(message_to_translate, dest_language)
            read_text(translated_message, dest_language)
            update_read_status(message_id)
            # Ask the user for action
            while True:
                action = recognize_speech()
                
                if action is None:
                    print("Could not understand audio. Please try again.")
                    continue

                if action == 'read again':
                    # Reread the same message
                    read_text(translated_message, dest_language)
                    print(translated_message, dest_language)
                elif action == 'reply':
                    # User wants to reply to the sender
                    send_message(receiver_unique_id, dest_language, receiver_name=sender_name)
                    break
                elif action == 'explain':
                    # Explain the message content
                    explanation = search_google(message_content)
                    read_text(explanation, dest_language)
                elif action == 'next':
                    break  # Move to the next message
                elif 'search' in action or 'find' in action:
                    # Modified condition
                    query = action.split("search", 1)[1].strip() if "search" in action else action.split("find", 1)[1].strip()
                    result = search_google(query)
                    print("Search result:", result)
                    read_text(result)
                elif "send" in action or "send message" in action:
                    read_text("To whom do you want to send the message?")
                    print("To whom do you want to send the message?")
                    receiver_name = recognize_speech()
                    send_message(1527605249, receiver_unique_id=None, receiver_name=receiver_name)
                elif action == "respond":
                    # Use the chatbot to generate a response
                    print("")
                    #respond_to_message(receiver_unique_id, dest_language='en', response=None, incoming_msg_id=None)
                    respond_to_message(receiver_unique_id, sender_unique_id, dest_language, message_id)
                elif "stop"or "stop":
                    print("Thank you for using PolyChat Voice Assistant!")
                    read_text("Thank you for using PolyChat Voice Assistant!")
                    exit()
                else:
                    print("Invalid action.")
    else:
        print("No new message")
        read_text("No new message")
        
def update_read_status(message_id):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="chatapp"
    )
    cursor = conn.cursor()

    # Execute SQL query to update the read_status to 1
    query = """
            UPDATE messages
            SET read_status = 1
            WHERE msg_id = %s
            """
    cursor.execute(query, (message_id,))
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

def search_google(query):
    try:
        # Initialize GoogleSearch object with your SerpApi key
        search = GoogleSearch({
            "q": query,
            "api_key": "b0ff03a6bfdded03c6123c031a924de3ab860f41f20ad354684ac9a1f9db1ab1"  # Replace this with your actual SerpApi key
        })

        # Get search results
        results = search.get_dict()

        # Extract and return the snippet of the first search result
        if "organic_results" in results:
            first_result = results["organic_results"][5]
            return first_result["snippet"]
        else:
            return "No relevant information found on Google."
    except Exception as e:
        print("Error occurred while fetching search results:", e)
        return "Error occurred while fetching search results."

def analyze_sentiment_vader(message):
    """
    Analyze the sentiment of a given message using VADER.
    Returns a dictionary containing sentiment scores.
    """
    sentiment_scores = analyzer.polarity_scores(message)
    return sentiment_scores

def generate_response_vader(sentiment_scores, message):
    """
    Generate a response based on the sentiment scores from VADER and the message content.
    """
    compound_score = sentiment_scores['compound']
    
    if compound_score >= 0.5:  # Very positive sentiment
        return "That's fantastic! I'm so happy for you! 😄🎉"
    elif compound_score >= 0.05 and compound_score < 0.5:  # Positive sentiment
        return "That's awesome! 😊"
    elif "hey" in message.lower() or "hello" in message.lower() or "hi" in message.lower():
        return "Hey there! How are you doing?"

    elif compound_score > -0.05 and compound_score < 0.05:  # Neutral sentiment
        if any(word in message.lower() for word in ['doing', 'up to']):
            return "Just chilling! What about you?"
        elif message.strip().endswith('?'):
            return "Not much, just here. What's up?"
        else:
            return "Gotcha, just hanging out!"
    elif compound_score <= -0.5:  # Very negative sentiment
        return "Oh no, I'm really sorry to hear that. It's okay to feel down sometimes. Do you want to talk about it?"
    elif compound_score <= -0.05 and compound_score > -0.5:  # Negative sentiment
        return "I'm sorry to hear that. Want to talk about it or need a distraction?"
    elif compound_score >= 0.05 and compound_score < 0.1:  # Slightly positive sentiment
        return "That's nice! 😊"
    elif compound_score <= -0.1 and compound_score > -0.5:  # Slightly negative sentiment
        return "I understand, it's tough. Hang in there!"
    elif compound_score >= 0.05 and compound_score < 0.1:  # Moderate positive sentiment
        return "That sounds great! 😊"
    elif compound_score <= -0.3 and compound_score > -0.5:  # Moderate negative sentiment
        return "I'm sorry, things will get better. I'm here for you."
    elif compound_score >= 0.3 and compound_score < 0.5:  # Strong positive sentiment
        return "Wow, that's amazing news! 🎉"
    else:  # For any other cases
        return "I'm not sure how to respond to that. Can you tell me more?"

def count_unread_messages(user_unique_id):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="chatapp"
    )
    cursor = conn.cursor()

    # Execute SQL query to count the number of unread messages
    query = """
            SELECT COUNT(*)
            FROM messages
            WHERE incoming_msg_id = %s AND read_status = 0
            """
    cursor.execute(query, (user_unique_id,))
    count = cursor.fetchone()[0]

    # Close cursor and connection
    cursor.close()
    conn.close()

    return count

def provide_help():
    help_text = """
    Available Commands:
    1. "Open Polychat" or "Open Poly Chat" - Opens the Polychat web application.
    2. "Read Messages" or "Read Message" - Reads your unread messages and translates them if needed.
    3. "Meaning [word]" - Provides the dictionary meaning of the specified word.
    4. "Search [query]" or "Find [query]" - Searches the web for the specified query.
    5. "Send Message" - Prompts you to send a message to a specified contact.
    6. "Help" - Provides this list of commands and their descriptions.
    7. "Stop" or "Quit" - Exits the application.
    """
    print(help_text)
    read_text(help_text)

def simple_chatbot(user_input):
    # Define casual responses
    responses = {
        "hello": "Hello!",
        "hey": "Hey!",
        "how are you": "I'm good, thanks! How about you?",
        "what's up": "Not much, just chilling. You?",
        "good morning": "Morning! How's it going?",
        "good afternoon": "Hey! What's up?",
        "good evening": "Hey! What's happening?",
        "bye": "Catch you later! Take care!",
        "thank you": "No worries!",
        "sorry": "No problem!",
        "tell me a joke": "Sure! Why did the bicycle fall over? Because it was two-tired!",
        "how was your day": "Pretty good! How about yours?",
        "what are you doing": "Just hanging out here!",
        "have a great day": "You too! Have a blast!",
        "how's it going": "All good! What's up with you?",
        "what are you up to": "Not much, just here to chat with you!",
        "nice to meet you": "Likewise!",
        "how's everything": "Everything's cool! You?",
        "take care": "You too! Catch you later!",
        "can you help me": "Sure thing! What do you need?",
        "what's new": "Not much, just the usual. You?",
        "I'm bored": "Let's chat and kill some time!",
        "that's funny": "Glad you liked it! I've got more jokes if you want!",
        "I'm hungry": "Me too! Let's grab a snack together!",
        "I'm tired": "Take a break and relax for a bit!",
        "let's hang out": "Sure thing! What do you want to do?",
        "what's your favorite movie": "I love all movies! What's yours?",
        "what's your favorite food": "I'm a fan of virtual snacks!",
        "I'm excited": "That's awesome! What's got you excited?",
        "I'm stressed": "Take a deep breath and relax. I'm here to chat if you need!",
        "I'm happy": "Great to hear! What's making you happy?",
        "I'm sad": "I'm here for you. Want to talk about it?",
        "doing": "Just chilling! What about you?",
        "weather": "It's looking pretty nice today!",
        "movie": "I love all movies! What's yours?",
        "time": "Sorry, I don't have access to real-time data!",
        "color": "As a chatbot, I don't have preferences, but blue is a nice color!",
        "music": "I don't have preferences, but I can appreciate a good tune!",
        "pets": "I don't have any pets, but I've heard cats are quite popular!",
        "hobby": "I don't have hobbies in the traditional sense, but I love chatting with people!",
        "interesting": "Did you know that the shortest war in history lasted only 38 minutes? It was between Britain and Zanzibar in 1896!",
        "chat": "Let's chat and kill some time!",
        "meet": "Sure, that sounds like fun! Let me know when you're free.",
        "fact": "Here's a fun fact: The first oranges weren't orange! They were green.",
        "book": "Books are a great way to escape reality for a while. Do you have a favorite genre?",
        "travel": "Traveling is an amazing experience! Where would you like to go next?",
        "dream": "Dream big and never stop chasing your aspirations! What's one of your biggest dreams?",
        "technology": "Technology is advancing rapidly! What's one technological innovation you're excited about?",
        "inspiration": "You're capable of amazing things! What's something that inspires you?"
        # Add more emotion-related responses here
    }

    # Convert user input to lowercase for case-insensitive matching
    user_input = user_input.lower()

    # Check if the user input matches any predefined responses
    if user_input in responses:
        return responses[user_input]
    else:
        found_response = False
        for key, value in responses.items():
            if any(word in user_input for word in ['doing', 'up to']) and 'doing' in key:
                print("Chatbot:", value)
                return value
            elif any(word in user_input for word in ['joke', 'funny']) and 'joke' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['weather']) and 'weather' in key:
                print("Chatbot:", value)
                return value
              
            elif any(word in user_input for word in ['hungry', 'food']) and ('hungry' in key or 'food' in key):
                print("Chatbot:", value)
                return value
                
            elif any(word in user_input for word in ['tired', 'stress']) and ('tired' in key or 'stress' in key):
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['happy', 'excited']) and ('happy' in key or 'excited' in key):
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['sad']) and 'sad' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['chat']) and 'chat' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['meet', 'hang out']) and ('meet' in key or 'hang out' in key):
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['fact']) and 'fact' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['book']) and 'book' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['travel']) and 'travel' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['dream']) and 'dream' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['technology']) and 'technology' in key:
                print("Chatbot:", value)
                return value
            
            elif any(word in user_input for word in ['inspiration']) and 'inspiration' in key:
                print("Chatbot:", value)
                return value

        if not found_response:
            sentiment_scores = analyze_sentiment_vader(user_input)
            response_vader = generate_response_vader(sentiment_scores, user_input)
            print("VADER Sentiment Analysis:", response_vader)


# Main function to execute the program
# Initialize Pygame mixer for playing audio
pygame.mixer.init()

def main():
    read_text("Welcome to Polychat Voice Assistant")
    print("Welcome to Polychat!")
    
    # Initialize the GFG class
    gfg = GFG()

    # Assuming the user's unique ID is 1527605249 (you might want to modify this to get the actual logged-in user's ID)
    user_unique_id = 228245051


    
    # Count the number of unread messages
    unread_count = count_unread_messages(user_unique_id)
    
    # Announce the number of unread messages
    if unread_count > 0:
        message = f"You have {unread_count} new messages."
    else:
        message = "You have no new messages."
    
    print(message)
    read_text(message)
    
    while True:
        print("Listening...")
        text = recognize_speech()

        if text:
            print("You said:", text)

            if "quit" in text.lower():
                break
            elif "open polychat" in text.lower() or "open poly chat" in text.lower():  # Check for variations
                open_polychat()  # Open Polychat web application
            elif "read messages" in text.lower() or "read message" in text.lower():
                dest_language = ask_language()
                read_and_translate_messages(user_unique_id, dest_language)
            elif "meaning" in text.lower():
                gfg.Dictionary()
            elif "search" in text.lower() or "find" in text.lower():
                query = text.split("search", 1)[1].strip() if "search" in text.lower() else text.split("find", 1)[1].strip()
                result = search_google(query)
                print("Search result:", result)
                read_text(result)
            elif "send" in text.lower() or "send message" in text.lower():
                read_text("To whom do you want to send the message?")
                print("To whom do you want to send the message?")
                receiver_name = recognize_speech()
                send_message(user_unique_id, receiver_unique_id=None, receiver_name=receiver_name)
            elif "help" in text.lower():
                provide_help()
            elif "stop" in text.lower() or "stop" in text.lower():
                print("Thank you for using PolyChat Voice Assistant!")
                read_text("Thank you for using PolyChat Voice Assistant!")
                exit() 
            else:
                print("Sorry, I didn't understand that.")
                read_text("Sorry, I didn't understand that.")


if __name__ == "__main__":
    main()
