from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import get_response

app = Flask(__name__)
CORS(app)  # 🔥 This enables cross-origin requests from your Next.js frontend

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_input = data.get('message', '')
    response = get_response(user_input)
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)
