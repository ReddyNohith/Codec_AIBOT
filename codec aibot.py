# File: chatbot.py
from flask import Flask, request, jsonify
import sqlite3
import nltk
from nltk.chat.util import Chat, reflections
import datetime

# Download NLTK data
nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)

# Define chatbot response pairs (FAQ-style)
pairs = [
    [r"hi|hello", ["Hello! How can I assist you today?"]],
    [r"what is your name", ["I'm Grok, your friendly chatbot!"]],
    [r"how are you", ["I'm doing great, thanks for asking!"]],
    [r"help|support", ["I can answer FAQs or guide you. Try asking about our services!"]],
    [r"service|services", ["We offer customer support, product info, and more. What's your query?"]],
    [r"bye|exit", ["Goodbye! Have a great day!"]],
    [r"(.*)", ["Sorry, I didn't understand. Try saying 'help' or 'services'."]]
]

# Create NLTK chatbot
chatbot = Chat(pairs, reflections)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_input TEXT,
                  bot_response TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

# Log chat interaction
def log_interaction(user_input, bot_response):
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs (user_input, bot_response, timestamp) VALUES (?, ?, ?)",
              (user_input, bot_response, timestamp))
    conn.commit()
    conn.close()

# Route for chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({'response': 'Please enter a message.'}), 400
    
    # Get chatbot response
    bot_response = chatbot.respond(user_input)
    
    # Log interaction
    log_interaction(user_input, bot_response)
    
    return jsonify({'response': bot_response})

# Home route to serve basic HTML
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Chatbot</title></head>
    <body>
        <h1>Simple Chatbot</h1>
        <input type="text" id="message" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
        <div id="response"></div>
        <script>
            async function sendMessage() {
                const message = document.getElementById('message').value;
                const responseDiv = document.getElementById('response');
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                const data = await res.json();
                responseDiv.innerHTML = <p><b>You:</b> ${message}</p><p><b>Bot:</b> ${data.response}</p>;
                document.getElementById('message').value = '';
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '_main_':
    init_db()  # Initialize database
    app.run(debug=True)