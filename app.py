from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/')
def home():
    return 'SayeesBot is online!'

@app.route('/chatbot', methods=['POST'])  # ✅ This enables POST on /chatbot
def chatbot():
    data = request.get_json()
    message = data.get('message', '')

    if "project" in message.lower():
        return jsonify({'response': "I worked on a project called Exquio — an AI-powered doctor booking system."})
    elif "name" in message.lower():
        return jsonify({'response': "I'm SayeesBot, your AI assistant!"})
    else:
        return jsonify({'response': f"You said: {message}"})

if __name__ == '__main__':
    app.run(debug=True)
