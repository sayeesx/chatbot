import json
import difflib
from datetime import datetime
import random

# Load portfolio data
with open('sayees_data.json') as f:
    data = json.load(f)


class PortfolioBot:
    def __init__(self):
        self.name = "SayeesBot"
        self.last_interaction = None
        self.conversation_history = []
        self.keyword_map = self._build_keyword_map()
        self.misspellings = {
            "exquio": "exquio",
            "sayees": "sayees",
            "linkedin": "linkedin",
            "github": "github",
            "data science": "data science"
        }

    def _build_keyword_map(self):
        return {
            "name": self._respond_name,
            "from|hometown|grew up": self._respond_hometown,
            "live|located|current location|based": self._respond_current_location,
            "education|study|school|college|university|degree": self._respond_education,
            "interest|hobby|passion": self._respond_interests,
            "language|speak|talk": self._respond_languages,
            "skill|ability|expertise|proficient": self._respond_skills,
            "tool|software|platform|technology": self._respond_tools,
            "project|work|exquio": self._respond_project,
            "contact|reach|connect|linkedin|github": self._respond_contact,
            "help": self._respond_help
        }

    def _correct_spelling(self, text):
        words = text.split()
        corrected = []
        for word in words:
            if word in self.misspellings:
                corrected.append(self.misspellings[word])
            else:
                matches = difflib.get_close_matches(word, self.keyword_map.keys(), n=1, cutoff=0.7)
                corrected.append(matches[0] if matches else word)
        return ' '.join(corrected)

    def _time_based_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning!"
        elif hour < 17:
            return "Good afternoon!"
        return "Good evening!"

    # Response handlers
    def _respond_name(self):
        responses = [
            f"I'm Sayees, an aspiring AI & Data Science professional.",
            "My name is Sayees, and I specialize in AI and Data Science.",
            "You can call me Sayees! I work in AI and Data Science."
        ]
        return random.choice(responses)

    def _respond_hometown(self):
        return random.choice([
            f"I'm originally from {data['location']['hometown']}.",
            f"My hometown is {data['location']['hometown']}.",
            f"I grew up in {data['location']['hometown']}."
        ])

    def _respond_current_location(self):
        return random.choice([
            f"I'm currently based in {data['location']['current']}.",
            f"Right now I'm living in {data['location']['current']}.",
            f"These days I'm located in {data['location']['current']}."
        ])

    def _respond_education(self):
        edu = data["education"]["current"]
        return random.choice([
            f"I'm pursuing {edu['degree']} specializing in {edu['specialization']} at {edu['college']}.",
            f"My current focus is {edu['degree']} with specialization in {edu['specialization']}.",
            f"I'm enrolled in {edu['degree']} at {edu['college']}, {edu['university']}."
        ])

    def _respond_interests(self):
        interests = ', '.join(data['interests'][:-1]) + ', and ' + data['interests'][-1]
        return f"My interests include: {interests}."

    def _respond_languages(self):
        languages = ', '.join(data['languages'][:-1]) + ', and ' + data['languages'][-1]
        return f"I'm proficient in: {languages}."

    def _respond_skills(self):
        skills = ', '.join(data['soft_skills'][:-1]) + ', and ' + data['soft_skills'][-1]
        return f"My skills include: {skills}."

    def _respond_tools(self):
        tools = ', '.join(data['tools'][:-1]) + ', and ' + data['tools'][-1]
        return f"I work with: {tools}."

    def _respond_project(self):
        proj = data["projects"][0]
        tech = ', '.join(proj['technologies'][:-1]) + ', and ' + proj['technologies'][-1]
        return f"I developed {proj['name']} - {proj['description']} using {tech}."

    def _respond_contact(self):
        return f"Connect with me on LinkedIn: {data['contact']['linkedin']} or GitHub: {data['contact']['github']}"

    def _respond_help(self):
        return "Ask me about my education, skills, projects, or contact information."

    def process_input(self, user_input):
        user_input = user_input.lower().strip()
        user_input = self._correct_spelling(user_input)

        # Check greetings
        if any(g in user_input for g in ["hi", "hello", "hey"]):
            return f"{self._time_based_greeting()} I'm Sayees' portfolio assistant. How can I help?"

        # Check farewells
        if any(f in user_input for f in ["bye", "goodbye"]):
            return "Nice chatting! Feel free to ask more questions anytime."

        # Find best matching handler
        best_score = 0
        best_handler = None

        for pattern, handler in self.keyword_map.items():
            for keyword in pattern.split('|'):
                if keyword in user_input:
                    score = difflib.SequenceMatcher(None, keyword, user_input).ratio()
                    if score > best_score:
                        best_score = score
                        best_handler = handler

        return best_handler() if best_score > 0.6 else "I can tell you about my education, skills, or projects. What would you like to know?"

    def _respond_greeting(self):
        return random.choice([
            f"{self._time_based_greeting()} I'm Sayees' portfolio assistant. How can I help you today?",
            "Hello! I'm here to share information about Sayees' professional background. What would you like to know?",
            "Hi there! I can tell you about Sayees' skills, education, and projects. How can I assist you?"
        ])

    def _respond_farewell(self):
        return random.choice([
            "It was great chatting with you! Feel free to come back if you have more questions.",
            "Goodbye! Don't hesitate to return if you'd like to know more about Sayees.",
            "Talk to you later! Best of luck with your exploration of Sayees' portfolio."
        ])

    def _respond_default(self):
        return random.choice([
            "I'm not entirely sure I understand. Could you try asking about Sayees' education, skills, or projects?",
            "I'm still learning! Try asking about Sayees' professional background, education, or technical skills.",
            "That's an interesting question. I'm better equipped to discuss Sayees' professional qualifications and experience."
        ])

    def process_input(self, user_input):
        """Process user input and generate appropriate response"""
        user_input = user_input.lower().strip()
        original_input = user_input
        user_input = self._correct_spelling(user_input)

        self.conversation_history.append(("user", original_input))

        # Check for greetings
        if any(greeting in user_input for greeting in GREETINGS):
            response = self._respond_greeting()
            self.conversation_history.append(("bot", response))
            return response

        # Check for farewells
        if any(farewell in user_input for farewell in FAREWELLS):
            response = self._respond_farewell()
            self.conversation_history.append(("bot", response))
            return response

        # Find the best matching keyword category
        best_match = None
        highest_score = 0

        for pattern, handler in self.keyword_map.items():
            for keyword in pattern.split('|'):
                if keyword in user_input:
                    score = self._calculate_similarity(keyword, user_input)
                    if score > highest_score:
                        highest_score = score
                        best_match = handler

        response = best_match() if best_match and highest_score >= CONFIDENCE_THRESHOLD else self._respond_default()

        self.conversation_history.append(("bot", response))
        self.last_interaction = datetime.now()
        return response


# Initialize the bot instance
bot = PortfolioBot()


# Flask API endpoints
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot_name": bot.name,
        "last_interaction": bot.last_interaction.isoformat() if bot.last_interaction else None
    })


@app.route('/chatbot', methods=['POST'])
def chatbot():
    request_data = request.get_json()
    message = request_data.get('message', '').strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = bot.process_input(message)
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "response": "I encountered an error processing your request. Please try again."
        }), 500


# Command line interface (for testing)
def chat_interface():
    print(f"{bot.name} initialized. Type 'quit' to exit.")
    print(bot._respond_greeting())

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            print(f"Bot: {bot._respond_farewell()}")
            break
        response = bot.process_input(user_input)
        print(f"Bot: {response}")


if __name__ == '__main__':
    # Run the Flask app by default
    app.run(debug=True)

    # To run in CLI mode instead:
    # chat_interface()