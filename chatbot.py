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
        """Initialize the chatbot with personal data and AI model"""
        
        logger.info("🤖 Initializing PortfolioBot...")
        
        # Load personal portfolio data
        self.data = self._load_portfolio_data(data_file)
        
        # Initialize conversation history
        self.conversation_history = []
        self.context_memory = []
        
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
            
            context = f"""I am {self.data.get('name', 'Sayees')}, a {self.data.get('role', 'Software Developer')}. 
I'm currently studying {education.get('degree', 'Computer Science')} in {education.get('specialization', 'Technology')} 
at {education.get('college', 'my college')}, {education.get('university', 'my university')}.

I'm based in {self.data.get('location', {}).get('current', 'India')}, 
and my hometown is {self.data.get('location', {}).get('hometown', 'Kerala')}.

{'I have internship experience at ' + experience[0].get('company', 'a tech company') + ' for ' + experience[0].get('duration', 'several months') + '.' if experience else 'I am gaining experience through various projects.'}

My key projects include:
{chr(10).join([f"• {p.get('name', 'Project')}: {p.get('description', 'Innovative solution')}" for p in projects[:3]])}

I'm fluent in {', '.join(self.data.get('languages', ['English']))}, 
and my technical expertise includes {', '.join(self.data.get('technical_skills', ['Programming']))}.

I also have {self.data.get('trading_experience', {}).get('years', '2+')} years of experience 
in financial trading across stocks, cryptocurrency, and forex markets."""
            
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
                f"Hello! I'm {name}'s AI assistant. How can I help you learn more about my background and projects?",
                f"Hi there! Welcome to {name}'s portfolio. What would you like to know?",
                "Greetings! I'm here to tell you about my skills, projects, and experience. What interests you most?",
                f"Welcome! I'm the AI assistant for {name}'s portfolio. Feel free to ask about my technical background!",
                "Hello and welcome! I'm here to share information about my professional journey. What catches your interest?",
                "Hey! Great to meet you! I'm an AI assistant that knows all about my creator's professional background. What would you like to explore?",
                "Hi! I'm excited to chat with you about my technical skills and projects. What sounds interesting?",
                "Hello there! I'm here to showcase my portfolio and answer any questions you might have. Fire away!"
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
                "That's an interesting question! While I focus on portfolio-related topics, I'd love to share how my technical skills might relate to that. What specific aspect interests you?",
                "I appreciate your curiosity! Though I specialize in discussing my professional background, I can see how that connects to my problem-solving experience. Want to hear more?",
                "Great question! While that's outside my main expertise, it reminds me of the analytical thinking I use in my projects. Would you like to explore my technical work?",
                "Interesting topic! I may not be an expert in that area, but I apply similar logical thinking in my programming and trading. Care to learn about those experiences?"
            ],
            "compliments": [
                "Thank you so much! That's very kind of you to say. I really appreciate it! 😊 Is there anything specific about my work you'd like to know more about?",
                "Aww, that's really sweet! Thank you for the kind words. 🙏 What aspect of my portfolio caught your attention?",
                "That means a lot to me, thank you! I'm glad you think so. What would you like to explore about my background?",
                "You're too kind! I really appreciate the compliment. 😄 What interests you most about my technical journey?"
            ],
            "casual_conversation": [
                "I enjoy chatting! While I love casual conversation, I'm especially excited to talk about my passion for technology and development. What interests you?",
                "That's a fun topic! I find that my experiences in coding and trading give me interesting perspectives on many things. Want to hear about them?",
                "I appreciate the casual chat! It's always nice to connect. Speaking of connections, would you like to know about my networking projects or professional experience?",
                "Thanks for the friendly conversation! I'm always happy to chat, especially about topics related to my technical background. What would you like to explore?"
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
                "I'm not quite sure what you're asking, but I'm here to help! Could you rephrase that? I'm excited to share information about my background!",
                "I didn't quite catch that - could you clarify? I'm ready to discuss my skills, projects, or any other aspect of my portfolio!",
                "I want to give you the best answer possible! Could you help me understand what you're looking for? I'm here to help!",
                "I'm having trouble understanding that question. Could you try asking in a different way? I'm eager to assist you!"
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
        """Classify user intent based on keywords and context with fuzzy matching for spelling mistakes"""
        user_input_lower = user_input.lower()
        
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
        """Generate response based on intent and templates"""
        
        if intent == "greeting":
            return self._get_varied_response("greeting")
        
        elif intent == "goodbye":
            return self._get_varied_response("goodbye")
        
        elif intent == "name_intro":
            return self._get_varied_response("name_intro")
        
        elif intent == "skills":
            skills = self.data.get('technical_skills', ['Programming'])
            base_responses = [
                f"I have expertise in {', '.join(skills[:6])}. I'm particularly strong in AI/ML and web development.",
                f"My technical toolkit includes {', '.join(skills[:6])}. I'm particularly passionate about AI/ML and creating innovative web solutions.",
                f"I work with {', '.join(skills[:6])} and focus on building intelligent systems and robust web applications.",
                f"My skill set covers {', '.join(skills[:6])}, with special emphasis on artificial intelligence and modern web development."
            ]
            return random.choice(base_responses)
        
        elif intent == "projects":
            projects = self.data.get('projects', [])
            if projects:
                project_list = []
                for i, project in enumerate(projects[:3], 1):
                    name = project.get('name', 'Project')
                    desc = project.get('description', 'Innovative solution')
                    tech = project.get('technologies', [])
                    tech_str = f" (Technologies: {', '.join(tech[:3])})" if tech else ""
                    project_list.append(f"{i}. {name}: {desc}{tech_str}")
                
                intros = [
                    "Here are some of my key projects:",
                    "I'm proud to showcase these projects:",
                    "Let me highlight some of my favorite projects:",
                    "Here's a selection of my recent work:"
                ]
                return f"{random.choice(intros)}\n\n" + "\n".join(project_list)
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
        """Process user input and generate appropriate response"""
        try:
            user_input = user_input.strip()
            if not user_input:
                return "Please ask me something! I'm here to help."
            
            # Check for grammar corrections
            corrected_input, has_corrections = self._correct_grammar(user_input)
            
            # Add to conversation history (use original input)
            self.conversation_history.append({"user": user_input, "timestamp": datetime.now()})
            
            # Classify intent using corrected input
            intent = self._classify_intent(corrected_input)
            
            # Generate response based on intent
            response = self._get_template_response(intent, corrected_input)
            
            # Add grammar correction note if needed
            if has_corrections and intent not in ["inappropriate", "unclear"]:
                correction_note = f"\n\n💡 *I noticed some small grammar/spelling corrections in your message. I understood you meant: \"{corrected_input}\"*"
                response = response + correction_note
            
            # Add response to history
            self.conversation_history.append({"bot": response, "timestamp": datetime.now()})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return random.choice(self.response_templates["error"])

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
