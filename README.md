🌍 Multi-Agent Tourism Assistant

A smart, AI-powered Trip Planner built with Python, Streamlit, Async Agents, Wikipedia API, OpenStreetMap (Overpass) and WeatherAPI.
It understands natural language queries and gives weather, tourist attractions, Wikipedia images, and summaries for any place.

🚀 Features
🧠 1. Natural Language Query Understanding

Ask anything like:

"I'm going to Bangalore, tell me weather and places to visit."

"Weather in Delhi?"

"Suggest top tourist places in Goa."

Your text is processed through an NLP-based place detector (regex + smart cleaning) from the orchestrator module.
(See agents/orchestrator.py 

orchestrator

)

🌦️ 2. Real Weather Data (WeatherAPI)

Powered by weather_agent.py 

weather_agent

Temperature

Chance of rain

Cloud %

City-level accurate weather

Requires a free API key from:
👉 https://www.weatherapi.com/

Add it in .env:

WEATHER_API_KEY=YOUR_KEY_HERE

🧭 3. Real Tourist Places from OpenStreetMap (Overpass API)

Using OpenStreetMap →
places_agent.py 

places_agent

 fetches attractions like:

beaches

museums

forts

viewpoints

parks

monuments

The agent filters noisy data (hotels, lodges, residences).

📸 4. Wikipedia Images + Summaries

Every place is enriched with:

Thumbnail (500px)

Extract (summary)

Description

Popularity Score

Thanks to the Wikipedia API:

WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php?...”

📍 5. Geocoding (Convert City → Lat/Lon)

Using the Nominatim API (OpenStreetMap)
utils/geocode.py 

geocode

🖥️ 6. Beautiful Streamlit UI

Your UI (app.py) 

app

:

Input box

Loading spinner

Final response text

Debug info section

Easy interaction

🧩 Project Structure
📁 tourism-assistant/
│── app.py                     # Streamlit UI
│── requirements.txt           
│── .env                       # WeatherAPI key
│── README.md
│
├── agents/
│   ├── orchestrator.py        # Controls workflow (weather + places)
│   ├── places_agent.py        # OSM + Wikipedia tourist places
│   └── weather_agent.py       # WeatherAPI client
│
└── utils/
    └── geocode.py             # Nominatim geocoder

⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/yourusername/tourism-multi-agent.git
cd tourism-multi-agent

2️⃣ Create Virtual Environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add API Key

Create a .env file:

WEATHER_API_KEY=YOUR_KEY

5️⃣ Run App
streamlit run app.py

🧠 How It Works (Architecture)
1. Orchestrator Agent

Controls the full pipeline:

Detects place from text

Detects intent (weather / places / both)

Calls the appropriate agents

Combines responses into clean output

2. Weather Agent

Uses WeatherAPI →
Returns temperature, cloud %, rain chance.

3. Places Agent

Pipeline:

Find coordinates from geocoder

Query Overpass API for tourist attractions

Clean + dedupe results

Fetch Wikipedia thumbnails + summaries

Compute popularity score

Sort and return best places

4. UI Layer

Streamlit frontend for user interaction.

💡 Example Queries

Try:

"I'm going to Bangalore, what’s the weather and places to visit?"

"Weather in Jaipur"

"Suggest some tourist places in Goa"

"Plan trip to Manali"

📝 Requirements

Minimal version (auto-detectable from your project):

streamlit
httpx
python-dotenv
asyncio
pytz

🧪 Debugging

A debug section in the UI shows:

Detected place

Detected intent

Raw weather response

Raw places list

Scores

Perfect for assignment submissions.

🤝 Contributing

Pull requests welcome!
You can add:

More agents

Better NLP

Sentiment analysis

Road distances

Hotel finder agent