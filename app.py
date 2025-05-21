from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ This route handles the homepage ("/")
@app.route('/')
def home():
    return 'SayeesBot is online!'

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '')

    # Example: Simple reply logic
    if "name" in message.lower():
        return jsonify({'response': "I'm SayeesBot, your AI assistant!"})
    elif "project" in message.lower():
        return jsonify({'response': "I worked on a project called Exquio — an AI-powered doctor booking system."})
    else:
        return jsonify({'response': f"You said: {message}"})
