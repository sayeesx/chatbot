from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import PortfolioBot
import asyncio

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the bot
bot = PortfolioBot()


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot_name": bot.name,
        "message": "Sayees' Portfolio Bot is running"
    })


@app.route('/chatbot', methods=['POST'])
async def chatbot():
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = await bot.process_input(message)
        return jsonify({
            "response": response,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "response": "I encountered an error processing your request"
        }), 500


# Required for Gunicorn
if __name__ == '__main__':
    app.run(debug=True)
else:
    application = app