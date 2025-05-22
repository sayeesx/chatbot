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
        self.GREETINGS = ["hi", "hello", "hey", "greetings", "howdy", "hola", "yo"]
        self.FAREWELLS = ["bye", "goodbye", "see you", "later", "farewell"]

        self.keyword_map = self._build_keyword_map()
        self.misspellings = {
            "exquio": "exquio",
            "sayees": "sayees",
            "linkedin": "linkedin",
            "github": "github",
            "data science": "data science",
            "ai": "ai",
            "project": "project",
            "projects": "project",
            "work": "project",
            "works": "project"
        }

        # State for project conversation context
        self.awaiting_project_choice = False

        # To track last topic asked to vary responses
        self.last_response_type = None
        self.response_counters = {}

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
            "project|work": self._handle_projects_intro,
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
    def _get_varied_response(self, key, responses):
        """Return different responses on repeated calls for same topic"""
        count = self.response_counters.get(key, 0)
        response = responses[count % len(responses)]
        self.response_counters[key] = count + 1
        return response

    def _respond_name(self):
        responses = [
            "I'm Sayees, an aspiring AI & Data Science professional.",
            "My name is Sayees, and I specialize in AI and Data Science.",
            "You can call me Sayees! I work in AI and Data Science."
        ]
        return self._get_varied_response("name", responses)

    def _respond_hometown(self):
        hometown = self.data['location']['hometown']
        responses = [
            f"I'm originally from {hometown}.",
            f"My hometown is {hometown}.",
            f"I grew up in {hometown}."
        ]
        return self._get_varied_response("hometown", responses)

    def _respond_current_location(self):
        current = self.data['location']['current']
        responses = [
            f"I'm currently based in {current}.",
            f"Right now I'm living in {current}.",
            f"These days I'm located in {current}."
        ]
        return self._get_varied_response("current_location", responses)

    def _respond_education(self):
        edu = self.data["education"]["current"]
        responses = [
            f"I'm pursuing {edu['degree']} specializing in {edu['specialization']} at {edu['college']}.",
            f"My current academic focus is {edu['degree']} with a specialization in {edu['specialization']}.",
            f"I'm enrolled in the {edu['degree']} program at {edu['college']}, {edu['university']}."
        ]
        return self._get_varied_response("education", responses)

    def _respond_interests(self):
        interests = ', '.join(self.data['interests'][:-1]) + ', and ' + self.data['interests'][-1]
        responses = [
            f"I'm particularly interested in: {interests}.",
            f"My professional interests include: {interests}.",
            f"I'm passionate about several areas: {interests}."
        ]
        return self._get_varied_response("interests", responses)

    def _respond_languages(self):
        languages = ', '.join(self.data['languages'][:-1]) + ', and ' + self.data['languages'][-1]
        responses = [
            f"I'm comfortable communicating in {languages}.",
            f"I can speak {languages}.",
            f"My language skills include {languages}."
        ]
        return self._get_varied_response("languages", responses)

    def _respond_skills(self):
        skills = ', '.join(self.data['soft_skills'][:-1]) + ', and ' + self.data['soft_skills'][-1]
        responses = [
            f"My interpersonal skills include: {skills}.",
            f"I've developed several soft skills: {skills}.",
            f"In terms of professional skills, I excel at: {skills}."
        ]
        return self._get_varied_response("skills", responses)

    def _respond_tools(self):
        tools = ', '.join(self.data['tools'][:-1]) + ', and ' + self.data['tools'][-1]
        responses = [
            f"In my work, I regularly use tools like: {tools}.",
            f"My technical toolkit includes: {tools}.",
            f"I'm proficient with several platforms: {tools}."
        ]
        return self._get_varied_response("tools", responses)

    def _respond_contact(self):
        contact = self.data['contact']
        responses = [
            f"Let's connect! LinkedIn: {contact['linkedin']} | GitHub: {contact['github']}",
            f"Reach me on LinkedIn: {contact['linkedin']} or GitHub: {contact['github']}",
            f"Professional contacts: LinkedIn ({contact['linkedin']}) | GitHub ({contact['github']})"
        ]
        return self._get_varied_response("contact", responses)

    def _respond_help(self):
        return ("I can tell you about my education, skills, projects, interests, and contact information. "
                "What would you like to know?")

    def _list_projects(self):
        """Return a formatted string listing all project names."""
        projects = self.data["projects"]
        project_names = [proj['name'] for proj in projects]
        formatted_list = "\n".join(f"- {name}" for name in project_names)
        return f"Here are some of my projects:\n{formatted_list}"

    def _handle_projects_intro(self):
        """List projects and ask user which one to know about."""
        self.awaiting_project_choice = True
        return (self._list_projects() +
                "\nWhich project would you like to know more about? Please type the project name.")

    def _respond_project_details(self, project_name):
        """Return detailed info about the specified project or fallback message."""
        projects = self.data["projects"]
        # Use fuzzy matching to find the best project match
        project_names = [proj['name'].lower() for proj in projects]
        matches = difflib.get_close_matches(project_name.lower(), project_names, n=1, cutoff=0.6)
        if matches:
            matched_name = matches[0]
            for proj in projects:
                if proj['name'].lower() == matched_name:
                    tech = ', '.join(proj['technologies'][:-1]) + ', and ' + proj['technologies'][-1] if len(proj['technologies']) > 1 else proj['technologies'][0]
                    response_variations = [
                        f"Project '{proj['name']}': {proj['description']} Technologies used include {tech}.",
                        f"Here's more about '{proj['name']}': {proj['description']} Built with {tech}.",
                        f"'{proj['name']}' is a project where I worked on {proj['description']}. It uses {tech}."
                    ]
                    return random.choice(response_variations)
        else:
            return ("I couldn't find that project. Please check the name or type 'list projects' to see available projects.")

    def _respond_greeting(self):
        greetings_responses = [
            f"{self._time_based_greeting()} I'm Sayees' portfolio assistant. How can I help you today?",
            f"{self._time_based_greeting()} Hello! Ready to explore my portfolio?",
            f"{self._time_based_greeting()} Hi there! What would you like to know about my work?"
        ]
        return random.choice(greetings_responses)

    def process_input(self, user_input):
        """Main method to process user input and generate response"""
        user_input = user_input.lower().strip()
        original_input = user_input
        user_input = self._correct_spelling(user_input)

        self.conversation_history.append(("user", original_input))
        self.last_interaction = datetime.now()

        # Check greetings
        if any(greeting in user_input for greeting in self.GREETINGS):
            self.awaiting_project_choice = False  # Reset any awaiting state
            response = self._respond_greeting()
            self.conversation_history.append(("bot", response))
            return response

        # Check farewells
        if any(farewell in user_input for farewell in self.FAREWELLS):
            self.awaiting_project_choice = False
            response = random.choice([
                "It was great chatting with you! Feel free to return with more questions.",
                "Goodbye! Don't hesitate to reach out if you need more information.",
                "Talk to you later! Best of luck with your exploration."
            ])
            self.conversation_history.append(("bot", response))
            return response

        # If awaiting project choice, handle that first
        if self.awaiting_project_choice:
            # Check if user wants to list projects again
            if "list" in user_input and "project" in user_input:
                response = self._list_projects()
                self.conversation_history.append(("bot", response))
                return response

            # Try to respond with project details
            response = self._respond_project_details(user_input)
            self.conversation_history.append(("bot", response))
            # Reset awaiting state after one project detail response
            self.awaiting_project_choice = False
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
                "Hmm, I didn't quite get that. Try asking about my education, skills, or projects.",
                "That's an interesting question. I can tell you about my professional background.",
                "Could you please ask about education, projects, or skills? I'd love to help!"
            ])

        self.conversation_history.append(("bot", response))
        return response


if __name__ == "__main__":
    bot = PortfolioBot()
    print("SayeesBot is ready! (type 'exit' or 'quit' to stop)")

    while True:
        user_text = input("You: ")
        if user_text.lower() in ['exit', 'quit']:
            print("SayeesBot: Goodbye! Have a great day.")
            break
        bot_response = bot.process_input(user_text)
        print("SayeesBot:", bot_response)
