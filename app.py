from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import PortfolioBot
import asyncio
from asgiref.wsgi import WsgiToAsgi
import os

app = Flask(__name__)
CORS(app)

bot = PortfolioBot()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot_name": bot.context['name'],
        "message": "Bot is running successfully!"
    })

@app.route('/chatbot', methods=['POST'])
async def chatbot_route():
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

# ASGI conversion
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(asgi_app, host="0.0.0.0", port=port)
