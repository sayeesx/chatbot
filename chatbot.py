import os
import json
import difflib
from datetime import datetime
import random

class PortfolioBot:
    def __init__(self):
        """Initialize the bot with portfolio data and configuration"""
        self.data = self.load_data()
        
        # Update name and add role definition
        self.name = "AI Portfolio Assistant"
        self.role = "I am an AI assistant designed to provide information about Sayees's portfolio and professional background."
        self.last_interaction = None
        self.conversation_history = []

        # Enhanced NLP Configuration
        self.SPELLING_SENSITIVITY = 0.8  # Increased for better accuracy
        self.CONFIDENCE_THRESHOLD = 0.7  # Increased for more precise responses
        self.GREETINGS = [
            "hi", "hello", "hey", "greetings", "hi there", "hello there",
            "good morning", "good afternoon", "good evening"
        ]  # More formal greetings
        self.FAREWELLS = [
            "bye", "goodbye", "see you", "farewell", "thank you", "thanks",
            "exit", "quit", "end"
        ]  # More professional farewells

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
            "works": "project",
            "achievments": "achievements",
            "experiance": "experience",
            "certifications": "certifications",
            "methodology": "methodology",
            "expertise": "expertise",
            "specialization": "specialization",
            "leadership": "leadership",
            "technical": "technical",
            "programming": "programming"
        }

        # State for project conversation context
        self.awaiting_project_choice = False

        # To track last topic asked to vary responses
        self.last_response_type = None
        self.response_counters = {}

    def load_data(self):
        """Load portfolio data from environment variable or JSON file"""
        env_data = os.getenv("S_DATA_JSON")
        if env_data:
            try:
                return json.loads(env_data)
            except json.JSONDecodeError:
                print("Warning: Failed to parse S_DATA_JSON environment variable, falling back to file.")
        with open("sayees_data.json", "r") as f:
            return json.load(f)

    # ... rest of your class code unchanged ...


    def _build_keyword_map(self):
        """Enhanced keyword mapping with more variations and specific handlers"""
        return {
            # Personal & Background
            "name|who|sayees|who are you": self._respond_name,
            "age|birth|born|how old|when were you born": self._respond_personal_info,
            "background|bio|about|tell me about|profile|introduction": self._respond_background,
            "trading|investor|market|stock|crypto|forex": self._respond_trading_experience,
            "location|where|city|place|based|live": self._respond_current_location,
            "hometown|origin|from where|native": self._respond_hometown,
            
            # Education & Skills
            "education|university|college|degree|study|course|bca|student": self._respond_education,
            "skill|skills|technical|programming|coding|development|technology|tech stack|languages": self._respond_technical_background,
            "tools|software|technologies|platform|ide|framework": self._respond_tools_expertise,
            "certification|certificate|courses|credentials|qualified": self._respond_certifications,
            "language|speak|communication": self._respond_languages,
            "soft skills|interpersonal|professional skills": self._respond_skills,
            
            # Projects & Experience
            "project|portfolio|work|experience|developed|built|created": self._handle_projects_intro,
            "exquio|doctor|medical|appointment|healthcare": self._respond_exquio_details,
            "roamio|travel|guide|tourism": self._respond_roamio_details,
            "campus|portal|college system|complaint|management": self._respond_campus_portal_details,
            "internship|cyber square|work experience|job": self._respond_internship_details,
            
            # Contact & Professional
            "contact|reach|connect|get in touch|email|phone": self._respond_contact,
            "website|portfolio site|personal site": self._respond_portfolio_website,
            "github|code|repository|open source|git": self._respond_github_details,
            "linkedin|professional|network|social|profile": self._respond_linkedin_details,
            
            # Interests & Expertise
            "interest|passion|focus|specialization": self._respond_interests,
            "ai|artificial intelligence|machine learning|ml|deep learning": self._respond_technical_background,
            "web|frontend|backend|full stack": self._respond_technical_background
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
        """Enhanced time-based greeting"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning!"
        elif 12 <= hour < 17:
            return "Good afternoon!"
        else:
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
        """More structured and professional help response"""
        return ("I can provide information in the following categories:\n"
                "1. Professional Background: Education and qualifications\n"
                "2. Technical Skills: Programming languages and tools\n"
                "3. Projects: Detailed information about professional projects\n"
                "4. Professional Interests: Areas of expertise and focus\n"
                "5. Contact Information: Professional networking channels\n\n"
                "How may I assist you today?")

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
        """Enhanced greeting responses"""
        current_time = self._time_based_greeting()
        greetings_responses = [
            f"{current_time} I'm your AI Portfolio Assistant. How can I help you today?",
            f"{current_time} I'm here to tell you about Sayees's work and experience. What would you like to know?",
            f"{current_time} Welcome! I can share information about Sayees's projects, skills, and experience. What interests you?"
        ]
        return self._get_varied_response("greeting", greetings_responses)

    def _respond_farewell(self):
        """Enhanced farewell responses"""
        farewell_responses = [
            "Goodbye! Feel free to return if you have more questions.",
            "Thank you for your time! Have a great day!",
            "Farewell! Don't hesitate to ask if you need more information in the future."
        ]
        return self._get_varied_response("farewell", farewell_responses)

    def process_input(self, user_input):
        """Enhanced input processing with better matching"""
        user_input = user_input.lower().strip()
        
        # Handle empty input
        if not user_input:
            return "I'm ready to assist you. Could you please ask a question?"

        # Enhanced greeting detection with more variations
        greetings = [g.lower() for g in self.GREETINGS]
        if any(greeting in user_input for greeting in greetings):
            return self._respond_greeting()

        # Enhanced farewell detection with more variations
        farewells = [f.lower() for f in self.FAREWELLS]
        if any(farewell in user_input for farewell in farewells):
            return self._respond_farewell()

        # Handle help command and variations
        if any(word in user_input for word in ["help", "assist", "guide", "what can you do"]):
            return self._respond_help()

        # Handle project listing request with more variations
        if any(phrase in user_input for phrase in [
            "list projects", "show projects", "what projects", 
            "tell me about projects", "what have you built",
            "what did you make", "your projects"
        ]):
            return self._list_projects()

        # If awaiting project choice, handle that first
        if self.awaiting_project_choice:
            self.awaiting_project_choice = False
            return self._respond_project_details(user_input)

        # Enhanced keyword matching
        best_match = None
        highest_score = 0

        for pattern, handler in self.keyword_map.items():
            keywords = pattern.split('|')
            for keyword in keywords:
                # Check for exact matches first
                if keyword in user_input:
                    return handler()
                
                # Try fuzzy matching for longer inputs
                score = difflib.SequenceMatcher(None, keyword, user_input).ratio()
                if score > highest_score and score >= self.CONFIDENCE_THRESHOLD:
                    highest_score = score
                    best_match = handler

        # Use best match if found
        if best_match:
            return best_match()

        # If still no match, try to understand the intent
        common_phrases = {
            "tell me about": self._respond_background,
            "what is your": self._respond_background,
            "can you": self._respond_help,
            "do you": self._respond_help,
            "how to": self._respond_help,
            "skills": self._respond_technical_background,
            "experience": self._respond_internship_details,
            "projects": self._handle_projects_intro
        }

        for phrase, handler in common_phrases.items():
            if phrase in user_input:
                return handler()

        # Default response with suggestions
        return self._respond_unknown()

    def _respond_personal_info(self):
        """Handle questions about age, birth, etc."""
        responses = [
            f"I am {self.data['age']} years old, born in {self.data['birth']['year']} in {self.data['birth']['place']}.",
            f"I was born in {self.data['birth']['place']} in {self.data['birth']['year']}.",
            f"I'm a {self.data['age']}-year-old developer from {self.data['birth']['place']}."
        ]
        return self._get_varied_response("personal_info", responses)

    def _respond_trading_experience(self):
        """Handle questions about trading experience"""
        trading = self.data['trading_experience']
        responses = [
            f"I have {trading['years']} years of experience trading in {', '.join(trading['domains'])}.",
            f"As an {trading['role']}, I've been actively involved in {', '.join(trading['domains'])} for {trading['years']} years.",
            f"My trading journey spans {trading['years']} years across {', '.join(trading['domains'])}."
        ]
        return self._get_varied_response("trading", responses)

    def _respond_technical_background(self):
        """Handle questions about technical skills"""
        tech_skills = self.data['technical_skills']
        responses = [
            f"I'm proficient in {', '.join(tech_skills[:5])} among other technologies.",
            f"My technical stack includes {', '.join(tech_skills[:3])} as primary languages, along with frameworks like {', '.join([s for s in tech_skills if '.js' in s.lower()])}.",
            f"I work with various technologies including {', '.join(tech_skills[:4])}, specializing in AI and web development."
        ]
        return self._get_varied_response("technical", responses)

    def _respond_certifications(self):
        """Handle questions about certifications"""
        certs = self.data['certifications']
        responses = [
            f"I hold several certifications including {', '.join(certs[:3])}.",
            f"My key certifications are in {certs[0]} and {certs[1]}, along with {len(certs)-2} other credentials.",
            f"I've completed certifications from various organizations, notably {', '.join(certs[:3])}."
        ]
        return self._get_varied_response("certifications", responses)

    def _respond_exquio_details(self):
        """Handle specific questions about Exquio project"""
        project = next(p for p in self.data['projects'] if p['name'] == 'Exquio')
        responses = [
            f"Exquio is {project['description']} It's built using {', '.join(project['technologies'])}.",
            f"The Exquio project is a healthcare solution that {project['description'].lower()}",
            f"I developed Exquio using {', '.join(project['technologies'])}, creating {project['description'].lower()}"
        ]
        return self._get_varied_response("exquio", responses)

    def _respond_background(self):
        """Handle questions about background and bio"""
        responses = [
            f"{self.data['bio']} My current role is {self.data['role']}.",
            f"Here's a bit about me: {self.data['bio']}",
            f"{self.data['headline']} {self.data['bio']}"
        ]
        return self._get_varied_response("background", responses)

    def _respond_unknown(self):
        """Handle unknown or unclear queries"""
        responses = [
            f"I specialize in providing information about {self.data['name']}'s professional background and work. "
            "You can ask about:\n"
            "- Education and skills\n"
            "- Projects and experience\n"
            "- Technical expertise\n"
            "- Certifications\n"
            "- Contact information",
            
            f"I'm focused on sharing information about {self.data['name']}'s work in {self.data['role']}. "
            "Would you like to know about specific projects, skills, or experience?",
            
            "I may not have information about that topic. "
            f"I can tell you about {self.data['name']}'s background in {', '.join(self.data['interests'][:3])}. "
            "What would you like to know?"
        ]
        return random.choice(responses)

    def _respond_tools_expertise(self):
        """Handle questions about tools and technologies"""
        tools = self.data['tools']
        responses = [
            f"I'm experienced with {', '.join(tools[:5])} and other development tools.",
            f"My toolkit includes {', '.join(tools)} for development and deployment.",
            f"I work with various tools including {', '.join(tools[:3])} among others."
        ]
        return self._get_varied_response("tools", responses)

    def _respond_roamio_details(self):
        """Handle questions about Roamio project"""
        project = next(p for p in self.data['projects'] if p['name'] == 'Roamio')
        responses = [
            f"Roamio is {project['description']} It's built using {', '.join(project['technologies'])}.",
            f"The Roamio project is a travel platform that {project['description'].lower()}",
            f"I developed Roamio using {', '.join(project['technologies'])}, creating {project['description'].lower()}"
        ]
        return self._get_varied_response("roamio", responses)

    def _respond_campus_portal_details(self):
        """Handle questions about Campus Portal project"""
        project = next(p for p in self.data['projects'] if p['name'] == 'Campus Portal')
        responses = [
            f"The Campus Portal is {project['description']} It's built using {', '.join(project['technologies'])}.",
            f"The Campus Portal project {project['description'].lower()}",
            f"I developed the Campus Portal using {', '.join(project['technologies'])}, creating {project['description'].lower()}"
        ]
        return self._get_varied_response("campus_portal", responses)

    def _respond_internship_details(self):
        """Handle questions about internship experience"""
        exp = self.data['experience'][0]  # Assuming first experience is the internship
        responses = [
            f"I'm working as {exp['position']} at {exp['company']}, where I {', '.join(exp['description'])}.",
            f"At {exp['company']}, I {', '.join(exp['description'])}.",
            f"My internship at {exp['company']} involves {', '.join(exp['description'])}."
        ]
        return self._get_varied_response("internship", responses)

    def _respond_portfolio_website(self):
        """Handle questions about portfolio website"""
        website = self.data['contact']['portfolio']
        project = next(p for p in self.data['projects'] if p['name'] == 'Portfolio Website')
        responses = [
            f"You can visit my portfolio at {website}. {project['description']}",
            f"My portfolio website ({website}) {project['description'].lower()}",
            f"Check out my work at {website} - {project['description']}"
        ]
        return self._get_varied_response("portfolio", responses)

    def _respond_github_details(self):
        """Handle questions about GitHub"""
        github = self.data['contact']['github']
        responses = [
            f"You can find my code repositories on GitHub: {github}",
            f"Check out my projects on GitHub: {github}",
            f"My GitHub profile ({github}) showcases my development work."
        ]
        return self._get_varied_response("github", responses)

    def _respond_linkedin_details(self):
        """Handle questions about LinkedIn"""
        linkedin = self.data['contact']['linkedin']
        responses = [
            f"Let's connect on LinkedIn: {linkedin}",
            f"You can find my professional profile on LinkedIn: {linkedin}",
            f"For professional networking, reach me at {linkedin}"
        ]
        return self._get_varied_response("linkedin", responses)

if __name__ == "__main__":
    try:
        # Create bot instance
        bot = PortfolioBot()
        
        # Enhanced welcome message
        print("\n" + "="*50)
        print(f"{bot._time_based_greeting()} {bot.role}")
        print("="*50 + "\n")
        print("Tips:")
        print("1. Type 'help' to see available options")
        print("2. Type 'exit' or 'quit' to end the conversation")
        print("3. Ask about: education, projects, skills, experience\n")

        # Main conversation loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\nBot: Thank you for your time! Goodbye!")
                    break
                
                response = bot.process_input(user_input)
                print(f"\nBot: {response}\n")
                
            except KeyboardInterrupt:
                print("\nBot: Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"\nBot: I apologize, but I encountered an error. Please try rephrasing your question.")
                continue

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please ensure sayees_data.json is in the same directory as this script.")
