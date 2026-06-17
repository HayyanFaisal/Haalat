# Haalat

Pakistan-focused emergency intelligence command center with multilingual triage, nearby resource routing, volunteer matching, live first-aid guidance, city-memory logging, mass-event detection, animated instruction visuals, and a live multi-agent telemetry matrix.

## Features

- FastAPI web app with custom HTML/CSS/JS command-center UI
- Gemini-powered emergency classification when `GEMINI_API_KEY` is available
- Offline keyword fallback when no Gemini key is configured
- Local RAG-style retrieval over emergency categories and first-aid protocols
- Folium map with OpenStreetMap/CartoDB tile layers
- Volunteer and emergency service matching from local JSON datasets
- Audio upload and Gemini transcription support
- Mass-event detection from `incident_log.json`
- Admin dashboard for incidents and volunteer status

## Requirements

- Python 3.10+
- Internet access for map tiles and Gemini API calls
- A Gemini API key for full AI classification/transcription behavior

## Installation

1. Clone the repository:

```bash
git clone https://github.com/HayyanFaisal/Haalat.git
cd Haalat
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
```

`GEMINI_API_KEY` is recommended. `GOOGLE_MAPS_API_KEY` is optional; the app uses Folium map tiles and opens Google Street View links without requiring it.

## Run

Start the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8000/
```

Admin dashboard:

```text
http://127.0.0.1:8000/admin
```

## Demo Prompts

Cardiac emergency:

```text
mere baap ko dil ka dorah para hai, woh gir gaye hain - main Garden mein hoon
```

Gas leak / mass-event trigger:

```text
gas ki smell aa rahi hai yahan pe
```

Severe bleeding:

```text
mere dost ka khoon bohat zyada beh raha hai
```

## Project Structure

```text
app.py                         FastAPI app, APIs, streaming telemetry, emergency pipeline
tools.py                       Location, volunteer, service, and map helpers
agents.py                      CrewAI agent definitions
tasks.py                       CrewAI task definitions
templates/index.html           Main dispatch command-center UI
templates/admin.html           Admin dashboard
rag/                           Local retrieval/index helpers
data/                          Emergency protocols, categories, services, volunteers
incident_log.json              Local anonymized incident memory
```

## Notes

- `.env`, audio uploads, Python caches, and generated local RAG indexes are ignored by git.
- `incident_log.json` is local demo/runtime state and may change when testing reports.
- This is a hackathon prototype and decision-support demo, not a replacement for official emergency services.
