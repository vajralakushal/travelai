# WanderAI ✈️

An AI travel planner built with Streamlit and a LangGraph multi-agent backend
(destination, activity, budget, and itinerary agents) powered by Anthropic Claude.

## Running with Docker

### 1. Add your API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Then edit `.env` and set all three values (the app validates them on startup):

| Variable             | Used for           | Get one at                       |
| -------------------- | ------------------ | -------------------------------- |
| `ANTHROPIC_API_KEY`  | LLM agents         | https://console.anthropic.com/   |
| `UNSPLASH_ACCESS_KEY`| Destination images | https://unsplash.com/developers  |
| `TAVILY_API_KEY`     | Web search         | https://app.tavily.com/          |

### 2. Build and start

```bash
docker compose up --build
```

Then open http://localhost:8501.

To stop: `Ctrl+C`, or `docker compose down`.

The SQLite database persists on the host as `travelai.db` (bind-mounted into the
container), so your saved trips survive restarts.

## Running locally (without Docker)

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/ui/streamlit_app.py
```

## Tests

```bash
pytest
```
