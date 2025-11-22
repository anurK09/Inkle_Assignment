🌍 Multi-Agent Tourism Assistant

A smart, AI-powered travel assistant built using Streamlit.

This project is a real-time tourism assistant that helps users:

🔎 Detect the city/place from any natural-language question

☁️ Get live weather information for the city

📍 Discover popular tourist attractions near that city

🧠 Use separate agents (Weather Agent + Places Agent + Orchestrator)

💬 Understand complex questions, not just simple ones

The entire system works with free APIs, no API keys for tourist places, and runs smoothly on Streamlit Cloud & mobile devices.

🚀 Features
✅ 1. Smart NLP-based place detection

Understands user queries like:

"I’m planning a trip to Bangalore, what’s the weather and places I can visit?"

"Plan my trip to Goa"

"What are the attractions near Ooty?"

✅ 2. Real Weather Data

Using WeatherAPI
✔ Temperature
✔ Rain chance
✔ Cloud info

✅ 3. Tourist Places (NO API KEY NEEDED)

Uses Wikipedia GeoSearch API:
✔ Highly reliable
✔ Fast
✔ Cloud-safe
✔ Accurate tourist attractions

✅ 4. Multi-Agent Architecture

Weather Agent → Fetches live weather

Places Agent → Fetches attractions

Orchestrator → Detects intent & merges agent responses

✅ 5. Fully Deployable

Works perfectly on:

Streamlit Cloud

Desktop

Mobile

📦 Project Structure
inkel_assignment/
│
├── app.py
├── agents/
│   ├── orchestrator.py
│   ├── weather_agent.py
│   └── places_agent.py
├── utils/
│   └── geocode.py
├── .env
└── README.md

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

2️⃣ Create Virtual Environment
python -m venv .venv


Activate:

Windows
.venv\Scripts\activate

Mac/Linux
source .venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Weather API Key

Create a .env file:

WEATHER_API_KEY=your_api_key_here


For Streamlit Cloud → Add inside Secrets:

WEATHER_API_KEY = "your_api_key_here"

5️⃣ Run the App
streamlit run app.py

🌐 APIs Used
1. WeatherAPI

Free

Accurate

Requires API key

2. Wikipedia GeoSearch (NO API KEY NEEDED)

Used for tourist attractions:

https://en.wikipedia.org/w/api.php

Extremely fast

Cloud-safe

🔧 Core Logic Summary
1. Orchestrator Agent

Detects place

Detects intent (weather, places, both)

Calls respective agents

Merges output

2. Weather Agent

Fetches real-time weather using WeatherAPI.

3. Places Agent

Uses Wikipedia’s GeoSearch:

Gets coordinates

Finds nearby attractions

Filters out non-tourist spots

📱 Fully Mobile Friendly

App works perfectly on:

Android

iPhone

Tablets

Desktop

🌟 Example Query

User:

I’m going to go to Manali next week, what’s the temperature and places I can visit?

Response:
✔ Weather in Manali
✔ Popular places like Hidimba Devi Temple, Solang Valley, Jogini Waterfall, Museum of Himachal Culture, etc.

📤 Deployment (Streamlit Cloud)

Upload project to GitHub

Go to https://streamlit.io/cloud

Create new app

Select repo + branch

Add API key in Secrets

Deploy 🎉