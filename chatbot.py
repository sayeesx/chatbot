import json
import os
import re
import random
from datetime import datetime
from typing import Dict, List, Optional
from difflib import get_close_matches  # For fuzzy matching to handle spelling mistakes

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers library not found. Using fallback responses.")

class PortfolioBot:
    def __init__(self, data_file: str = "sayees_data.json"):
        """Initialize the chatbot with personal data and AI model"""
        
        # Load personal portfolio data
        self.data = self._load_portfolio_data(data_file)
        
        # Initialize conversation history
        self.conversation_history = []
        self.context_memory = []
        
        # Setup AI model if available
        self.model = None
        self.tokenizer = None
        if TRANSFORMERS_AVAILABLE:
            self._initialize_model()
        
        # Generate context summary
        self.context = self._generate_context_summary()
        
        # Predefined responses for common queries
        self.response_templates = self._setup_response_templates()
        
        # Define intent keywords for fuzzy matching
        self._setup_intent_keywords()
        
        # Setup response tracking to avoid repetition
        self._setup_response_tracking()
        
        print("✅ PortfolioBot initialized successfully!")

    def _load_portfolio_data(self, data_file: str) -> Dict:
        """Load portfolio data with error handling"""
        try:
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Fallback data if file doesn't exist
                return self._get_fallback_data()
        except Exception as e:
            print(f"Warning: Could not load {data_file}. Using fallback data. Error: {e}")
            return self._get_fallback_data()

    def _get_fallback_data(self) -> Dict:
        """Provide fallback data structure"""
        return {
            "name": "Muhammed Sayees",
            "role": "Software Developer & AI/ML Engineer",
            "education": {
                "current": {
                    "degree": "Bachelor's",
                    "specialization": "Computer Science",
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
                    "duration": "6 months"
                }
            ],
            "projects": [
                {
                    "name": "AI Portfolio Bot",
                    "description": "Intelligent chatbot for portfolio website"
                }
            ],
            "technical_skills": ["Python", "Machine Learning", "Web Development"],
            "languages": ["English", "Malayalam", "Hindi"],
            "trading_experience": {
                "years": "2+"
            }
        }

    def _initialize_model(self):
        """Initialize the AI model with proper error handling"""
        try:
            model_name = "microsoft/DialoGPT-small"  # Using small model for better performance
            
            print("🤖 Loading AI model... This may take a moment.")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                padding_side="left",
                use_fast=True
            )
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,
                torch_dtype="auto"
            )
            
            # Create pipeline
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
            
            print("✅ AI model loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Could not load AI model: {e}")
            print("🔄 Falling back to template-based responses.")
            self.model = None

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
            print(f"Error generating context: {e}")
            return f"I am {self.data.get('name', 'Sayees')}, a software developer and AI enthusiast."

    def _setup_response_templates(self) -> Dict[str, List[str]]:
        """Setup template responses for common queries"""
        return {
            "greeting": [
                f"Hello! I'm {self.data.get('name', 'Sayees')}'s AI assistant. How can I help you learn more about my background and projects?",
                f"Hi there! Welcome to {self.data.get('name', 'Sayees')}'s portfolio. What would you like to know?",
                "Greetings! I'm here to tell you about my skills, projects, and experience. What interests you most?",
                f"Welcome! I'm the AI assistant for {self.data.get('name', 'Sayees')}'s portfolio. Feel free to ask about my technical background!",
                "Hello and welcome! I'm here to share information about my professional journey. What catches your interest?"
            ],
            "name_intro": [
                f"I'm {self.data.get('name', 'Sayees')}, a {self.data.get('role', 'Software Developer')} passionate about AI and technology.",
                f"My name is {self.data.get('name', 'Sayees')}, and I specialize in software development and machine learning.",
                f"I'm {self.data.get('name', 'Sayees')} - a tech enthusiast working in software development and AI/ML engineering.",
                f"You can call me {self.data.get('name', 'Sayees')}! I'm a developer focused on creating innovative AI and web solutions.",
                f"I'm {self.data.get('name', 'Sayees')}, currently pursuing my passion in software development while building expertise in AI and machine learning.",
                f"Nice to meet you! I'm {self.data.get('name', 'Sayees')}, a software developer who loves working with cutting-edge technologies like AI and machine learning."
            ],
            "skills": [
                f"My technical skills include {', '.join(self.data.get('technical_skills', ['Programming']))}. I'm particularly strong in AI/ML and web development.",
                "I work with modern technologies focusing on AI, machine learning, and full-stack development.",
                f"I'm proficient in {', '.join(self.data.get('technical_skills', ['Programming']))} and have hands-on experience with various frameworks and tools.",
                "My expertise spans across multiple domains including artificial intelligence, web development, and system design."
            ],
            "projects": [
                "I've worked on several interesting projects including AI applications, web development, and trading systems.",
                "My projects range from machine learning models to web applications and financial trading tools.",
                "I love building innovative solutions! My portfolio includes AI-powered applications, web platforms, and automated trading systems.",
                "I've developed various projects that showcase my skills in AI, web development, and financial technology."
            ],
            "general_redirect": [
                "I'm here to showcase my professional background and technical expertise. What aspect of my portfolio interests you most?",
                "I specialize in discussing my skills, projects, and professional journey. What would you like to explore?",
                "My focus is on sharing insights about my technical background and career. What specific area catches your attention?",
                "I'm designed to highlight my professional capabilities and experience. Which topic would you like to dive into?",
                "Let me tell you about my technical journey! What aspect of my background would you like to know more about?",
                "I'm passionate about discussing my work in technology and development. What interests you most?",
                "I'd love to share my professional story with you! Are you curious about my skills, projects, or experience?",
                "My expertise lies in software development and AI. What particular area would you like to explore?",
                "I'm here to discuss my technical background and achievements. What would you like to learn about?",
                "Feel free to ask about my programming skills, projects, or professional experience. What sounds interesting to you?"
            ],
            "irrelevant_polite": [
                "That's an interesting question, but I'm here specifically to help you learn about my professional background and projects. What would you like to know about my skills or experience?",
                "I appreciate your curiosity, but I'm designed to discuss my portfolio and professional experience. Would you like to hear about my technical projects or career journey?",
                "While that's a fascinating topic, I'm focused on helping visitors understand my professional background. Can I tell you about my latest projects or technical skills instead?",
                "I'd love to help, but I specialize in discussing my portfolio, skills, and professional experience. What aspect of my background interests you most?",
                "That's outside my expertise, but I'm great at talking about my technical skills and projects! What would you like to explore?",
                "I'm not equipped for that topic, but I can share exciting details about my development work and AI projects. Interested?"
            ],
            "irrelevant_redirect": [
                "I'm not equipped to help with that particular topic, but I'd be happy to discuss my software development projects, AI/ML experience, or trading background. What would you like to explore?",
                "That's outside my area of expertise. However, I can share insights about my technical skills, project experience, or professional journey. What interests you?",
                "I'm specifically designed to showcase my portfolio and professional capabilities. Would you like to learn about my programming skills, recent projects, or educational background?",
                "I focus on discussing my professional experience and technical expertise. Can I interest you in learning about my AI projects, development skills, or trading experience instead?",
                "That's not my specialty, but I excel at discussing my technical background! Want to hear about my latest projects or skills?",
                "I'm better suited to talk about my professional journey and technical achievements. What aspect would you like to explore?"
            ],
            "inappropriate": [
                "I'm here to maintain a professional conversation about my portfolio and career. Let's focus on my technical skills, projects, or professional experience instead.",
                "I prefer to keep our conversation professional and portfolio-focused. What would you like to know about my technical background or projects?",
                "I'm designed to discuss my professional qualifications and experience. Would you like to hear about my development projects or technical skills?",
                "Let's keep things professional! I'd be happy to discuss my technical expertise, projects, or career journey instead."
            ],
            "error": [
                "I apologize, but I'm having trouble processing that right now. Could you rephrase your question?",
                "Something went wrong on my end. Please try asking again, and I'll do my best to help!",
                "I'm experiencing a technical hiccup. Could you try rephrasing your question?",
                "Oops! I encountered an issue. Mind trying that again in a different way?"
            ],
            "unclear": [
                "I'm not quite sure what you're asking. Could you rephrase your question about my portfolio, skills, or experience?",
                "I didn't quite catch that. Would you mind clarifying what aspect of my background you'd like to know about?",
                "I'm having trouble understanding your question. Could you try asking in a different way about my professional experience or projects?",
                "Could you help me understand what you're looking for? I'm here to discuss my technical background and projects.",
                "I'm not sure I follow. Could you rephrase your question about my skills, experience, or projects?"
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
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "hola"],
            "name_intro": ["name", "who are you", "introduce", "about you", "sayees", "who is", "tell me about yourself", "your name"],
            "skills": ["skills", "technical", "programming", "languages", "technologies", "expertise", "stack", "tech stack", "coding", "develop", "software", "framework", "library", "tool"],
            "projects": ["projects", "work", "portfolio", "built", "created", "developed", "github", "showcase", "demo", "application", "app", "website", "system", "platform"],
            "experience": ["experience", "internship", "job", "work history", "career", "professional", "industry", "company", "employment", "worked", "role", "position"],
            "education": ["education", "study", "college", "university", "degree", "qualification", "academic", "school", "course", "major", "graduate", "student"],
            "contact": ["contact", "reach", "email", "phone", "connect", "hire", "recruiting", "message", "get in touch", "social media", "linkedin"],
            "trading": ["trading", "crypto", "cryptocurrency", "forex", "stocks", "investment", "market", "finance", "financial", "trade", "investor", "portfolio", "asset"]
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
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation except apostrophes
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract words from text for fuzzy matching"""
        normalized = self._normalize_text(text)
        words = normalized.split()
        # Filter out very short words and common stop words
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
        
        # Check for inappropriate content first (exact match for sensitive words)
        inappropriate_words = [
            "sex", "dating", "relationship", "personal life", "family", "girlfriend", "boyfriend",
            "politics", "religion", "controversial", "offensive", "illegal", "drugs", "violence"
        ]
        
        if any(word in user_input_lower for word in inappropriate_words):
            return "inappropriate"
        
        # Extract keywords from user input
        input_keywords = self._extract_keywords(user_input)
        
        if not input_keywords:
            return "unclear"  # No meaningful keywords found
        
        # Try fuzzy matching for each keyword in user input
        matched_intents = {}
        
        for user_word in input_keywords:
            # Find close matches in our keyword dictionary
            matches = get_close_matches(user_word, self.all_keywords, n=3, cutoff=0.75)
            
            if matches:
                # Find which intent category these matches belong to
                for match in matches:
                    for intent, keywords in self.intent_keywords.items():
                        if match in keywords:
                            matched_intents[intent] = matched_intents.get(intent, 0) + 1
        
        # If we found matches, return the intent with the most matches
        if matched_intents:
            return max(matched_intents.items(), key=lambda x: x[1])[0]
        
        # Check for common irrelevant topics
        irrelevant_topics = [
            "weather", "food", "movies", "music", "sports", "games", "celebrities", "news",
            "cooking", "travel", "fashion", "animals", "pets", "hobbies", "entertainment",
            "jokes", "funny", "memes", "random", "philosophy", "literature", "history",
            "geography", "science facts", "trivia", "gossip", "shopping", "health advice",
            "medical advice", "legal advice", "financial advice", "investment advice"
        ]
        
        if any(topic in user_input_lower for topic in irrelevant_topics):
            return "irrelevant"
        
        # Check for questions that are clearly not portfolio-related
        question_starters = [
            "what is", "how to", "why does", "when did", "where is", "can you help me with",
            "tell me about the", "explain", "what do you think about", "do you know about",
            "have you heard", "what's your opinion"
        ]
        
        if any(phrase in user_input_lower for phrase in question_starters) and not self._is_portfolio_related(user_input):
            return "irrelevant"
        
        # Default to general if we can't determine a specific intent
        return "general"

    def _get_template_response(self, intent: str, user_input: str) -> str:
        """Generate response based on intent and templates"""
    
        if intent == "greeting":
            return self._get_varied_response("greeting")
    
        elif intent == "name_intro":
            return self._get_varied_response("name_intro")
    
        elif intent == "skills":
            skills = self.data.get('technical_skills', ['Programming'])
            base_responses = [
                f"I have expertise in {', '.join(skills)}. I specialize in AI/ML, web development, and have experience with trading systems.",
                f"My technical toolkit includes {', '.join(skills)}. I'm particularly passionate about AI/ML and creating innovative web solutions.",
                f"I work with {', '.join(skills)} and focus on building intelligent systems and robust web applications.",
                f"My skill set covers {', '.join(skills)}, with special emphasis on artificial intelligence and modern web development."
            ]
            return random.choice(base_responses)
    
        elif intent == "projects":
            projects = self.data.get('projects', [])
            if projects:
                project_list = []
                for i, project in enumerate(projects[:3], 1):
                    project_list.append(f"{i}. {project.get('name', 'Project')}: {project.get('description', 'Innovative solution')}")
            
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
                    f"I have internship experience at {exp.get('company', 'a tech company')} for {exp.get('duration', 'several months')}, where I gained valuable industry experience.",
                    f"I've worked as an intern at {exp.get('company', 'a tech company')} for {exp.get('duration', 'several months')}, which gave me great hands-on experience.",
                    f"My professional journey includes a {exp.get('duration', 'several months')} internship at {exp.get('company', 'a tech company')}, where I developed practical skills.",
                    f"I gained valuable industry exposure through my {exp.get('duration', 'several months')} internship at {exp.get('company', 'a tech company')}."
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
            years = self.data.get('trading_experience', {}).get('years', '2+')
            base_responses = [
                f"Yes, I have {years} years of experience trading in stocks, cryptocurrency, and forex markets. It's taught me a lot about market analysis and risk management.",
                f"I've been actively trading for {years} years across stocks, crypto, and forex markets. It's given me valuable insights into financial markets and analytical thinking.",
                f"Trading has been a passion of mine for {years} years! I work with stocks, cryptocurrency, and forex, which has sharpened my analytical and decision-making skills.",
                f"I have {years} years of hands-on trading experience in various markets including stocks, crypto, and forex. It's been an excellent complement to my technical skills."
            ]
            return random.choice(base_responses)
    
        elif intent == "inappropriate":
            return self._get_varied_response("inappropriate")
    
        elif intent == "unclear":
            return self._get_varied_response("unclear")
    
        elif intent == "irrelevant":
            # Determine if it's a polite redirect or more direct redirect
            polite_indicators = ["please", "could you", "would you", "can you", "help me"]
            if any(indicator in user_input.lower() for indicator in polite_indicators):
                response = self._get_varied_response("irrelevant_polite")
            else:
                response = self._get_varied_response("irrelevant_redirect")
        
            # Add a helpful suggestion
            suggestions = [
                "\n\nFor example, you could ask about:\n• My programming skills and technologies\n• Recent projects I've worked on\n• My educational background\n• My trading and market analysis experience",
                "\n\nI'd be happy to discuss:\n• Technical expertise and tech stack\n• Portfolio projects and achievements\n• Professional experience and internships\n• AI/ML and development work",
                "\n\nSome topics I can help with:\n• Software development experience\n• AI and machine learning projects\n• Trading and financial market insights\n• Educational background and qualifications",
                "\n\nFeel free to ask about:\n• My coding skills and favorite technologies\n• Exciting projects I've built\n• My academic and professional journey\n• My experience in financial markets"
            ]
            return response + random.choice(suggestions)
    
        else:
            # For general queries, check if it's somewhat related to portfolio
            portfolio_keywords = ["career", "developer", "programming", "technology", "computer", "software", "coding", "tech"]
            if any(keyword in user_input.lower() for keyword in portfolio_keywords):
                return "I'd be happy to discuss my career in technology and software development! What specific aspect would you like to know about - my technical skills, projects, or professional experience?"
            else:
                # Use varied general redirect responses
                return self._get_varied_response("general_redirect")

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
        
        # Extract keywords from user input
        input_keywords = self._extract_keywords(user_input)
        
        # Try fuzzy matching
        for word in input_keywords:
            matches = get_close_matches(word, portfolio_keywords, n=1, cutoff=0.8)
            if matches:
                return True
                
        return False

    async def process_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response"""
        try:
            # Clean and validate input
            user_input = user_input.strip()
            if not user_input:
                return "Please ask me something! I'm here to help."
            
            # Add to conversation history
            self.conversation_history.append({"user": user_input, "timestamp": datetime.now()})
            
            # Classify intent first
            intent = self._classify_intent(user_input)
            
            # Handle inappropriate or irrelevant queries immediately
            if intent in ["inappropriate", "irrelevant", "unclear"]:
                response = self._get_template_response(intent, user_input)
            
            # Check if this is portfolio-related
            elif self._is_portfolio_related(user_input) or intent in [
                "greeting", "name_intro", "skills", "projects", "experience", 
                "education", "contact", "trading"
            ]:
                # Use template-based response for portfolio queries
                response = self._get_template_response(intent, user_input)
            
            elif not self.model:
                # No AI model available - redirect to portfolio topics
                response = self._get_varied_response("general_redirect")
            
            else:
                # Use AI model for general conversation with constraints
                response = await self._generate_ai_response(user_input)
            
            # Add response to history
            self.conversation_history.append({"bot": response, "timestamp": datetime.now()})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            print(f"Error processing input: {e}")
            return random.choice(self.response_templates["error"])

    async def _generate_ai_response(self, user_input: str) -> str:
        """Generate response using AI model with portfolio focus"""
        try:
            if not self.model:
                return "I'm here to discuss my portfolio and professional background. What would you like to know about my skills or experience?"
            
            # Create a portfolio-focused prompt that constrains the AI
            # Include recent conversation history for context
            recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 0 else []
            history_text = ""
            
            for item in recent_history:
                if "user" in item:
                    history_text += f"User: {item['user']}\n"
                elif "bot" in item:
                    history_text += f"Assistant: {item['bot']}\n"
            
            # Create a more detailed system prompt to handle irrelevant queries better
            prompt = f"""You are an AI assistant for a software developer's portfolio website named Muhammed Sayees.
Your primary purpose is to provide information about Sayees's skills, projects, education, and professional experience.

IMPORTANT INSTRUCTIONS:
1. Always maintain a professional tone.
2. For questions about Sayees's background, provide detailed information from your knowledge base.
3. For irrelevant or off-topic questions, politely redirect the conversation back to Sayees's portfolio.
4. Never provide information on controversial, political, or inappropriate topics.
5. If you're unsure about specific details, focus on general information about Sayees's skills and experience.

Recent conversation:
{history_text}

User: {user_input}
Assistant:"""
            
            # Generate response
            result = self.model(prompt, max_length=len(prompt) + 80, num_return_sequences=1)
            
            # Extract and clean response
            response = result[0]['generated_text']
            response = response[len(prompt):].strip()
            
            # Clean up response
            response = re.sub(r'\s+', ' ', response)
            
            # If response is empty or too short, provide fallback
            if not response or len(response) < 10:
                return "I'm here to help you learn about my professional background. What would you like to know about my skills, projects, or experience?"
            
            # Ensure response doesn't exceed reasonable length
            if len(response) > 250:
                response = response[:250] + "..."
            
            # Check if the AI response is still off-topic and redirect if needed
            if self._is_response_off_topic(response):
                return random.choice(self.response_templates["irrelevant_polite"])
            
            return response
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return "I'm designed to discuss my portfolio and professional experience. What aspect of my background interests you most?"

    def _is_response_off_topic(self, response: str) -> bool:
        """Check if the AI-generated response is off-topic"""
        off_topic_indicators = [
            "i don't know", "i'm not sure", "i can't help", "that's not something",
            "i'm not able to", "i don't have information", "i'm not programmed",
            "weather", "cooking", "movies", "sports", "politics", "religion"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in off_topic_indicators)

    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("✅ Conversation history cleared!")

    def get_portfolio_summary(self) -> str:
        """Get a comprehensive portfolio summary"""
        return self.context

    def test_spelling_correction(self):
        """Test the spelling correction functionality"""
        test_cases = [
            "wat are your skils?",  # what are your skills?
            "tel me abut your projcts",  # tell me about your projects
            "wher did you studie?",  # where did you study?
            "wat is your experiance?",  # what is your experience?
            "can you tel me abut tradng?",  # can you tell me about trading?
        ]
        
        print("\n🧪 Testing Spelling Correction:")
        print("=" * 40)
        
        for test_input in test_cases:
            intent = self._classify_intent(test_input)
            print(f"Input: '{test_input}' -> Intent: {intent}")
        
        print("=" * 40)


# Enhanced main function for testing
async def main():
    """Main function for testing the chatbot"""
    try:
        bot = PortfolioBot()
        
        # Test spelling correction
        bot.test_spelling_correction()
        
        print("\n" + "="*50)
        print("🤖 SAYEES PORTFOLIO BOT ACTIVATED!")
        print("="*50)
        print("✨ NEW FEATURES:")
        print("• Improved spelling mistake handling")
        print("• Better irrelevant query detection")
        print("• Enhanced AI model integration")
        print("• Fuzzy matching for typos")
        print("\nAsk me about:")
        print("• Skills and technical expertise")
        print("• Projects and portfolio")
        print("• Education and experience")
        print("• Trading experience")
        print("• Or just chat with me!")
        print("\n⚠️  Note: I'm designed to focus on portfolio-related topics")
        print("and will politely redirect other questions back to professional discussion.")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'summary' to get a full portfolio summary")
        print("Type 'test' to run spelling correction tests")
        print("-"*50 + "\n")
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("🤖 Bot: Thank you for your interest in my portfolio! Have a great day! 👋")
                    break
                    
                elif user_input.lower() == 'clear':
                    bot.clear_history()
                    continue
                    
                elif user_input.lower() in ['summary', 'portfolio summary']:
                    print(f"🤖 Bot: {bot.get_portfolio_summary()}\n")
                    continue
                
                elif user_input.lower() == 'test':
                    bot.test_spelling_correction()
                    continue
                
                # Get bot response
                response = await bot.process_input(user_input)
                print(f"🤖 Bot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Goodbye! Thanks for chatting! 👋")
                break
            except Exception as e:
                print(f"⚠️  Error: {e}")
                print("🤖 Bot: Sorry, I encountered an issue. Please try again.\n")
                
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        print("Please check your setup and try again.")


# Run the chatbot if executed directly
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
