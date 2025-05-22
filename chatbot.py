import json
import difflib
from datetime import datetime
import random


class PortfolioBot:
    def __init__(self):
        """Initialize the bot with portfolio data and configuration"""
        with open('sayees_data.json') as f:
            self.data = json.load(f)

        self.name = "SayeesBot"
        self.last_interaction = None
        self.conversation_history = []

        # NLP Configuration
        self.SPELLING_SENSITIVITY = 0.7
        self.CONFIDENCE_THRESHOLD = 0.6
        self.GREETINGS = ["hi", "hello", "hey", "greetings", "howdy"]
        self.FAREWELLS = ["bye", "goodbye", "see you", "later", "farewell"]

        self.keyword_map = self._build_keyword_map()
        self.misspellings = {
            "exquio": "exquio",
            "sayees": "sayees",
            "linkedin": "linkedin",
            "github": "github",
            "data science": "data science",
            "ai": "ai"
        }

    def _build_keyword_map(self):
        """Create mapping of keywords to response handlers"""
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
        """Correct common misspellings in user input"""
        words = text.lower().split()
        corrected = []
        for word in words:
            if word in self.misspellings:
                corrected.append(self.misspellings[word])
            else:
                matches = difflib.get_close_matches(
                    word,
                    self.keyword_map.keys(),
                    n=1,
                    cutoff=self.SPELLING_SENSITIVITY
                )
                corrected.append(matches[0] if matches else word)
        return ' '.join(corrected)

    def _time_based_greeting(self):
        """Return appropriate greeting based on time of day"""
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning!"
        elif hour < 17:
            return "Good afternoon!"
        return "Good evening!"

    # Response Handlers
    def _respond_name(self):
        responses = [
            f"I'm Sayees, an aspiring AI & Data Science professional.",
            "My name is Sayees, and I specialize in AI and Data Science.",
            "You can call me Sayees! I work in AI and Data Science."
        ]
        return random.choice(responses)

    def _respond_hometown(self):
        return random.choice([
            f"I'm originally from {self.data['location']['hometown']}.",
            f"My hometown is {self.data['location']['hometown']}.",
            f"I grew up in {self.data['location']['hometown']}."
        ])

    def _respond_current_location(self):
        return random.choice([
            f"I'm currently based in {self.data['location']['current']}.",
            f"Right now I'm living in {self.data['location']['current']}.",
            f"These days I'm located in {self.data['location']['current']}."
        ])

    def _respond_education(self):
        edu = self.data["education"]["current"]
        responses = [
            f"I'm pursuing {edu['degree']} specializing in {edu['specialization']} at {edu['college']}.",
            f"My current academic focus is {edu['degree']} with a specialization in {edu['specialization']}.",
            f"I'm enrolled in the {edu['degree']} program at {edu['college']}, {edu['university']}."
        ]
        return random.choice(responses)

    def _respond_interests(self):
        interests = ', '.join(self.data['interests'][:-1]) + ', and ' + self.data['interests'][-1]
        return random.choice([
            f"I'm particularly interested in: {interests}.",
            f"My professional interests include: {interests}.",
            f"I'm passionate about several areas: {interests}."
        ])

    def _respond_languages(self):
        languages = ', '.join(self.data['languages'][:-1]) + ', and ' + self.data['languages'][-1]
        return random.choice([
            f"I'm comfortable communicating in {languages}.",
            f"I can speak {languages}.",
            f"My language skills include {languages}."
        ])

    def _respond_skills(self):
        skills = ', '.join(self.data['soft_skills'][:-1]) + ', and ' + self.data['soft_skills'][-1]
        return random.choice([
            f"My interpersonal skills include: {skills}.",
            f"I've developed several soft skills: {skills}.",
            f"In terms of professional skills, I excel at: {skills}."
        ])

    def _respond_tools(self):
        tools = ', '.join(self.data['tools'][:-1]) + ', and ' + self.data['tools'][-1]
        return random.choice([
            f"In my work, I regularly use tools like: {tools}.",
            f"My technical toolkit includes: {tools}.",
            f"I'm proficient with several platforms: {tools}."
        ])

    def _respond_project(self):
        proj = self.data["projects"][0]
        tech = ', '.join(proj['technologies'][:-1]) + ', and ' + proj['technologies'][-1]
        return random.choice([
            f"One notable project is {proj['name']} – {proj['description']}, using {tech}.",
            f"I developed {proj['name']}, which {proj['description']}. Built with {tech}.",
            f"My project {proj['name']} {proj['description']}. Technologies used: {tech}."
        ])

    def _respond_contact(self):
        return random.choice([
            f"Let's connect! LinkedIn: {self.data['contact']['linkedin']} | GitHub: {self.data['contact']['github']}",
            f"Reach me on LinkedIn: {self.data['contact']['linkedin']} or GitHub: {self.data['contact']['github']}",
            f"Professional contacts: LinkedIn ({self.data['contact']['linkedin']}) | GitHub ({self.data['contact']['github']})"
        ])

    def _respond_help(self):
        return "I can tell you about my education, skills, projects, interests, and contact information. What would you like to know?"

    def process_input(self, user_input):
        """Main method to process user input and generate response"""
        # Clean and normalize input
        user_input = user_input.lower().strip()
        original_input = user_input
        user_input = self._correct_spelling(user_input)

        # Store conversation history
        self.conversation_history.append(("user", original_input))
        self.last_interaction = datetime.now()

        # Check greetings
        if any(greeting in user_input for greeting in self.GREETINGS):
            response = f"{self._time_based_greeting()} I'm Sayees' portfolio assistant. How can I help you today?"
            self.conversation_history.append(("bot", response))
            return response

        # Check farewells
        if any(farewell in user_input for farewell in self.FAREWELLS):
            response = random.choice([
                "It was great chatting with you! Feel free to return with more questions.",
                "Goodbye! Don't hesitate to reach out if you need more information.",
                "Talk to you later! Best of luck with your exploration."
            ])
            self.conversation_history.append(("bot", response))
            return response

        # Find best matching keyword category
        best_match = None
        highest_score = 0

        for pattern, handler in self.keyword_map.items():
            for keyword in pattern.split('|'):
                if keyword in user_input:
                    score = difflib.SequenceMatcher(None, keyword, user_input).ratio()
                    if score > highest_score:
                        highest_score = score
                        best_match = handler

        # Generate response
        if best_match and highest_score >= self.CONFIDENCE_THRESHOLD:
            response = best_match()
        else:
            response = random.choice([
                "I'm not sure I understand. Could you ask about my education, skills, or projects?",
                "That's an interesting question. I can tell you about my professional background.",
                "I'm still learning! Try asking about my technical skills or education."
            ])

        self.conversation_history.append(("bot", response))
        return response


# Test the bot directly if run as main
if __name__ == '__main__':
    bot = PortfolioBot()
    print(f"{bot.name} initialized. Type 'quit' to exit.")
    print(bot.process_input("hello"))

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            print(f"Bot: {bot.process_input('bye')}")
            break
        response = bot.process_input(user_input)
        print(f"Bot: {response}")