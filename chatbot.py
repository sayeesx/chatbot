import json
import os
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import get_close_matches
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformers, but don't fail if not available
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers library available")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ Transformers library not found. Using fallback responses.")

class PortfolioBot:
    def __init__(self, data_file: str = "sayees_data.json"):
                 # Check for grammar corrections
            corrected_input, has_corrections = self._correct_grammar(corrected_input)
            
            # Add to conversation history (use original input)
            self.conversation_history.append({"user": user_input, "timestamp": datetime.now()})
            
            # Classify intent using corrected input
            intent = self._classify_intent(corrected_input)
            
            # Handle affirmative/negative responses
            if intent in ['affirmative', 'negative']:
                last_bot_message = next((msg.get("bot", "") for msg in reversed(self.conversation_history) 
                                      if "bot" in msg), "")
                
                if intent == 'affirmative':
                    # If we were talking about skills
                    if any(keyword in last_bot_message.lower() for keyword in ['skills', 'tech stack', 'technologies']):
                        return self._show_next_project()
                    
                    # If we were talking about projects
                    elif 'project' in last_bot_message.lower():
                        return self._show_next_project()
                    
                    # If we asked about sharing something specific
                    elif '?' in last_bot_message:
                        if any(tech in last_bot_message.lower() for tech in ['ai', 'machine learning', 'data']):
                            # Show AI-related project
                            for project in self.data.get('projects', []):
                                if any(tech.lower() in ['ai', 'machine learning', 'python'] 
                                     for tech in project.get('technologies', [])):
                                    return f"Perfect! Let me tell you about {project['name']}: {project['description']}\n\nWant to know more about how I built it? 💡"
                
                elif intent == 'negative':
                    return "No problem! Here's what I can tell you about:\n\n🔹 My technical skills\n🔹 My projects\n🔹 My experience\n🔹 My education\n\nWhat interests you? 😊"
            
            # Update conversation state
            self.conversation_state['last_topic'] = intent
            self.conversation_state['awaiting_response'] = '?' in corrected_input
            
            # Generate response based on intent
            response = self._get_template_response(intent, corrected_input)
        
    def __init__(self, data_file: str = "sayees_data.json"):
        logger.info("🤖 Initializing PortfolioBot...")
        # Load personal portfolio data
        self.data = self._load_portfolio_data(data_file)
        # Initialize conversation history and state
        self.conversation_history = []
        self.context_memory = []
        self.conversation_state = {
            'last_topic': None,
            'awaiting_response': False,
            'offered_project': False,
            'current_project_index': 0,
            'last_question': None,
            'follow_up_options': []
        }
        # Setup AI model if available (disabled for Render deployment)
        self.model = None
        self.tokenizer = None
        # Commenting out AI model initialization for faster deployment
        # if TRANSFORMERS_AVAILABLE:
        #     self._initialize_model()
        # Generate context summary
        self.context = self._generate_context_summary()
        # Create easy access properties for Flask integration
        self.context_data = {
            'name': self.data.get('name', 'Muhammed Sayees'),
            'role': self.data.get('role', 'Software Developer & AI/ML Engineer'),
            'location': self.data.get('location', {}).get('current', 'India'),
            'skills': self.data.get('technical_skills', ['Programming']),
            'projects_count': len(self.data.get('projects', [])),
            'experience_years': self.data.get('trading_experience', {}).get('years', '2+')
        }
        # Predefined responses for common queries
        self.response_templates = self._setup_response_templates()
        # Define intent keywords for fuzzy matching
        self._setup_intent_keywords()
        # Setup response tracking to avoid repetition
        self._setup_response_tracking()
        # Setup grammar correction patterns
        self._setup_grammar_patterns()
        logger.info("✅ PortfolioBot initialized successfully!")

    def _load_portfolio_data(self, data_file: str) -> Dict:
        """Load portfolio data with error handling"""
        try:
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"✅ Loaded portfolio data from {data_file}")
                    return data
            else:
                logger.warning(f"⚠️ Data file {data_file} not found. Using fallback data.")
                return self._get_fallback_data()
        except Exception as e:
            logger.error(f"❌ Could not load {data_file}: {e}. Using fallback data.")
            return self._get_fallback_data()

    def _get_fallback_data(self) -> Dict:
        """Provide fallback data structure"""
        return {
            "name": "Muhammed Sayees",
            "role": "Software Developer & AI/ML Engineer",
            "education": {
                "current": {
                    "degree": "Bachelor's in Computer Science",
                    "specialization": "Computer Science & Engineering",
                    "college": "Engineering College",
                    "university": "University"
                }
            },
            "location": {
                "current": "Bengaluru, India",
                "hometown": "Kerala, India"
            },
            "experience": [
                {
                    "company": "Tech Company",
                    "role": "Software Development Intern",
                    "duration": "6 months",
                    "description": "Worked on web development and AI projects"
                }
            ],
            "projects": [
                {
                    "name": "AI Portfolio Bot",
                    "description": "Intelligent chatbot for portfolio website using Python and NLP",
                    "technologies": ["Python", "Flask", "NLP", "Machine Learning"]
                },
                {
                    "name": "Trading Analysis System",
                    "description": "Automated trading analysis tool for cryptocurrency and forex markets",
                    "technologies": ["Python", "Data Analysis", "Financial APIs"]
                },
                {
                    "name": "Web Development Projects",
                    "description": "Various full-stack web applications using modern frameworks",
                    "technologies": ["React", "Node.js", "Next.js", "MongoDB"]
                }
            ],
            "technical_skills": [
                "Python", "JavaScript", "React", "Next.js", "Node.js", 
                "Machine Learning", "AI/ML", "Web Development", "Flask", 
                "MongoDB", "SQL", "Git", "Docker"
            ],
            "languages": ["English", "Malayalam", "Hindi"],
            "trading_experience": {
                "years": "2+",
                "markets": ["Cryptocurrency", "Forex", "Stocks"],
                "description": "Active trader with experience in market analysis and risk management"
            }
        }

    def _generate_context_summary(self) -> str:
        """Create a comprehensive context summary"""
        try:
            education = self.data.get("education", {}).get("current", {})
            projects = self.data.get("projects", [])
            experience = self.data.get("experience", [])
            name = self.data.get('name', 'Sayees')
            role = self.data.get('role', 'Software Developer')
            location = self.data.get('location', {})
            languages = ', '.join(self.data.get('languages', ['English']))
            skills = ', '.join(self.data.get('technical_skills', ['Programming']))
            trading_years = self.data.get('trading_experience', {}).get('years', '2+')
            
            context = (
                f"I am {name}, a {role}.\n"
                f"I'm currently studying {education.get('degree', 'Computer Science')} in {education.get('specialization', 'Technology')} at {education.get('college', 'my college')}, {education.get('university', 'my university')}.\n\n"
                f"I'm based in {location.get('current', 'India')}, and my hometown is {location.get('hometown', 'Kerala')}.\n\n"
                f"{'I have internship experience at ' + experience[0].get('company', 'a tech company') + ' for ' + experience[0].get('duration', 'several months') + '.' if experience else 'I am gaining experience through various projects.'}\n\n"
                f"My key projects include:\n"
                f"{chr(10).join([f'• {p.get('name', 'Project')}: {p.get('description', 'Innovative solution')}' for p in projects[:3]])}\n\n"
                f"I'm fluent in {languages}, and my technical expertise includes {skills}.\n\n"
                f"I also have {trading_years} years of experience in financial trading across stocks, cryptocurrency, and forex markets."
            )
            return context.strip()
        except Exception as e:
            logger.error(f"Error generating context: {e}")
            return f"I am {self.data.get('name', 'Sayees')}, a software developer and AI enthusiast."

    def _initialize_model(self):
        """Initialize the AI model with proper error handling"""
        try:
            model_name = "microsoft/DialoGPT-small"
            
            logger.info("🤖 Loading AI model... This may take a moment.")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                padding_side="left",
                use_fast=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,
                torch_dtype="auto"
            )
            
            self.model = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info("✅ AI model loaded successfully!")
            
        except Exception as e:
            logger.error(f"⚠️ Could not load AI model: {e}")
            logger.info("🔄 Falling back to template-based responses.")
            self.model = None

    def _setup_grammar_patterns(self):
        """Setup common grammar correction patterns"""
        self.grammar_corrections = {
            # Common spelling mistakes
            r'\bwat\b': 'what',
            r'\bwher\b': 'where',
            r'\bwhen\b': 'when',
            r'\bhow\b': 'how',
            r'\btel\b': 'tell',
            r'\babut\b': 'about',
            r'\bskils\b': 'skills',
            r'\bprojcts\b': 'projects',
            r'\bexperiance\b': 'experience',
            r'\btradng\b': 'trading',
            r'\byour\b': 'your',
            r'\byou\b': 'you',
            r'\bcan\b': 'can',
            r'\bwil\b': 'will',
            r'\bwould\b': 'would',
            r'\bcould\b': 'could',
            r'\bshould\b': 'should',
            
            # Grammar patterns
            r'\bi am\b': 'I am',
            r'\bi\b': 'I',
            r'\byou is\b': 'you are',
            r'\bhe are\b': 'he is',
            r'\bshe are\b': 'she is',
            r'\bit are\b': 'it is',
            r'\bthey is\b': 'they are',
            r'\bwe is\b': 'we are',
        }

    def _correct_grammar(self, text: str) -> Tuple[str, bool]:
        """Correct basic grammar and spelling mistakes"""
        original_text = text
        corrected_text = text.lower()
        
        # Apply corrections
        for pattern, replacement in self.grammar_corrections.items():
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        # Capitalize first letter and after periods
        corrected_text = '. '.join(sentence.strip().capitalize() for sentence in corrected_text.split('.') if sentence.strip())
        
        # Check if any corrections were made
        has_corrections = original_text.lower() != corrected_text.lower()
        
        return corrected_text, has_corrections

    def _setup_response_templates(self) -> Dict[str, List[str]]:
        """Setup template responses for common queries"""
        name = self.data.get('name', 'Sayees')
        role = self.data.get('role', 'Software Developer')
        
        return {
            "greeting": [
                f"Hey! 👋 I'm {name}. What would you like to know?",
                f"Hi there! I'm {name}'s AI. How can I help?",
                "Hello! Ready to chat about tech and projects! What interests you?",
                f"Hi! 😊 Let's talk about my journey in tech. What's on your mind?",
                "Hey there! Want to hear about my latest projects?",
                "Hi! Ask me anything about coding, AI, or my projects!",
                "Hello! 🚀 What would you like to explore first?"
            ],
            "name_intro": [
                f"I'm {name}, a {role} passionate about AI and technology.",
                f"My name is {name}, and I specialize in software development and machine learning.",
                f"I'm {name} - a tech enthusiast working in software development and AI/ML engineering.",
                f"You can call me {name}! I'm a developer focused on creating innovative AI and web solutions.",
                f"I'm {name}, currently pursuing my passion in software development while building expertise in AI and machine learning.",
                f"Nice to meet you! I'm {name}, a software developer who loves working with cutting-edge technologies like AI and machine learning."
            ],
            "weather": [
                "I don't have access to real-time weather data, but I can tell you about the climate of innovation in my coding projects! 🌟 Speaking of which, would you like to hear about my latest tech projects?",
                "While I can't check the weather for you, I can tell you it's always sunny in the world of programming! ☀️ Want to know about my development work?",
                "I'm not a weather bot, but I can forecast that you'll find my portfolio projects quite interesting! 🌈 What would you like to explore?",
                "The weather outside might be unpredictable, but my coding skills are consistently reliable! 💻 Care to learn about my technical expertise?"
            ],
            "jokes": [
                "Why do programmers prefer dark mode? Because light attracts bugs! 😄 Speaking of programming, want to hear about my coding projects?",
                "Here's a tech joke: Why do Java developers wear glasses? Because they don't C#! 😂 By the way, I work with both languages - want to know more?",
                "Why did the developer go broke? Because he used up all his cache! 💸 I've got better financial sense in my trading projects though!",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡 But I can solve software problems - check out my projects!",
                "Why don't programmers like nature? It has too many bugs! 🐛 Unlike my clean code - want to see some examples?"
            ],
            "general_knowledge": [
                "🤔 Interesting! That reminds me of a project where I used similar concepts. Want to hear about it?",
                "Cool topic! I actually applied related ideas in my AI work. Shall I explain?",
                "You know, this connects nicely with my tech experience. Want me to share how?",
                "That's fascinating! It's like how in programming... want me to draw the parallel?",
                "Speaking of that - it's similar to a challenge I solved in my projects. Curious to know more?"
            ],
            "compliments": [
                "Thank you so much! That's very kind of you to say. I really appreciate it! 😊 Is there anything specific about my work you'd like to know more about?",
                "Aww, that's really sweet! Thank you for the kind words. 🙏 What aspect of my portfolio caught your attention?",
                "That means a lot to me, thank you! I'm glad you think so. What would you like to explore about my background?",
                "You're too kind! I really appreciate the compliment. 😄 What interests you most about my technical journey?"
            ],
            "casual_conversation": [
                "You know what? I just completed an exciting AI project! Want to hear about it? 🚀",
                "Speaking of that - I recently worked on a cool project using AI and web tech. Interested?",
                "That reminds me of my latest project in machine learning! Want me to share it?",
                "Hey! I've got something exciting to share about my recent work in tech. Shall I tell you more?",
                "Actually, this connects perfectly with my latest project. Want to know how? 🤖",
                "I've got a really interesting project that relates to this! Want to hear about it?"
            ],
            "food_cooking": [
                "I don't cook much code... I mean food! 😄 But I do 'cook up' some pretty tasty algorithms and applications. Want to see my recipe for success in programming?",
                "While I can't share cooking recipes, I can share my recipe for building great software projects! Interested in the ingredients?",
                "Food is great, but have you tried the satisfaction of debugging clean code? It's quite delicious! 🍰 Want to taste some of my programming projects?",
                "I'm more of a code chef than a kitchen chef! My specialty is serving up fresh web applications and AI solutions. Care for a sample?"
            ],
            "movies_entertainment": [
                "I enjoy a good movie! Though I spend more time creating interactive experiences through web development. Want to see some of my digital entertainment projects?",
                "Movies are great! I actually find inspiration for my UI/UX designs from cinematography. Would you like to see how I apply visual storytelling in my projects?",
                "Entertainment is important! I create my own entertainment by building cool applications and trading systems. Want to see what I've been working on?",
                "I love good storytelling! In fact, every project I build tells a story of problem-solving and innovation. Interested in hearing those stories?"
            ],
            "music": [
                "Music is awesome! I find that coding has its own rhythm - there's something musical about clean, well-structured code. Want to see the symphony of my projects?",
                "I appreciate good music! Interestingly, I apply similar pattern recognition skills in both music appreciation and my machine learning projects. Care to explore?",
                "Music and code both follow patterns and structures! I've actually worked on some audio-related programming projects. Would you like to hear about them?",
                "Great taste in topics! While I enjoy music, I create my own kind of harmony through elegant code architecture. Want to see my compositions?"
            ],
            "sports": [
                "Sports are exciting! I apply the same strategic thinking from sports to my trading strategies and project planning. Want to know about my analytical approach?",
                "I appreciate the competitive spirit in sports! I bring that same drive to my coding challenges and technical projects. Interested in my achievements?",
                "Sports teach great lessons about teamwork and perseverance - qualities I use in my software development work. Want to hear about my collaborative projects?",
                "The strategy in sports reminds me of algorithmic thinking in programming! I love applying game theory concepts in my projects. Care to explore?"
            ],
            "travel": [
                "Travel broadens perspectives! My coding journey has taken me through many different technologies and frameworks - it's like traveling through the tech world. Want to see my itinerary?",
                "I love the idea of exploration! I explore new programming languages and technologies the way others explore new places. Want to join my tech adventure?",
                "Travel is amazing! While I haven't traveled much physically, I've journeyed through various programming paradigms and tech stacks. Interested in my technical travels?",
                "Different places, different cultures - just like different programming languages have different philosophies! Want to see my multilingual coding skills?"
            ],
            "inappropriate": [
                "I prefer to keep our conversation professional and focused on my portfolio. Let's talk about something more constructive - like my technical projects or career journey!",
                "Let's steer this conversation in a more positive direction! I'd love to share my professional achievements and technical skills instead.",
                "I'm here to maintain a respectful conversation about my work and experience. What aspect of my professional background interests you?",
                "I'd rather focus on my professional accomplishments and technical expertise. What would you like to know about my projects or skills?"
            ],
            "error": [
                "Oops! Something went wrong on my end. Could you try rephrasing that? I'm here to help! 🤖",
                "I encountered a little hiccup there! Mind trying that again? I'm excited to assist you!",
                "Sorry about that technical glitch! Could you give it another shot? I'm ready to help!",
                "My circuits got a bit tangled there! 😅 Please try again - I'm here to help you explore my portfolio!"
            ],
            "unclear": [
                "Hi! 👋 I'm your AI assistant! Ask me about my skills, projects, or experience!",
                "Hey there! 😊 Want to know about my tech journey? Ask away!",
                "Hello! I'd love to tell you about my projects and skills. What interests you?",
                "Hi! Let's chat about coding, AI, or any of my other tech adventures! 🚀"
            ],
            "goodbye": [
                "Thanks for chatting with me! It was great talking about my portfolio. Feel free to come back anytime! 👋",
                "Goodbye! I hope you learned something interesting about my background. Have a wonderful day! 🌟",
                "It was a pleasure talking with you! Thanks for your interest in my work. See you later! 😊",
                "Take care! I enjoyed sharing my professional journey with you. Come back soon! 🚀"
            ]
        }

    def _get_varied_response(self, response_type: str, fallback_message: str = None) -> str:
        """Get a varied response to avoid repetition"""
        if response_type in self.response_templates:
            available_responses = self.response_templates[response_type]
            
            # Filter out recently used responses
            unused_responses = [r for r in available_responses if r not in self.recent_responses]
            
            # If all responses have been used recently, reset and use all
            if not unused_responses:
                self.recent_responses = []
                unused_responses = available_responses
            
            # Select a random unused response
            selected_response = random.choice(unused_responses)
            
            # Track this response
            self.recent_responses.append(selected_response)
            if len(self.recent_responses) > self.max_recent_responses:
                self.recent_responses.pop(0)
            
            return selected_response
        
        return fallback_message or "I'm here to help you learn about my professional background."

    def _setup_intent_keywords(self):
        """Setup keywords for each intent category for fuzzy matching"""
        self.intent_keywords = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "hola", "yo", "what's up", "wassup"],
            "name_intro": ["name", "who are you", "introduce", "about you", "sayees", "who is", "tell me about yourself", "your name"],
            "skills": ["skills", "technical", "programming", "languages", "technologies", "expertise", "stack", "tech stack", "coding", "develop", "software", "framework", "library", "tool"],
            "projects": ["projects", "work", "portfolio", "built", "created", "developed", "github", "showcase", "demo", "application", "app", "website", "system", "platform"],
            "experience": ["experience", "internship", "job", "work history", "career", "professional", "industry", "company", "employment", "worked", "role", "position"],
            "education": ["education", "study", "college", "university", "degree", "qualification", "academic", "school", "course", "major", "graduate", "student"],
            "contact": ["contact", "reach", "email", "phone", "connect", "hire", "recruiting", "message", "get in touch", "social media", "linkedin"],
            "trading": ["trading", "crypto", "cryptocurrency", "forex", "stocks", "investment", "market", "finance", "financial", "trade", "investor", "portfolio", "asset"],
            "weather": ["weather", "temperature", "rain", "sunny", "cloudy", "forecast", "climate"],
            "jokes": ["joke", "funny", "humor", "laugh", "comedy", "amusing", "hilarious"],
            "food": ["food", "cooking", "recipe", "eat", "meal", "dinner", "lunch", "breakfast", "restaurant"],
            "movies": ["movie", "film", "cinema", "watch", "netflix", "entertainment", "actor", "actress"],
            "music": ["music", "song", "artist", "band", "listen", "spotify", "album", "concert"],
            "sports": ["sports", "football", "basketball", "cricket", "game", "team", "player", "match"],
            "travel": ["travel", "trip", "vacation", "country", "city", "visit", "tourism", "journey"],
            "compliment": ["good", "great", "awesome", "amazing", "excellent", "wonderful", "fantastic", "brilliant", "smart", "talented"],
            "goodbye": ["bye", "goodbye", "see you", "farewell", "take care", "later", "exit", "quit"]
        }
        
        # Flatten all keywords for quick lookup
        self.all_keywords = []
        for category, words in self.intent_keywords.items():
            self.all_keywords.extend(words)

    def _setup_response_tracking(self):
        """Setup response tracking to avoid repetition"""
        self.recent_responses = []
        self.max_recent_responses = 5

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra spaces, punctuation, and converting to lowercase"""
        text = text.lower()
        text = re.sub(r'[^\w\s\']', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract words from text for fuzzy matching"""
        normalized = self._normalize_text(text)
        words = normalized.split()
        
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                     'be', 'been', 'being', 'to', 'of', 'for', 'with', 'by', 'about', 
                     'against', 'between', 'into', 'through', 'during', 'before', 'after',
                     'above', 'below', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 
                     'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
                     'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
                     'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
                     'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
                     'should', 'now'}
        
        return [word for word in words if len(word) > 2 and word not in stop_words]

    def _classify_intent(self, user_input: str) -> str:
        """Classify user intent based on keywords and context with improved fuzzy matching"""
        user_input_lower = user_input.lower().strip()
        
        # Check for yes/no responses first
        if user_input_lower in ['yes', 'yeah', 'sure', 'okay', 'ok', 'yep', 'yup', 'y']:
            return 'affirmative'
        if user_input_lower in ['no', 'nah', 'nope', 'not really', 'n']:
            return 'negative'
        
        # Handle common partial words
        partial_word_mappings = {
            'proj': 'projects',
            'projec': 'projects',
            'tech': 'skills',
            'exp': 'experience',
            'edu': 'education',
            'lang': 'skills',
            'frame': 'skills',
            'tool': 'skills',
            'data': 'skills',
            'web': 'skills',
            'dev': 'skills',
            'cont': 'contact'
        }
        
        # Check if input is a partial word
        if user_input_lower in partial_word_mappings:
            user_input_lower = partial_word_mappings[user_input_lower]
        
        # Check for inappropriate content first
        inappropriate_words = [
            "sex", "dating", "relationship", "personal life", "family", "girlfriend", "boyfriend",
            "politics", "religion", "controversial", "offensive", "illegal", "drugs", "violence"
        ]
        
        if any(word in user_input_lower for word in inappropriate_words):
            return "inappropriate"
        
        # Extract keywords from user input
        input_keywords = self._extract_keywords(user_input)
        
        if not input_keywords:
            return "unclear"
        
        # Try fuzzy matching for each keyword in user input
        matched_intents = {}
        
        for user_word in input_keywords:
            matches = get_close_matches(user_word, self.all_keywords, n=3, cutoff=0.75)
            
            if matches:
                for match in matches:
                    for intent, keywords in self.intent_keywords.items():
                        if match in keywords:
                            matched_intents[intent] = matched_intents.get(intent, 0) + 1
        
        # If we found matches, return the intent with the most matches
        if matched_intents:
            return max(matched_intents.items(), key=lambda x: x[1])[0]
        
        # Default to general conversation for unmatched queries
        return "general_conversation"

    def _get_template_response(self, intent: str, user_input: str) -> str:
        """Generate response based on intent and templates with context echoing and humor"""
        
        # Echo back relevant context when possible
        context_echo = ""
        keywords = self._extract_keywords(user_input)
        if keywords:
            relevant_word = keywords[0]
            context_echo = f"About {relevant_word}? "
        
        if intent == "greeting":
            return self._get_varied_response("greeting")
        
        elif intent == "goodbye":
            return self._get_varied_response("goodbye")
        
        elif intent == "name_intro":
            return self._get_varied_response("name_intro")
        
        elif intent == "skills":
            skills = self.data.get('technical_skills', ['Programming'])
            # Group skills by category
            categories = {
                'Languages': ['Python', 'C', 'C++', 'JavaScript', 'SQL'],
                'Frameworks': ['React Native', 'Next.js', 'Node.js', 'Express.js'],
                'Frontend': ['HTML', 'CSS', 'Tailwind CSS'],
                'Databases': ['Firebase', 'Supabase', 'MySQL'],
                'Tools': ['Git', 'Docker', 'VS Code', 'Figma', 'Postman']
            }
            
            # Format skills by category
            formatted_skills = []
            for category, cat_skills in categories.items():
                matched_skills = [s for s in cat_skills if s in skills]
                if matched_skills:
                    formatted_skills.append(f"🔹 {category}: {', '.join(matched_skills)}")
            
            base_responses = [
                f"Here are my key technical skills:\n\n{chr(10).join(formatted_skills[:3])}\n\nWant to know more about any specific technology? Just ask! 🚀",
                f"I'm proficient in various technologies:\n\n{chr(10).join(formatted_skills[:3])}\n\nCurious about my projects with these technologies? Let me know! 💻",
                f"My tech stack includes:\n\n{chr(10).join(formatted_skills[:3])}\n\nI'd love to tell you about how I use these in my projects! 🛠️"
            ]
            return random.choice(base_responses)
        
        elif intent == "projects":
            projects = self.data.get('projects', [])
            if projects:
                # Check for "more" in user input to determine if user wants to see more projects
                if "more" in user_input.lower() or user_input.lower() in ["yes", "yeah", "sure", "okay", "ok", "yep", "yup"]:
                    # Show next set of projects
                    project_history = next((msg for msg in reversed(self.conversation_history) if "project" in msg.get("bot", "").lower()), None)
                    shown_count = 1 if project_history is None else len([line for line in project_history.get("bot", "").split("\n") if line.strip().startswith(("1.", "2.", "3.", "4.", "5."))])
                    remaining = len(projects) - shown_count
                    
                    if remaining <= 0:
                        return "That's all the projects I have! But I'd be happy to dive deeper into any specific project that interests you!"
                    
                    start_idx = shown_count
                    end_idx = min(shown_count + 2, len(projects))
                    
                    project_list = []
                    for i, project in enumerate(projects[start_idx:end_idx], start_idx + 1):
                        name = project.get('name', 'Project')
                        desc = project.get('description', 'Innovative solution')
                        tech = project.get('technologies', [])
                        tech_str = f" (Technologies: {', '.join(tech[:3])})" if tech else ""
                        project_list.append(f"{i}. {name}: {desc}{tech_str}")
                    
                    more_projects = len(projects) - end_idx
                    more_text = f"\n\nI have {more_projects} more projects! Want to see them? Just ask for more! 🚀" if more_projects > 0 else ""
                    return "Here are some more of my projects:\n\n" + "\n".join(project_list) + more_text
                
                # Show first project only initially
                project = projects[0]
                name = project.get('name', 'Project')
                desc = project.get('description', 'Innovative solution')
                tech = project.get('technologies', [])
                tech_str = f" (Technologies: {', '.join(tech[:3])})" if tech else ""
                
                intros = [
                    "Let me showcase one of my favorite projects:",
                    "Here's a highlight from my portfolio:",
                    "I'm particularly proud of this project:",
                    "Let me start with this exciting project:"
                ]
                
                return f"{random.choice(intros)}\n\n1. {name}: {desc}{tech_str}\n\nI have {len(projects)-1} more cool projects! Want to see them? Just ask! 😊"
            else:
                return self._get_varied_response("projects")
        
        elif intent == "experience":
            experience = self.data.get('experience', [])
            if experience:
                exp = experience[0]
                base_responses = [
                    f"I have internship experience at {exp.get('company', 'a tech company')} as a {exp.get('role', 'intern')} for {exp.get('duration', 'several months')}, where I gained valuable industry experience.",
                    f"I've worked as a {exp.get('role', 'intern')} at {exp.get('company', 'a tech company')} for {exp.get('duration', 'several months')}, which gave me great hands-on experience.",
                    f"My professional journey includes a {exp.get('duration', 'several months')} role as {exp.get('role', 'intern')} at {exp.get('company', 'a tech company')}, where I developed practical skills.",
                    f"I gained valuable industry exposure through my {exp.get('duration', 'several months')} position at {exp.get('company', 'a tech company')}."
                ]
                return random.choice(base_responses)
            else:
                return "I'm currently building my professional experience through projects and continuous learning in the tech industry."
        
        elif intent == "education":
            education = self.data.get('education', {}).get('current', {})
            base_responses = [
                f"I'm currently pursuing {education.get('degree', 'my degree')} in {education.get('specialization', 'Computer Science')} at {education.get('college', 'my college')}, {education.get('university', 'my university')}.",
                f"I'm studying {education.get('specialization', 'Computer Science')} for my {education.get('degree', 'degree')} at {education.get('college', 'my college')}, {education.get('university', 'my university')}.",
                f"My academic journey involves pursuing {education.get('degree', 'my degree')} in {education.get('specialization', 'Computer Science')} from {education.get('college', 'my college')}, {education.get('university', 'my university')}.",
                f"I'm currently enrolled in {education.get('degree', 'my degree')} program specializing in {education.get('specialization', 'Computer Science')} at {education.get('college', 'my college')}, {education.get('university', 'my university')}."
            ]
            return random.choice(base_responses)
        
        elif intent == "contact":
            base_responses = [
                "You can find my contact information and connect with me through the contact section of this portfolio website.",
                "Feel free to reach out through the contact details available on this portfolio site!",
                "I'd love to connect! Check out the contact section of this website for ways to get in touch.",
                "You can contact me using the information provided in the contact section of this portfolio."
            ]
            return random.choice(base_responses)
        
        elif intent == "trading":
            trading_info = self.data.get('trading_experience', {})
            years = trading_info.get('years', '2+')
            markets = trading_info.get('markets', ['stocks', 'cryptocurrency', 'forex'])
            base_responses = [
                f"Yes, I have {years} years of experience trading in {', '.join(markets)}. It's taught me a lot about market analysis and risk management.",
                f"I've been actively trading for {years} years across {', '.join(markets)}. It's given me valuable insights into financial markets and analytical thinking.",
                f"Trading has been a passion of mine for {years} years! I work with {', '.join(markets)}, which has sharpened my analytical and decision-making skills.",
                f"I have {years} years of hands-on trading experience in various markets including {', '.join(markets)}. It's been an excellent complement to my technical skills."
            ]
            return random.choice(base_responses)
        
        elif intent == "weather":
            return self._get_varied_response("weather")
        
        elif intent == "jokes":
            return self._get_varied_response("jokes")
        
        elif intent == "food":
            return self._get_varied_response("food_cooking")
        
        elif intent == "movies":
            return self._get_varied_response("movies_entertainment")
        
        elif intent == "music":
            return self._get_varied_response("music")
        
        elif intent == "sports":
            return self._get_varied_response("sports")
        
        elif intent == "travel":
            return self._get_varied_response("travel")
        
        elif intent == "compliment":
            return self._get_varied_response("compliments")
        
        elif intent == "inappropriate":
            return self._get_varied_response("inappropriate")
        
        elif intent == "unclear":
            return self._get_varied_response("unclear")
        
        elif intent == "general_conversation":
            return self._get_varied_response("casual_conversation")
        
        else:
            # For any other queries, provide a helpful general response
            return self._get_varied_response("general_knowledge")

    def _is_portfolio_related(self, user_input: str) -> bool:
        """Determine if the query is portfolio-related with fuzzy matching for typos"""
        portfolio_keywords = [
            "sayees", "portfolio", "skills", "projects", "experience", "education", 
            "name", "who", "what", "about", "tell me", "trading", "developer",
            "programming", "technical", "software", "ai", "ml", "machine learning",
            "internship", "college", "university", "contact", "hire", "recruiting",
            "github", "code", "development", "technology", "career", "professional",
            "crypto", "cryptocurrency", "forex", "stocks", "market", "analysis"
        ]
        
        input_keywords = self._extract_keywords(user_input)
        
        for word in input_keywords:
            matches = get_close_matches(word, portfolio_keywords, n=1, cutoff=0.8)
            if matches:
                return True
                
        return False

    async def process_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response with improved LLM-like flow"""
        try:
            user_input = user_input.strip()
            if not user_input:
                return "Please ask me something! I'm here to help."

            # Check for grammar corrections and possible suggestions
            corrected_input, has_corrections = self._correct_grammar(user_input)
            suggestion = None
            # Try to suggest a close known intent if input is unclear
            if has_corrections and corrected_input != user_input.lower():
                suggestion = corrected_input
            else:
                all_keywords = []
                for klist in self.intent_keywords.values():
                    all_keywords.extend(klist)
                from difflib import get_close_matches
                close = get_close_matches(user_input.lower(), all_keywords, n=1, cutoff=0.7)
                if close:
                    suggestion = close[0]

            # Classify intent
            intent = self._classify_intent(corrected_input)

            # Add to conversation history
            self.conversation_history.append({"user": user_input, "timestamp": datetime.now()})

            # Enhanced: Track repeated 'affirmative' responses
            if not hasattr(self, '_affirmative_count'):
                self._affirmative_count = 0
            if not hasattr(self, '_affirmative_topic_cycle'):
                self._affirmative_topic_cycle = ['skills', 'projects', 'experience', 'education', 'trading']
            if not hasattr(self, '_affirmative_topic_index'):
                self._affirmative_topic_index = 0


            # Handle yes/no responses with improved context
            if intent in ['affirmative', 'negative']:
                last_bot_message = next((msg.get("bot", "") for msg in reversed(self.conversation_history) if "bot" in msg), "")
                # If last bot message was a clarification question
                if 'did you mean' in last_bot_message.lower():
                    if intent == 'affirmative':
                        return self._get_template_response(self._classify_intent(suggestion or user_input), suggestion or user_input)
                    else:
                        return "No worries! If you want, you can ask about my skills, projects, experience, or just say a topic you're interested in!"

                # Only cycle topics if bot is awaiting a follow-up (e.g., after offering more info)
                if intent == 'affirmative' and self.conversation_state.get('awaiting_response', False):
                    self._affirmative_count += 1
                    # If last topic is set, move to next topic in cycle
                    if self.conversation_state.get('last_topic') in self._affirmative_topic_cycle:
                        idx = self._affirmative_topic_cycle.index(self.conversation_state['last_topic'])
                        next_idx = (idx + 1) % len(self._affirmative_topic_cycle)
                        self._affirmative_topic_index = next_idx
                    # Pick topic to share
                    topic = self._affirmative_topic_cycle[self._affirmative_topic_index]
                    self.conversation_state['last_topic'] = topic
                    self._affirmative_topic_index = (self._affirmative_topic_index + 1) % len(self._affirmative_topic_cycle)
                    # Reset count if cycled through all
                    if self._affirmative_count > len(self._affirmative_topic_cycle):
                        self._affirmative_count = 1
                    # Share info about the topic
                    response = self._get_template_response(topic, user_input)
                    # If at end of cycle, offer open-ended question
                    if self._affirmative_topic_index == 0:
                        response += "\n\nIs there a specific area you'd like to dive deeper into, or should I keep sharing more? 😊"
                    # After cycling, set awaiting_response to False unless user asks for more
                    self.conversation_state['awaiting_response'] = False
                    return response
                else:
                    self._affirmative_count = 0
                    # If not awaiting a follow-up, just acknowledge and offer a friendly open-ended prompt
                    return random.choice([
                        "👍 Got it! If you want to know more about my skills, projects, or experience, just ask!",
                        "Alright! Let me know if you want to dive into any topic—skills, projects, or anything else!",
                        "Okay! If you have a specific question or want to explore something, feel free to say so! 😊",
                        "Noted! I'm here if you want to chat about my portfolio, tech, or anything else!"
                    ])

            # Reset affirmative count if not a yes/no
            self._affirmative_count = 0



            # Improved: Only suggest if suggestion is meaningfully different and not a known intent
            # Don't suggest if suggestion is the same as input, or if input is a known intent (like greeting)
            known_intents = set()
            for klist in self.intent_keywords.values():
                known_intents.update(klist)

            # Detect gibberish/random input (no intent, no suggestion, or input is mostly non-words)
            def is_gibberish(text):
                # If text is short, not a known intent, and contains no real words
                if len(text) < 5 and not text.isalpha():
                    return True
                # If text is mostly consonants or repeated chars
                if re.fullmatch(r'(.)\1{2,}', text):
                    return True
                # If text has no vowels and is not a number
                if not re.search(r'[aeiou]', text.lower()) and not text.isdigit():
                    return True
                # If text is a single word and not in known intents and not a real word
                if len(text.split()) == 1 and text.lower() not in known_intents and not re.match(r'^[a-zA-Z]+$', text):
                    return True
                return False

            if (
                (intent == 'unclear' or intent == 'general_conversation')
                and (not suggestion or suggestion == corrected_input)
                and is_gibberish(user_input)
            ):
                humour = random.choice([
                    "I didn't quite catch that. Did your cat walk across the keyboard? 😺",
                    "Oops, I didn't understand that. Maybe your keyboard is speaking in tongues!",
                    "That looks like a secret code! If you want to know about my skills or projects, just ask!",
                    "Hmm, that doesn't look like a question. Want to know about my skills, projects, or anything else about me?",
                    "I didn't understand that. But I'm great at talking about tech, not so much at deciphering keyboard art!"
                ])
                return humour

            # If suggestion is not the same as input, not a known intent, and intent is unclear/general
            if (
                (intent == 'unclear' or intent == 'general_conversation')
                and suggestion
                and suggestion != corrected_input
                and suggestion not in known_intents
                and corrected_input not in known_intents
            ):
                return f"Did you mean '{suggestion}'? (yes/no) If not, you can ask about my skills, projects, or anything else."

            # Update conversation state
            self.conversation_state['last_topic'] = intent
            self.conversation_state['awaiting_response'] = True

            # Generate response based on intent
            response = self._get_template_response(intent, corrected_input)
            return response
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return "Oops! Something went wrong. Please try again or ask me about my skills, projects, or experience."

    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("✅ Conversation history cleared!")

    def get_portfolio_summary(self) -> str:
        """Get a comprehensive portfolio summary"""
        return self.context

    def get_context_data(self) -> Dict:
        """Get context data as dictionary for web integration"""
        return self.context_data

    def _show_next_project(self) -> str:
        """Show the next project based on conversation state"""
        projects = self.data.get('projects', [])
        if not projects:
            return "I'd love to show you my projects, but I'm currently working on adding them! Want to hear about my skills instead? 🔧"
        
        current_idx = self.conversation_state.get('current_project_index', 0)
        if current_idx >= len(projects):
            return "Those are all my projects! What else would you like to know about? My skills? Experience? 🎯"
            
        project = projects[current_idx]
        self.conversation_state['current_project_index'] = current_idx + 1
        
        response = f"Let me tell you about {project['name']}: {project['description']}"
        if project.get('technologies'):
            response += f"\n\nI built this using {', '.join(project['technologies'][:3])} 🛠️"
        response += "\n\nWant to see another project? 🚀"
        
        return response

    def _show_detailed_skills(self) -> str:
        """Show detailed skills with examples and projects"""
        skills = self.data.get('technical_skills', ['Programming'])
        projects = self.data.get('projects', [])
        
        # Get a random project that uses the most mentioned skills
        if projects:
            project = random.choice(projects)
            project_techs = project.get('technologies', [])
            skill_example = f"\nFor example, I used {', '.join(project_techs[:3])} in my {project['name']} project."
        else:
            skill_example = ""
            
        categories = {
            '🔹 Core Languages': ['Python', 'JavaScript', 'C', 'C++', 'SQL'],
            '🔹 Web Technologies': ['React Native', 'Next.js', 'Node.js', 'HTML', 'CSS', 'Tailwind'],
            '🔹 AI & Data': ['TensorFlow', 'Machine Learning', 'Data Analysis', 'NLP'],
            '🔹 Tools & DevOps': ['Git', 'Docker', 'VS Code', 'Postman']
        }
        
        response = "Here's a detailed look at my technical skills:\n\n"
        for category, cat_skills in categories.items():
            matched = [s for s in cat_skills if s in skills]
            if matched:
                response += f"{category}: {', '.join(matched)}\n"
        
        response += f"{skill_example}\n\nWould you like to see some of my projects using these technologies? 🚀"
        
        self.conversation_state['awaiting_response'] = True
        self.conversation_state['offered_project'] = True
        return response

    def get_basic_info(self) -> Dict:
        """Get basic information for web display"""
        return {
            'name': self.data.get('name', 'Muhammed Sayees'),
            'role': self.data.get('role', 'Software Developer & AI/ML Engineer'),
            'location': self.data.get('location', {}).get('current', 'India'),
            'hometown': self.data.get('location', {}).get('hometown', 'Kerala'),
            'skills': self.data.get('technical_skills', ['Programming']),
            'languages': self.data.get('languages', ['English']),
            'projects': self.data.get('projects', []),
            'experience': self.data.get('experience', []),
            'education': self.data.get('education', {}),
            'trading_years': self.data.get('trading_experience', {}).get('years', '2+')
        }

# Add this at the end of chatbot.py
async def interactive_chat():
    """Run an interactive chat session with the bot"""
    print("\n" + "="*60)
    print("🤖 ENHANCED PORTFOLIO BOT - NOW WITH AI-LIKE RESPONSES!")
    print("="*60)
    print("✨ NEW FEATURES:")
    print("• Responds to jokes, weather, movies, music, and more!")
    print("• Grammar and spelling correction")
    print("• Natural conversation while focusing on portfolio")
    print("• Friendly and helpful like a real AI assistant")
    print("\nType 'exit', 'quit', or 'bye' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("-"*60 + "\n")
    
    bot = PortfolioBot()
    print("Bot: Hello! I'm an enhanced AI assistant that loves to chat about anything, but I'm especially excited to share my creator's amazing portfolio! What's on your mind today? 😊")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            response = await bot.process_input(user_input)
            print(f"\nBot: {response}")
            break
            
        if user_input.lower() == 'clear':
            bot.clear_history()
            print("Bot: Conversation history cleared! Ready for a fresh start! 🚀")
            continue
            
        if not user_input:
            continue
            
        response = await bot.process_input(user_input)
        print(f"\nBot: {response}")

# Run the interactive chat if this file is executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(interactive_chat())
