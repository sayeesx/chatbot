from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ✅ Configure CORS properly (no wildcards, specific domains)
CORS(app, resources={r"/api/*": {
    "origins": [
        "https://sayees.vercel.app",  # Replace with your actual Vercel domain
        "http://localhost:3000"       # For local dev
    ],
    "supports_credentials": True
}})

# Initialize bot
bot = None
try:
    from chatbot import PortfolioBot
    bot = PortfolioBot()
    logger.info("✅ PortfolioBot initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize PortfolioBot: {e}")
    bot = None

@app.route('/')
def home():
    if not bot:
        return jsonify({
            "status": "error",
            "message": "Bot initialization failed",
            "error": "PortfolioBot could not be initialized"
        }), 500
    try:
        return jsonify({
            "status": "online",
            "service": "Portfolio Chatbot API",
            "bot_name": bot.data.get('name', 'Portfolio Bot'),
            "message": "Bot is running successfully!",
            "version": "1.0.0",
            "endpoints": {
                "chat": "/api/chat (POST)",
                "health": "/api/health (GET)",
                "info": "/api/info (GET)"
            }
        })
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy" if bot else "unhealthy",
        "bot_initialized": bot is not None,
        "ai_model_loaded": hasattr(bot, 'model') and bot.model is not None if bot else False,
        "timestamp": "2025-06-12T11:23:00Z"
    })

@app.route('/api/info')
def info():
    if not bot:
        return jsonify({"error": "Bot not initialized", "status": "error"}), 500
    try:
        return jsonify({
            "status": "success",
            "bot_info": {
                'name': bot.data.get('name', 'Portfolio Bot'),
                'role': bot.data.get('role', 'AI Assistant'),
                'location': bot.data.get('location', {}).get('current', 'Unknown'),
                'skills': bot.data.get('technical_skills', []),
                'projects': len(bot.data.get('projects', [])),
                'languages': bot.data.get('languages', [])
            },
            "context_available": hasattr(bot, 'context')
        })
    except Exception as e:
        logger.error(f"Error in info route: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    if not bot:
        return jsonify({
            "error": "Bot not initialized",
            "response": "Bot unavailable. Please try again later.",
            "status": "error"
        }), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "response": "Please provide a message in JSON format.",
                "status": "error"
            }), 400

        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                "error": "No message provided",
                "response": "Please provide a message to chat with me!",
                "status": "error"
            }), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(bot.process_input(message))
        finally:
            loop.close()

        return jsonify({
            "response": response,
            "status": "success",
            "user_message": message,
            "timestamp": "2025-06-12T11:23:00Z"
        })

    except Exception as e:
        logger.error(f"Error in chat route: {e}")
        return jsonify({
            "error": str(e),
            "response": "I encountered an error. Please try again.",
            "status": "error"
        }), 500

@app.route('/api/conversation/history')
def get_history():
    if not bot:
        return jsonify({"error": "Bot not initialized", "status": "error"}), 500
    try:
        history = bot.get_conversation_history()
        return jsonify({
            "status": "success",
            "history": [
                {
                    "type": "user" if 'user' in item else "bot",
                    "message": item.get('user') or item.get('bot'),
                    "timestamp": item.get('timestamp').isoformat() if item.get('timestamp') else None
                }
                for item in history
            ],
            "total_messages": len(history)
        })
    except Exception as e:
        logger.error(f"Error in history route: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/conversation/clear', methods=['POST'])
def clear_history():
    if not bot:
        return jsonify({"error": "Bot not initialized", "status": "error"}), 500
    try:
        bot.clear_history()
        return jsonify({"status": "success", "message": "Conversation history cleared"})
    except Exception as e:
        logger.error(f"Error in clear history route: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "available_endpoints": [
            "GET /",
            "GET /api/health",
            "GET /api/info",
            "POST /api/chat",
            "GET /api/conversation/history",
            "POST /api/conversation/clear"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong",
        "status": "error"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    logger.info(f"🚀 Starting Portfolio Bot API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
