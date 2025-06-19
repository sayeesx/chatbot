# 🤖 Chatbot API – sayeesx/chatbot

This repository contains the backend code for my personal chatbot, integrated into my portfolio website:  
🔗 [sayees.vercel.app](https://www.sayees.vercel.app)

The chatbot is built using **Flask** and **Gunicorn**, designed to handle chat interactions and API requests from the front-end (Next.js). It is hosted on **Render** for fast, always-on access and is connected to the portfolio as an embedded chat widget.

---

## 🚀 Live Demo

> 🟢 API hosted at: `https://chatbot*****render.com`  
> Used in production on my portfolio site: [sayees.vercel.app](https://www.sayees.vercel.app)

---

## ⚙️ Tech Stack

| Layer      | Tools & Technologies                |
|------------|-------------------------------------|
| Server     | [Flask Cors](https://pypi.org/project/flask-cors/)      |
| Framework  | [Gunicorn](https://gunicorn.org/)|
| Deployment | [Render](https://render.com/)       |
| API Format | JSON over HTTP                      |
| Integration| Next.js Frontend (via Fetch API)    |

---

## 💬 Features

- Lightweight, Express-based server
- Handles POST requests from frontend
- Configured with timeout handling for long responses
- Sends back chatbot replies in real-time
- Secure CORS-enabled for cross-origin access
- Optimized for deployment on Render

---

## 🧩 How It Works

1. Frontend chat widget (in `sayees.vercel.app`) sends a message to this API.
2. Backend processes the message and generates a response.
3. Response is sent back to the client and shown in the UI.
4. Optional: Add AI logic or database support to make it smarter.

---

## 🛠 Running Locally
git clone https://github.com/sayeesx/chatbot.git
cd chatbot
npm install
node index.js


Then visit:
http://localhost:5000


📬 Integration Example (Frontend)
const response = await fetch("https://chatbot-...(your render link)", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "Hello!" }),
});
const data = await response.json();
console.log(data.reply);



🚧 To-Do / Improvements
 Add NLP or AI logic for smarter replies

 Implement a rate limiter to protect the endpoint

 Support message history and context

 Deploy backup server for redundancy

🤝 Contributing
Feel free to fork the repo, explore it, or improve on it. PRs are welcome if you’d like to collaborate.

📄 License
MIT License. Free to use and modify.

Made with Node.js and purpose ✨
© 2025 Sayees. All rights reserved.
