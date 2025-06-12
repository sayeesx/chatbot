from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for your Vercel domain
CORS(app, origins=[
    "https://*.vercel.app",
    "https://sayees.vercel.app/",  # Replace with your actual domain
    "http://localhost:3000",  # For local development
    "https://localhost:3000"
])

# Initialize bot with error handling
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
    """Health check and API info endpoint"""
    if not bot:
        return jsonify({
            "status": "error",
            "message": "Bot initialization failed",
            "error": "PortfolioBot could not be initialized"
        }), 500
    
    try:
        # Get bot information safely
        bot_name = bot.data.get('name', 'Portfolio Bot')
        
        return jsonify({
            "status": "online",
            "service": "Portfolio Chatbot API",
            "bot_name": bot_name,
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
        return jsonify({
            "status": "error",
            "message": f"Error getting bot info: {str(e)}"
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy" if bot else "unhealthy",
        "bot_initialized": bot is not None,
        "ai_model_loaded": hasattr(bot, 'model') and bot.model is not None if bot else False,
        "timestamp": "2025-06-12T11:23:00Z"
    })

@app.route('/api/info')
def info():
    """Get bot information endpoint"""
    if not bot:
        return jsonify({
            "error": "Bot not initialized",
            "status": "error"
        }), 500
    
    try:
        # Get basic info safely
        basic_info = {
            'name': bot.data.get('name', 'Portfolio Bot'),
            'role': bot.data.get('role', 'AI Assistant'),
            'location': bot.data.get('location', {}).get('current', 'Unknown'),
            'skills': bot.data.get('technical_skills', []),
            'projects': len(bot.data.get('projects', [])),
            'languages': bot.data.get('languages', [])
        }
        
        return jsonify({
            "status": "success",
            "bot_info": basic_info,
            "context_available": hasattr(bot, 'context')
        })
    except Exception as e:
        logger.error(f"Error in info route: {e}")
        return jsonify({
            "error": f"Failed to get bot info: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main chat endpoint for the bot"""
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    if not bot:
        return jsonify({
            "error": "Bot not initialized",
            "response": "Sorry, the bot is currently unavailable. Please try again later.",
            "status": "error"
        }), 500

    try:
        # Get and validate request data
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

        # Process the message with the bot
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
            "response": "I encountered an error processing your request. Please try again.",
            "status": "error"
        }), 500

@app.route('/api/conversation/history')
def get_history():
    """Get conversation history"""
    if not bot:
        return jsonify({
            "error": "Bot not initialized",
            "status": "error"
        }), 500
    
    try:
        history = bot.get_conversation_history()
        
        # Format history for JSON response
        formatted_history = []
        for item in history:
            if 'user' in item:
                formatted_history.append({
                    "type": "user",
                    "message": item['user'],
                    "timestamp": item['timestamp'].isoformat() if 'timestamp' in item else None
                })
            elif 'bot' in item:
                formatted_history.append({
                    "type": "bot",
                    "message": item['bot'],
                    "timestamp": item['timestamp'].isoformat() if 'timestamp' in item else None
                })
        
        return jsonify({
            "status": "success",
            "history": formatted_history,
            "total_messages": len(formatted_history)
        })
        
    except Exception as e:
        logger.error(f"Error in history route: {e}")
        return jsonify({
            "error": f"Failed to get conversation history: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/conversation/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    if not bot:
        return jsonify({
            "error": "Bot not initialized",
            "status": "error"
        }), 500
    
    try:
        bot.clear_history()
        return jsonify({
            "status": "success",
            "message": "Conversation history cleared"
        })
    except Exception as e:
        logger.error(f"Error in clear history route: {e}")
        return jsonify({
            "error": f"Failed to clear history: {str(e)}",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "available_endpoints": [
            "GET / - API information",
            "GET /api/health - Health check", 
            "GET /api/info - Bot information",
            "POST /api/chat - Chat with bot",
            "GET /api/conversation/history - Get chat history",
            "POST /api/conversation/clear - Clear chat history"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end",
        "status": "error"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    logger.info(f"🚀 Starting Portfolio Bot API on port {port}")
    logger.info("Available endpoints:")
    logger.info("• GET  / - API information and status")
    logger.info("• GET  /api/health - Health check")
    logger.info("• GET  /api/info - Detailed bot information")
    logger.info("• POST /api/chat - Chat with the bot")
    logger.info("• GET  /api/conversation/history - Get chat history")
    logger.info("• POST /api/conversation/clear - Clear chat history")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
