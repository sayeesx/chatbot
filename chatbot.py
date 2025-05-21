import json

# Load Sayees' data
with open('sayees_data.json') as f:
    data = json.load(f)


def get_response(user_input):
    user_input = user_input.lower()

    if "name" in user_input:
        return f"I'm Sayees, an aspiring AI & Data Science professional."

    elif "where are you from" in user_input or "hometown" in user_input:
        return f"I'm from {data['location']['hometown']}."

    elif "where are you now" in user_input or "current location" in user_input:
        return f"I'm currently based in {data['location']['current']}."

    elif "education" in user_input:
        edu = data["education"]["current"]
        return f"I'm pursuing {edu['degree']} with specialization in {edu['specialization']} at {edu['college']}, {edu['university']}."

    elif "interests" in user_input:
        return f"I'm interested in: {', '.join(data['interests'])}."

    elif "languages" in user_input:
        return f"I can communicate in {', '.join(data['languages'])}."

    elif "skills" in user_input or "soft skills" in user_input:
        return f"My soft skills include: {', '.join(data['soft_skills'])}."

    elif "tools" in user_input:
        return f"I work with tools like: {', '.join(data['tools'])}."

    elif "project" in user_input or "exquio" in user_input:
        proj = data["projects"][0]
        return f"I worked on a project called {proj['name']} – {proj['description']}, using {', '.join(proj['technologies'])}."

    elif "contact" in user_input or "linkedin" in user_input:
        return f"You can reach me via LinkedIn: {data['contact']['linkedin']} or GitHub: {data['contact']['github']}."

    elif "bye" in user_input:
        return "Talk to you later! 😊"

    else:
        return "I'm still learning! Try asking about my education, skills, interests, or project."
