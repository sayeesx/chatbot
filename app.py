from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Chatbot API is running!'

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '')

    # Example response logic
    if "name" in message.lower():
        return jsonify({'response': "My name is SayeesBot. I'm here to help you!"})
    else:
        return jsonify({'response': f"You said: {message}"})
