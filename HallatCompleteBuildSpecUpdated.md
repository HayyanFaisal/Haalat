# Haalat (حالت) — Pakistan's Emergency Intelligence System
## Complete Blueprint for From-Scratch System Creation

This blueprint outlines the complete system design, folder structure, dataset seeds, local TF-IDF RAG retriever setup, multi-agent CrewAI definitions, FastAPI server backend, and the interactive HTML/CSS/JS frontend dashboards (both the Dispatch Console and Admin Control Panel).

---

## 1. Project Folder Structure

To set up this project from scratch, construct the following directory structure:

```text
haalat/
├── .env
├── requirements.txt
├── app.py
├── agents.py
├── tasks.py
├── tools.py
├── incident_log.json
├── data/
│   ├── emergency_categories.txt
│   ├── emergency_protocols.txt
│   ├── volunteers.json
│   ├── services.json
│   └── civil_defense_template.txt
├── rag/
│   ├── __init__.py
│   ├── knowledge_base.py
│   ├── retriever.py
│   └── prompt_builder.py
└── templates/
    ├── index.html
    └── admin.html
```

---

## 2. Environment Setup

### `requirements.txt`
```text
crewai
langchain
langchain-google-genai
langchain-text-splitters
google-genai
gradio
python-dotenv
folium
fastapi
uvicorn
python-multipart
```

### `.env`
```ini
# Haalat Environment Variables
# Copy this file, add your real API key, and save as .env

# Required: Gemini API key for agent reasoning and classification
# Get one at: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Google Maps API key for embedded Folium tiles and Street View panels
# Demo key is provided
GOOGLE_MAPS_API_KEY=AIzaSyCgsTMQhSsnQAxlmDPVN8LbfUAXql6bVik
```

---

## 3. Data Seed Files (`data/`)

### `data/emergency_categories.txt`
```text
CATEGORY: Cardiac Event
SEVERITY: 5
KEYWORDS: [dil, heart, cardiac, chest, behosh, unconscious, cpr, pulse, saans nahi, dil ka dorah, seene mein dard, dharkan, heart attack]
DESCRIPTION: Patient has sudden chest pain, is gasping for breath, or has collapsed and is unresponsive.
FIRST_RESPONSE: Perform CPR immediately. Compress the chest at 100-120 bpm, 2 inches deep. Get an AED.

CATEGORY: Severe Bleeding
SEVERITY: 4
KEYWORDS: [bleed, blood, khoon, zakhm, cut, wound, gehra, chot, bleeding, hemorrhage]
DESCRIPTION: Deep arterial or venous laceration with steady or spurting blood loss that does not stop with light pressure.
FIRST_RESPONSE: Apply direct pressure using a clean cloth. Elevate the limb. Prepare a tourniquet if bleeding is arterial and uncontrollable.

CATEGORY: Gas Leak
SEVERITY: 4
KEYWORDS: [gas, smell, boo, cylinder, sui gas, dhuaan, saans mein jalan, leak, explosion, gas leak, gas cylinder]
DESCRIPTION: Odor of natural gas or LPG present in an enclosed space, causing coughing, eye irritation, or risk of combustion.
FIRST_RESPONSE: Do not turn on lights or appliances. Evacuate the area, open windows, and isolate the gas supply valve.

CATEGORY: Burn Injury
SEVERITY: 3
KEYWORDS: [burn, jal, aag, fire, hot water, steam, oil, chemical, tezaab, scald]
DESCRIPTION: Thermal or chemical burns covering skin layers, causing redness, blisters, or charring.
FIRST_RESPONSE: Run cool water over the burn for 10-15 minutes. Do not apply ice, butter, or paste. Cover with a clean damp cloth.

CATEGORY: Drowning
SEVERITY: 5
KEYWORDS: [drown, pani, water, doob, river, sea, swimming, drowning, submersion]
DESCRIPTION: Victim submerged in water, unresponsive or struggling to breathe.
FIRST_RESPONSE: Pull the victim out of the water safely. Clear the airway and immediately begin rescue breaths followed by chest compressions.
```

### `data/emergency_protocols.txt`
```text
Protocol: Cardiac Event / Heart Attack
1. Assess responsiveness: Shake shoulders and shout "Are you okay?".
2. Check breathing: Look for chest rising for no more than 10 seconds.
3. Call for help: Direct someone to call 1122 / 115 and retrieve an AED.
4. CPR Compressions: Place hands on center of chest. Push hard and fast (100-120 bpm, 2 inches depth).
5. Rescue Breaths: If trained, give 2 breaths after every 30 compressions. Keep chest compressing continuously.
6. AED Usage: Turn on AED and follow voice prompts. Do not touch patient during shock delivery.

Protocol: Severe Bleeding
1. Safety First: Wear protective gloves if available to avoid contact with blood.
2. Direct Pressure: Place sterile dressing or clean cloth over wound and push firmly with both hands.
3. Elevation: Elevate the injured area above the level of the heart if possible.
4. Tourniquet: For limbs, if direct pressure fails, apply tourniquet 2-3 inches above the wound. Tighten until bleeding stops. Note the time.
5. Prevent Shock: Keep the patient warm and lying flat with legs raised slightly.
6. Monitor: Ensure dressing is not completely soaked. Do not remove original cloth; add more layers on top.

Protocol: Gas Leak
1. Evacuate Immediately: Order all occupants to exit the building to fresh air.
2. No Sparks: Do not use switches, matches, or cell phones inside the leak area.
3. Open Openings: If safe, open doors and windows to ventilate the area.
4. Shut Valves: Close the main gas regulator valve outside the building.
5. Alert: Call the gas company hotline and fire services from a safe distance.
6. Await Clearance: Do not re-enter the building until emergency responders declare it safe.
```

### `data/volunteers.json`
```json
[
  {
    "id": "V001",
    "name": "Dr. Ayesha Siddiqui",
    "skills": ["CPR", "trauma", "pediatrics"],
    "lat": 24.8607,
    "lng": 67.0011,
    "area": "Garden",
    "phone": "0300-0000001",
    "availability": "available",
    "response_time_minutes": 3,
    "region": "karachi"
  },
  {
    "id": "V002",
    "name": "Muhammad Bilal",
    "skills": ["First Aid", "CPR", "firefighting"],
    "lat": 24.8681,
    "lng": 67.0261,
    "area": "Soldier Bazaar",
    "phone": "0333-1112223",
    "availability": "available",
    "response_time_minutes": 5,
    "region": "karachi"
  },
  {
    "id": "V003",
    "name": "Zainab Khan",
    "skills": ["trauma", "nursing", "triage"],
    "lat": 24.8325,
    "lng": 67.0430,
    "area": "Clifton",
    "phone": "0312-3334445",
    "availability": "on call",
    "response_time_minutes": 4,
    "region": "karachi"
  },
  {
    "id": "V004",
    "name": "Hamza Ali",
    "skills": ["CPR", "first_aid", "basic_life_support"],
    "lat": 33.7167,
    "lng": 73.0587,
    "area": "Blue Area",
    "phone": "0321-5556667",
    "availability": "available",
    "response_time_minutes": 2,
    "region": "islamabad"
  }
]
```

### `data/services.json`
```json
[
  {
    "id": "S001",
    "name": "Civil Hospital Emergency",
    "type": "hospital",
    "lat": 24.8617,
    "lng": 67.0129,
    "phone": "021-99215740",
    "services": ["trauma", "cardiac", "burns", "surgery"],
    "24hr": true,
    "region": "karachi"
  },
  {
    "id": "S002",
    "name": "Edhi Ambulance Station - Saddar",
    "type": "ambulance",
    "lat": 24.8550,
    "lng": 67.0050,
    "phone": "115",
    "services": ["ambulance", "rescue", "patient transport"],
    "24hr": true,
    "region": "karachi"
  },
  {
    "id": "S003",
    "name": "Pakistan Institute of Medical Sciences (PIMS)",
    "type": "hospital",
    "lat": 33.6933,
    "lng": 73.0586,
    "phone": "051-9261170",
    "services": ["trauma", "cardiac", "burns", "pediatric ER"],
    "24hr": true,
    "region": "islamabad"
  }
]
```

### `data/civil_defense_template.txt`
```text
CIVIL DEFENSE SITUATION REPORT (SITREP)
=======================================
Incident Type: {incident_type}
Cluster Size: {cluster_size} incidents reported
Target Area: {area_name}
Threat Level: High
Recommended Actions:
- Mobilize ambulance staging units.
- Put neighborhood hospitals on pre-alert status.
- Alert local civil defense volunteers to control pedestrian traffic.

شہری دفاعی صورتحال رپورٹ
===================
واقعہ کی قسم: {incident_type}
منسلک واقعات: {cluster_size}
متاثرہ علاقہ: {area_name}
خطرہ کی سطح: شدید
اہم ہدایات:
- متاثرہ علاقہ میں ایمبولینس روانہ کریں۔
- قریبی اسپتالوں کو الرٹ کریں۔
- مقامی رضاکاروں کو ٹریفک بحال رکھنے کی ہدایت کریں۔
```

---

## 4. RAG Pipeline (`rag/`)

### `rag/__init__.py`
*(Leave empty or import retrieval functions)*

### `rag/knowledge_base.py`
```python
"""Free local RAG index builder for Haalat."""
from __future__ import annotations
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INDEX_DIR = Path(__file__).resolve().parent / "local_index"

CATEGORY_COLLECTION = "emergency_categories"
PROTOCOL_COLLECTION = "emergency_protocols"

SOURCE_FILES = {
    CATEGORY_COLLECTION: DATA_DIR / "emergency_categories.txt",
    PROTOCOL_COLLECTION: DATA_DIR / "emergency_protocols.txt",
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")

def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())

def _load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Knowledge source file not found: {path}")
    return path.read_text(encoding="utf-8")

def _split_text(text: str, source_name: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.create_documents([text], metadatas=[{"source": source_name}])

def _build_index_payload(collection_name: str, source_path: Path) -> dict[str, Any]:
    documents = _split_text(_load_text(source_path), source_path.name)
    if not documents:
        raise RuntimeError(f"No chunks produced for {source_path}")

    document_tokens = [tokenize(document.page_content) for document in documents]
    document_frequencies: Counter[str] = Counter()

    for tokens in document_tokens:
        document_frequencies.update(set(tokens))

    total_documents = len(documents)
    chunks = []

    for index, document in enumerate(documents):
        tokens = document_tokens[index]
        term_counts = Counter(tokens)
        chunks.append({
            "id": f"{collection_name}-{index}",
            "text": document.page_content,
            "metadata": document.metadata,
            "term_counts": dict(term_counts),
            "token_count": max(len(tokens), 1),
        })

    idf = {
        token: math.log((1 + total_documents) / (1 + frequency)) + 1
        for token, frequency in document_frequencies.items()
    }

    return {
        "collection": collection_name,
        "source": str(source_path),
        "retriever": "local_tfidf",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "document_count": total_documents,
        "idf": idf,
        "chunks": chunks,
    }

def _index_path(collection_name: str) -> Path:
    return INDEX_DIR / f"{collection_name}.json"

def collection_exists(collection_name: str) -> bool:
    path = _index_path(collection_name)
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return bool(payload.get("chunks"))

class HaalatKnowledgeBase:
    def __init__(self, index_directory: Path | str = INDEX_DIR) -> None:
        self.index_directory = Path(index_directory)
        self.index_directory.mkdir(parents=True, exist_ok=True)

    def build_if_missing(self, force: bool = False, quiet: bool = False) -> None:
        for collection_name, source_path in SOURCE_FILES.items():
            if not force and collection_exists(collection_name):
                if not quiet:
                    print(f"Local index '{collection_name}' already exists. Skipping build.")
                continue
            self.build_collection(collection_name, source_path)

    def build_collection(self, collection_name: str, source_path: Path) -> None:
        payload = _build_index_payload(collection_name, source_path)
        output_path = _index_path(collection_name)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Built local index '{collection_name}' with {payload['document_count']} chunks.")

def build_knowledge_base(force: bool = False, quiet: bool = False) -> None:
    HaalatKnowledgeBase().build_if_missing(force=force, quiet=quiet)

if __name__ == "__main__":
    build_knowledge_base(force=True)
```

### `rag/retriever.py`
```python
"""Free local retrieval helpers for Haalat using the JSON TF-IDF indexes."""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any

try:
    from .knowledge_base import (
        CATEGORY_COLLECTION,
        INDEX_DIR,
        PROTOCOL_COLLECTION,
        build_knowledge_base,
        tokenize,
    )
except ImportError:
    from knowledge_base import (
        CATEGORY_COLLECTION,
        INDEX_DIR,
        PROTOCOL_COLLECTION,
        build_knowledge_base,
        tokenize,
    )

DEFAULT_TOP_K = 3

def _index_path(collection_name: str) -> Path:
    return INDEX_DIR / f"{collection_name}.json"

def _load_index(collection_name: str) -> dict[str, Any]:
    build_knowledge_base(quiet=True)
    path = _index_path(collection_name)
    if not path.exists():
        raise RuntimeError(f"Local retrieval index not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Local retrieval index is invalid JSON: {path}") from exc

def _score_chunk(query_terms: dict[str, int], chunk: dict[str, Any], idf: dict[str, float]) -> float:
    score = 0.0
    chunk_terms = chunk.get("term_counts", {})
    chunk_length = max(float(chunk.get("token_count", 1)), 1.0)

    for token, query_count in query_terms.items():
        if token not in chunk_terms:
            continue
        term_frequency = float(chunk_terms[token]) / chunk_length
        score += query_count * term_frequency * float(idf.get(token, 1.0))

    text = str(chunk.get("text", "")).lower()
    if text.startswith("protocol:") or text.startswith("category:"):
        heading_tokens = set(tokenize(text[:160]))
        overlap = heading_tokens.intersection(query_terms)
        score += 0.15 * len(overlap)

    return score

def _retrieve_context(collection_name: str, query: str, top_k: int = DEFAULT_TOP_K) -> list[str]:
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    index = _load_index(collection_name)
    tokens = tokenize(query)
    if not tokens:
        return []

    query_terms = {token: tokens.count(token) for token in set(tokens)}
    idf = index.get("idf", {})

    ranked = []
    for chunk in index.get("chunks", []):
        score = _score_chunk(query_terms, chunk, idf)
        ranked.append((score, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    matches = [chunk["text"] for score, chunk in ranked[:top_k] if score > 0]

    if matches:
        return matches
    return [chunk["text"] for chunk in index.get("chunks", [])[:top_k]]

def retrieve_category_context(query: str) -> list[str]:
    return _retrieve_context(CATEGORY_COLLECTION, query)

def retrieve_protocol_context(query: str) -> list[str]:
    return _retrieve_context(PROTOCOL_COLLECTION, query)
```

### `rag/prompt_builder.py`
```python
"""Prompt assembly helpers for Gemini generation."""
from __future__ import annotations
from rag.retriever import retrieve_category_context, retrieve_protocol_context

SYSTEM_PROMPT = """You are Haalat, a real-time emergency intelligence assistant for Pakistan.

Core operating rules:
1. Preserve the user's source language in all user-facing text. If the user mixes Roman Urdu and English, respond in the same mixed style.
2. Treat emergencies conservatively. If cardiac arrest, unconsciousness, severe bleeding, gas leak, or airway danger is possible, escalate severity.
3. Use the provided RAG context as the source of truth for categories, severity, and first-response guidance.
4. Give concise, dispatch-ready output. Do not invent hospitals, volunteers, phone numbers, or distances.
5. Include immediate safety guidance, nearest resource summary, and a clear emergency type/severity.
6. This is decision-support only; always encourage calling local emergency services for life-threatening cases.
"""

def build_gemini_emergency_prompt(
    user_input: str,
    user_location: str,
    resource_summary: str | None = None,
) -> str:
    category_context = "\n\n---\n\n".join(retrieve_category_context(user_input))
    protocol_context = "\n\n---\n\n".join(retrieve_protocol_context(user_input))
    resource_block = resource_summary or "Resource lookup has not been run yet."

    return f"""{SYSTEM_PROMPT}

LOCAL RAG CONTEXT: EMERGENCY CATEGORIES
{category_context}

LOCAL RAG CONTEXT: FIRST-AID PROTOCOLS
{protocol_context}

RESOURCE LOOKUP RESULT
{resource_block}

USER INPUT
{user_input}

USER LOCATION
{user_location}

TASK
Analyze the user input, infer the source language, classify the emergency type,
assign severity from 1 to 5, and produce a final emergency response in the
user's source language.

OUTPUT FORMAT
Return exactly these sections:
1. Language:
2. Emergency:
3. Severity:
4. Immediate action:
5. Nearest help:
6. Why:
"""
```

---

## 5. CrewAI Agents & Tasks

### `agents.py`
```python
"""CrewAI agent definitions for the Haalat emergency intelligence workflow."""
from __future__ import annotations
import os
from pathlib import Path
from crewai import Agent, LLM
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import emergency_rag_tool, location_finder_tool

PROJECT_ROOT = Path(__file__).resolve().parent
REQUESTED_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL = "gemini-2.0-flash"

def _gemini_api_key() -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env.")
    return api_key

def _normalize_model_name(model_name: str) -> str:
    return model_name.removeprefix("models/")

def _resolve_gemini_model() -> str:
    preferred_model = os.getenv("HAALAT_GEMINI_MODEL", REQUESTED_GEMINI_MODEL)
    preferred_model = _normalize_model_name(preferred_model)
    api_key = _gemini_api_key()
    try:
        client = genai.Client(api_key=api_key)
        available_models = {
            _normalize_model_name(model.name)
            for model in client.models.list()
            if "generateContent" in str(getattr(model, "supported_actions", []))
        }
    except Exception:
        return preferred_model
    if preferred_model in available_models:
        return preferred_model
    return FALLBACK_GEMINI_MODEL

GEMINI_MODEL = _resolve_gemini_model()

def _gemini_chat_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=_gemini_api_key(),
        temperature=0.1,
    )

def _crewai_gemini_llm() -> LLM:
    return LLM(
        model=f"gemini/{GEMINI_MODEL}",
        api_key=_gemini_api_key(),
        temperature=0.1,
    )

gemini_chat_model = _gemini_chat_model()
llm = _crewai_gemini_llm()

language_router_agent = Agent(
    role="South Asian Emergency Language Router",
    goal="Identify whether report is text/audio, detect source language, and preserve it downstream.",
    backstory="You are a translation expert trained in Urdu, Sindhi, Pashto, English, and Roman Urdu.",
    llm=llm,
    allow_delegation=False,
    verbose=False,
    multimodal=True,
    max_retry_limit=0,
)

emergency_classifier_agent = Agent(
    role="Emergency Triage Paramedic",
    goal="Analyze emergency, read categories RAG, assign severity 1-5.",
    backstory="You are a triage paramedic. You write reasoning in user's detected source language.",
    tools=[emergency_rag_tool],
    llm=llm,
    allow_delegation=False,
    verbose=False,
    max_retry_limit=0,
)

resource_locator_agent = Agent(
    role="Field Asset Coordinator",
    goal="Find closest relevant emergency services and volunteers.",
    backstory="You search Karachi/Islamabad databases and format dispatches in detected languages.",
    tools=[location_finder_tool],
    llm=llm,
    allow_delegation=False,
    verbose=False,
    max_retry_limit=0,
)
```

### `tasks.py`
```python
"""Task definitions for Haalat's sequential emergency workflow."""
from __future__ import annotations
from crewai import Task
from agents import (
    emergency_classifier_agent,
    language_router_agent,
    resource_locator_agent,
)

language_detection_task = Task(
    description=(
        "Inspect the incoming user input: {user_input}\n\n"
        "Detect the source language: Urdu, Sindhi, Pashto, English, or Mixed/Unknown. "
        "Force downstream tasks to output user-facing response in this language."
    ),
    expected_output=(
        "A JSON block only:\n"
        "{\n"
        '  "detected_language": "Urdu|Sindhi|Pashto|English|Mixed/Unknown",\n'
        '  "input_type": "audio|text"\n'
        "}"
    ),
    agent=language_router_agent,
)

classification_task = Task(
    description=(
        "Using input {user_input} and detected language, call emergency_rag_tool. "
        "Assign severity 1-5 and write reasoning in user's source language."
    ),
    expected_output=(
        "A JSON block only:\n"
        "{\n"
        '  "type": "emergency type",\n'
        '  "severity": 1-5,\n'
        '  "reasoning": "reasoning in source language"\n'
        "}"
    ),
    agent=emergency_classifier_agent,
    context=[language_detection_task],
)

resource_location_task = Task(
    description=(
        "Using classified emergency, location {user_location}, and detected language, "
        "call location_finder_tool. Produce final dispatch in source language."
    ),
    expected_output="Concise dispatch details containing emergency type, services, and volunteers.",
    agent=resource_locator_agent,
    context=[language_detection_task, classification_task],
)
```

---

## 6. Custom Tools

### `tools.py`
```python
"""Custom tools used by Haalat CrewAI agents with multi-region support."""
from __future__ import annotations
import json
import math
import re
from pathlib import Path
from typing import Any
from crewai.tools import tool

try:
    from rag.retriever import retrieve_category_context, retrieve_protocol_context
except ImportError:
    from .rag.retriever import retrieve_category_context, retrieve_protocol_context

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

KNOWN_LOCATIONS = {
    "garden": (24.8665, 67.0235),
    "garden karachi": (24.8665, 67.0235),
    "garden east": (24.8662, 67.0239),
    "garden west": (24.8648, 67.0207),
    "soldier bazaar": (24.8681, 67.0261),
    "civil hospital": (24.8617, 67.0129),
    "saddar": (24.8550, 67.0050),
    "clifton": (24.8325, 67.0430),
    "gulshan": (24.8770, 67.0412),
    "gulshan-e-iqbal": (24.9100, 67.0900),
    "north nazimabad": (24.9300, 67.0400),
    "pechs": (24.8900, 67.0450),
    "lyari": (24.8800, 66.9800),
    "korangi": (24.8300, 67.1400),
    "malir": (24.9000, 67.2000),
    "dha": (24.8100, 67.0500),
    "federal b area": (24.9200, 67.0550),
    "blue area": (33.7167, 73.0587),
    "islamabad": (33.7200, 73.0700),
    "g-8": (33.6933, 73.0586),
    "g-9": (33.6830, 73.0600),
    "f-8": (33.7200, 73.0650),
    "f-7": (33.7240, 73.0720),
    "i-8": (33.7100, 73.0500),
    "h-8": (33.6880, 73.0650),
    "g-10": (33.6720, 73.0700),
    "f-10": (33.6950, 73.0620),
    "e-7": (33.7280, 73.0800),
    "i-10": (33.6980, 73.0420),
    "shifa hospital": (33.7172, 73.0593),
    "pims": (33.6933, 73.0586),
}

REGION_AREAS = {
    "karachi": [
        "Garden", "Saddar", "Clifton", "Gulshan", "Gulshan-e-Iqbal",
        "North Nazimabad", "PECHS", "Lyari", "Korangi", "Malir", "DHA",
        "Federal B Area", "Soldier Bazaar", "Garden East", "Garden West"
    ],
    "islamabad": [
        "Blue Area", "G-8", "G-9", "F-8", "F-7", "F-10", "I-8", "H-8",
        "G-10", "E-7", "I-10"
    ],
    "rawalpindi": [
        "Saddar", "Rawalpindi Cantt", "Westridge", "Committee Chowk",
        "Chandni Chowk", "Satellite Town", "Dhoke Choudharian", "Lalazar"
    ],
}

REGION_CENTERS = {
    "karachi": (24.8600, 67.0100),
    "islamabad": (33.7167, 73.0587),
    "rawalpindi": (33.6010, 73.0510),
}

SKILL_KEYWORDS = {
    "cardiac": {"cpr", "aed", "basic_life_support"},
    "heart": {"cpr", "aed", "basic_life_support"},
    "arrest": {"cpr", "aed", "basic_life_support"},
    "dil": {"cpr", "aed", "basic_life_support"},
    "chest": {"cpr", "aed", "basic_life_support"},
    "bleeding": {"bleeding_control", "trauma_support", "first_aid"},
    "blood": {"bleeding_control", "trauma_support", "first_aid"},
    "khoon": {"bleeding_control", "trauma_support", "first_aid"},
    "trauma": {"bleeding_control", "trauma_support", "first_aid"},
    "burn": {"burn_care", "first_aid", "triage"},
    "fire": {"burn_care", "first_aid", "triage"},
    "gas": {"triage", "first_aid", "basic_life_support"},
    "drowning": {"basic_life_support", "rescue", "cpr"},
    "seizure": {"basic_life_support", "first_aid"},
    "allergic": {"basic_life_support", "cpr"},
    "stroke": {"basic_life_support", "cpr"},
}

def _load_json(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required data file missing: {path}") from exc
    return data if isinstance(data, list) else []

def _clean_location(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", value.lower()).strip()

def _parse_location(user_location: str) -> tuple[float, float]:
    if not user_location or not user_location.strip():
        raise ValueError("user_location must be non-empty.")
    coordinate_match = re.search(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", user_location)
    if coordinate_match:
        return float(coordinate_match.group(1)), float(coordinate_match.group(2))
    normalized = _clean_location(user_location)
    if normalized in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[normalized]
    for place_name, coordinates in KNOWN_LOCATIONS.items():
        if place_name in normalized:
            return coordinates
    for region_name, coords in REGION_CENTERS.items():
        if region_name in normalized:
            return coords
    raise ValueError(f"Could not resolve location: '{user_location}'")

def _haversine_km(origin_lat: float, origin_lng: float, target_lat: float, target_lng: float) -> float:
    radius_km = 6371.0
    d_lat = math.radians(target_lat - origin_lat)
    d_lng = math.radians(target_lng - origin_lng)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(origin_lat)) * math.cos(math.radians(target_lat)) * math.sin(d_lng / 2) ** 2
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def _nearest_record(records: list[dict[str, Any]], origin: tuple[float, float]) -> tuple[dict[str, Any], float]:
    if not records:
        raise RuntimeError("No records found.")
    lat, lng = origin
    ranked = sorted(
        ((record, _haversine_km(lat, lng, float(record["lat"]), float(record["lng"]))) for record in records),
        key=lambda item: item[1]
    )
    return ranked[0]

def _skill_terms_for_emergency(emergency_type: str) -> set[str]:
    normalized = _clean_location(emergency_type)
    skills: set[str] = set()
    for keyword, mapped_skills in SKILL_KEYWORDS.items():
        if keyword in normalized:
            skills.update(mapped_skills)
    return skills or {"first_aid", "triage", "basic_life_support"}

def _matching_volunteers(volunteers: list[dict[str, Any]], emergency_type: str) -> list[dict[str, Any]]:
    needed_skills = _skill_terms_for_emergency(emergency_type)
    matches = []
    for volunteer in volunteers:
        volunteer_skills = {str(skill).lower() for skill in volunteer.get("skills", [])}
        if needed_skills.intersection(volunteer_skills):
            matches.append(volunteer)
    return matches or volunteers

def get_services_for_region(region: str) -> list[dict[str, Any]]:
    all_services = _load_json(DATA_DIR / "services.json")
    if region and region != "all":
        region_lower = region.lower()
        return [s for s in all_services if s.get("region", "").lower() == region_lower]
    return all_services

def get_volunteers_for_region(region: str) -> list[dict[str, Any]]:
    all_volunteers = _load_json(DATA_DIR / "volunteers.json")
    if region and region != "all":
        region_lower = region.lower()
        return [v for v in all_volunteers if v.get("region", "").lower() == region_lower]
    return all_volunteers

def generate_incident_map(
    user_location: str,
    services: list[dict[str, Any]] | None = None,
    volunteers: list[dict[str, Any]] | None = None,
    region: str = "karachi",
    lat: float | None = None,
    lng: float | None = None,
) -> str:
    """Generate an HTML map with Folium showing user position, services, and volunteers."""
    import folium
    from folium import plugins
    from folium.plugins import MarkerCluster

    if lat is not None and lng is not None:
        origin = (lat, lng)
    else:
        try:
            origin = _parse_location(user_location)
        except ValueError:
            center = REGION_CENTERS.get(region, REGION_CENTERS["karachi"])
            origin = center

    center_lat, center_lng = origin

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=14,
        control_scale=True,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&apistyle=s.t%3A0|p.v%3Aoff",
        attr="Haalat | Google Maps",
    )

    # User marker (pulsing red) with Street View link
    streetview_url = f"https://www.google.com/maps?layer=c&cbll={center_lat},{center_lng}"
    folium.Marker(
        [center_lat, center_lng],
        popup=f"""
        <div style="font-family: Inter, sans-serif; min-width: 180px;">
            <b>📍 Your Location</b><br>
            <span style="color: #666; font-size: 11px;">Lat: {center_lat:.4f}, Lng: {center_lng:.4f}</span><br>
            <a href="{streetview_url}" target="_blank" style="color: #ff3333; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 5px;">
                <i class="fa-solid fa-street-view"></i> Open Google Street View ↗
            </a>
        </div>
        """,
        icon=folium.Icon(color="red", icon="info-sign", prefix="glyphicon"),
    ).add_to(m)

    # Accuracy circle
    folium.Circle(
        [center_lat, center_lng],
        radius=500,
        color="red",
        fill=True,
        fillColor="red",
        fillOpacity=0.08,
        weight=1,
    ).add_to(m)

    # Services layer
    if services:
        svc_cluster = MarkerCluster(name="Emergency Services").add_to(m)
        for svc in services:
            svc_lat = svc.get("lat")
            svc_lng = svc.get("lng")
            streetview_url = f"https://www.google.com/maps?layer=c&cbll={svc_lat},{svc_lng}"
            popup_html = f"""
            <div style="font-family: Inter, sans-serif; min-width: 200px;">
                <b style="color: #ff3333;">🏥 {svc.get('name', 'Service')}</b><br>
                <span style="color: #666;">Type: {svc.get('type', 'N/A')}</span><br>
                <span style="color: #666;">📞 {svc.get('phone', 'N/A')}</span><br>
                <span style="color: #666;">📍 {svc.get('area', 'N/A')}</span><br>
                <a href="{streetview_url}" target="_blank" style="color: #ff3333; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 5px;">
                    <i class="fa-solid fa-street-view"></i> Open Street View ↗
                </a>
            </div>
            """
            folium.Marker(
                [svc["lat"], svc["lng"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(
                    color="blue" if svc.get("type") == "hospital" else "green",
                    icon="plus" if svc.get("type") == "hospital" else "ambulance",
                    prefix="fa" if svc.get("type") != "hospital" else "glyphicon",
                ),
            ).add_to(svc_cluster)

    # Volunteers layer
    if volunteers:
        vol_cluster = MarkerCluster(name="Volunteers").add_to(m)
        for vol in volunteers:
            status = vol.get("availability", "unknown")
            status_color = "green" if status == "available" else "orange"
            vol_lat = vol.get("lat")
            vol_lng = vol.get("lng")
            streetview_url = f"https://www.google.com/maps?layer=c&cbll={vol_lat},{vol_lng}"
            popup_html = f"""
            <div style="font-family: Inter, sans-serif; min-width: 200px;">
                <b style="color: #00cc66;">👤 {vol.get('name', 'Volunteer')}</b><br>
                <span style="color: #666;">Status: {'✅ Available' if status == 'available' else '⏰ On Call'}</span><br>
                <span style="color: #666;">📞 {vol.get('phone', 'N/A')}</span><br>
                <span style="color: #666;">📍 {vol.get('area', 'N/A')}</span><br>
                <span style="color: #666;">Skills: {', '.join(vol.get('skills', []))}</span><br>
                <a href="{streetview_url}" target="_blank" style="color: #00cc66; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 5px;">
                    <i class="fa-solid fa-street-view"></i> Open Street View ↗
                </a>
            </div>
            """
            folium.Marker(
                [vol["lat"], vol["lng"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=status_color, icon="user", prefix="fa"),
            ).add_to(vol_cluster)

    plugins.Fullscreen(position="topright").add_to(m)
    folium.LayerControl().add_to(m)
    return m.get_root()._repr_html_()

@tool
def emergency_rag_tool(query: str) -> str:
    """Classify an emergency report using local categories.txt index."""
    try:
        from rag.retriever import retrieve_category_context
        return "\n\n---\n\n".join(retrieve_category_context(query))
    except Exception as exc:
        return f"Category retrieval failed: {exc}"

@tool
def protocols_rag_tool(query: str) -> str:
    """Retrieve first-aid protocol guidance from local protocols.txt index."""
    try:
        from rag.retriever import retrieve_protocol_context
        return "\n\n---\n\n".join(retrieve_protocol_context(query))
    except Exception as exc:
        return f"Protocol retrieval failed: {exc}"

@tool
def location_finder_tool(emergency_type: str, user_location: str) -> str:
    """Find the nearest emergency service and nearest volunteer."""
    try:
        origin = _parse_location(user_location)
        services = _load_json(DATA_DIR / "services.json")
        volunteers = _matching_volunteers(_load_json(DATA_DIR / "volunteers.json"), emergency_type)

        nearest_service, service_distance = _nearest_record(services, origin)
        nearest_volunteer, volunteer_distance = _nearest_record(volunteers, origin)

        volunteer_skills = ", ".join(nearest_volunteer.get("skills", []))
        service_capabilities = ", ".join(nearest_service.get("services", []))

        return (
            f"Nearest service: {nearest_service['name']} "
            f"({nearest_service['type']}, {service_distance:.2f} km away). Phone: {nearest_service['phone']}.\n"
            f"Nearest matching volunteer: {nearest_volunteer['name']} "
            f"({volunteer_distance:.2f} km away). Phone: {nearest_volunteer['phone']}. Skills: {volunteer_skills}."
        )
    except Exception as exc:
        return f"Location lookup failed: {exc}"
```

---

## 7. FastAPI Backend Application

### `app.py`
```python
"""
Haalat (حالت) — Pakistan's First Real-Time Multi-Agent Emergency Intelligence System.
FastAPI Web App, custom HTML frontend console, auto-geolocation routing, and Admin panel dashboard.
"""
from __future__ import annotations
import os
import json
import re
import time
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

def _init_rag():
    from rag.knowledge_base import build_knowledge_base
    build_knowledge_base(quiet=True)

_init_rag()

from tools import (
    REGION_CENTERS,
    generate_incident_map,
    get_services_for_region,
    get_volunteers_for_region,
    location_finder_tool,
)
from rag.retriever import retrieve_protocol_context

app = FastAPI(title="Haalat Emergency Intelligence System")

REQUESTED_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL = "gemini-2.0-flash"

def _gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return ""
    return api_key

def _normalize_model_name(model_name: str) -> str:
    return model_name.removeprefix("models/")

def _resolve_gemini_model() -> str:
    preferred_model = os.getenv("HAALAT_GEMINI_MODEL", REQUESTED_GEMINI_MODEL)
    preferred_model = _normalize_model_name(preferred_model)
    api_key = _gemini_api_key()
    if not api_key:
        return preferred_model
    try:
        client = genai.Client(api_key=api_key)
        available_models = {
            _normalize_model_name(model.name)
            for model in client.models.list()
            if "generateContent" in str(getattr(model, "supported_actions", []))
        }
    except Exception:
        return preferred_model
    if preferred_model in available_models:
        return preferred_model
    return FALLBACK_GEMINI_MODEL

GEMINI_MODEL = _resolve_gemini_model()

class ReportRequest(BaseModel):
    message: str
    audio_path: str | None = None
    region: str
    area: str
    lat: float | None = None
    lng: float | None = None

def _load_incidents():
    path = PROJECT_ROOT / "incident_log.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data if isinstance(data, list) else []

def _save_incident(incident: dict):
    path = PROJECT_ROOT / "incident_log.json"
    incidents = _load_incidents()
    incident["time"] = time.strftime("%H:%M")
    incidents.append(incident)
    path.write_text(json.dumps(incidents, indent=2, ensure_ascii=False), encoding="utf-8")

def _demo_incidents():
    return [
        {"time": "22:14", "area": "Garden East, Karachi", "type": "Gas Leak", "severity": 4, "lat": 24.8662, "lng": 67.0239, "user_message": "Sui gas cylinder leaking inside ground floor shop."},
        {"time": "22:16", "area": "Garden West, Karachi", "type": "Gas Leak", "severity": 4, "lat": 24.8648, "lng": 67.0207, "user_message": "Strong smell of LPG outdoors near the apartments."},
        {"time": "22:18", "area": "Saddar, Rawalpindi", "type": "Cardiac Event", "severity": 5, "lat": 33.6010, "lng": 73.0510, "user_message": "Elderly man fell down clutching chest near market."},
    ]

def _classify_emergency(query: str) -> dict:
    q = query.lower()
    CATEGORIES = [
        ("Cardiac Event", 5, ["dil", "heart", "cardiac", "chest", "behosh", "unconscious", "cpr", "pulse", "dil ka dorah", "seene mein dard"]),
        ("Severe Bleeding", 4, ["bleed", "blood", "khoon", "zakhm", "cut", "wound"]),
        ("Gas Leak", 4, ["gas", "smell", "boo", "cylinder", "sui gas", "leak"]),
        ("Burn Injury", 3, ["burn", "jal", "aag", "fire", "chemical", "tezaab"]),
    ]
    for name, severity, keywords in CATEGORIES:
        if any(k in q for k in keywords):
            return {"type": name, "severity": severity}
    return {"type": "General Emergency", "severity": 3}

def _get_resources_text(emergency_type: str, location: str) -> str:
    try:
        return location_finder_tool.run(emergency_type=emergency_type, user_location=location)
    except Exception:
        return "Resource lookup pending."

def _extract_resource(text: str, label: str) -> dict[str, str]:
    lines = text.splitlines()
    body = ""
    for line in lines:
        if label.lower() in line.strip().lower():
            body = line.strip()
            break
    if not body:
        return {"name": "None", "phone": "---", "distance": "---"}
    phone = "---"
    distance = "---"
    pm = re.search(r"Phone:\s*([^,\n]+)", body)
    if pm: phone = pm.group(1).strip()
    dm = re.search(r"([\d.]+)\s*km", body)
    if dm: distance = f"{dm.group(1)} km"
    name = re.split(r",\s*(?:Phone|Distance):", body, maxsplit=1)[0]
    name = re.sub(r"^Nearest (?:service|matching volunteer):\s*", "", name, flags=re.IGNORECASE)
    return {"name": name.strip(), "phone": phone, "distance": distance}

def _protocol_for(emergency_type: str) -> str:
    snippets = retrieve_protocol_context(emergency_type)
    if snippets:
        lines = [l.strip() for l in snippets[0].splitlines() if l.strip()]
        return "\n\n".join(lines[:6])
    return "First aid protocol loading..."

def _mass_event_check(area_name: str) -> tuple[bool, str]:
    incidents = _load_incidents() or _demo_incidents()
    area_part = area_name.split(",")[0].strip().lower() if area_name else ""
    recent = [i for i in incidents if area_part in i.get("area", "").lower() and i.get("type") in ["Gas Leak", "Fire", "Building Collapse"]]
    if len(recent) >= 2:
        report = (
            f"CIVIL DEFENSE SITUATION REPORT\nCluster: {area_part.title()}\nActive linked incidents: {len(recent)}\n"
            "Assessment: Multi-incident pattern detected.\nAction: Escalate ambulance staging.\n\n"
            "شہری دفاعی صورتحال رپورٹ\nعلاقہ: {area_part.title()}\nمنسلک واقعات: {len(recent)}"
        )
        return True, report
    return False, "No active mass-event clusters flagged in district."

def transcribe_audio_if_possible(audio_path: str) -> str:
    api_key = _gemini_api_key()
    if not api_key:
        return "[Audio Report Saved]"
    try:
        client = genai.Client(api_key=api_key)
        audio_file = Path(audio_path)
        if audio_file.exists():
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    genai.types.Part.from_bytes(data=audio_file.read_bytes(), mime_type="audio/wav"),
                    "Transcribe the spoken audio and translate it to English. If already in English, just return the transcription. Return ONLY the final English translation, with no labels."
                ]
            )
            return response.text.strip()
    except Exception as e:
        print(f"[Haalat] Gemini transcription error: {e}")
    return "[Audio Report Received]"

def classify_emergency_with_llm(message: str, location_str: str, resources_summary: str) -> dict:
    api_key = _gemini_api_key()
    if not api_key:
        return {}
    try:
        from rag.prompt_builder import build_gemini_emergency_prompt
        client = genai.Client(api_key=api_key)
        prompt = build_gemini_emergency_prompt(message, location_str, resources_summary)
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "detected_language": {"type": "STRING"},
                        "type": {"type": "STRING"},
                        "severity": {"type": "INTEGER"},
                        "immediate_action": {"type": "STRING"},
                        "nearest_help": {"type": "STRING"},
                        "why": {"type": "STRING"}
                    },
                    "required": ["detected_language", "type", "severity", "immediate_action", "nearest_help", "why"]
                }
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[Haalat] Gemini classification error: {e}")
    return {}

@app.get("/", response_class=HTMLResponse)
def get_home():
    html_path = PROJECT_ROOT / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/logo.png")
def get_logo():
    logo_path = PROJECT_ROOT / "haalat_logo_1781643712746.png"
    if logo_path.exists():
        return FileResponse(logo_path)
    raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/api/incidents")
def get_incidents():
    incidents = _load_incidents()
    if not incidents:
        incidents = _demo_incidents()
    return incidents

@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    audio_dir = PROJECT_ROOT / "data" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    file_path = audio_dir / f"recording_{int(time.time())}.wav"
    try:
        with file_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return {"file_path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {e}")

@app.get("/api/map", response_class=HTMLResponse)
def get_map(region: str = "karachi", area: str = "Garden", lat: float | None = None, lng: float | None = None):
    city_map = {"karachi": "Karachi", "islamabad": "Islamabad", "rawalpindi": "Rawalpindi"}
    city = city_map.get(region.lower(), "Karachi")
    location_str = f"{area}, {city}"
    
    svcs = get_services_for_region(region)
    vols = get_volunteers_for_region(region)
    map_html = generate_incident_map(location_str, services=svcs, volunteers=vols, region=region, lat=lat, lng=lng)
    return HTMLResponse(content=map_html)

@app.post("/api/report")
async def report_emergency(request: ReportRequest):
    message_text = request.message
    if request.audio_path:
        transcription = transcribe_audio_if_possible(request.audio_path)
        if message_text and message_text != "[AUDIO REPORT TRANSMITTED]":
            message_text = f"{message_text} [Transcribed: {transcription}]"
        else:
            message_text = transcription

    city_map = {"karachi": "Karachi", "islamabad": "Islamabad", "rawalpindi": "Rawalpindi"}
    city = city_map.get(request.region.lower(), "Karachi")
    location_str = f"{request.area}, {city}"

    if request.lat is not None and request.lng is not None:
        lat, lng = request.lat, request.lng
    else:
        try:
            from tools import _parse_location
            lat, lng = _parse_location(location_str)
        except Exception:
            lat, lng = REGION_CENTERS.get(request.region.lower(), (24.8665, 67.0235))

    api_key = _gemini_api_key()
    has_llm = bool(api_key)
    
    if has_llm:
        resources_summary = _get_resources_text("General Emergency", location_str)
        llm_res = classify_emergency_with_llm(message_text, location_str, resources_summary)
        if llm_res:
            detected_language = llm_res.get("detected_language", "English/Urdu")
            emergency_type = llm_res.get("type", "General Emergency")
            severity = llm_res.get("severity", 3)
            first_aid_steps = llm_res.get("immediate_action", "")
            reasoning = llm_res.get("why", "")
        else:
            fallback = _classify_emergency(message_text)
            detected_language = "English/Roman Urdu"
            emergency_type = fallback["type"]
            severity = fallback["severity"]
            first_aid_steps = _protocol_for(emergency_type)
            reasoning = f"Direct rule matched incident category to {emergency_type}."
    else:
        fallback = _classify_emergency(message_text)
        detected_language = "English/Roman Urdu"
        emergency_type = fallback["type"]
        severity = fallback["severity"]
        first_aid_steps = _protocol_for(emergency_type)
        reasoning = f"Standard pattern rules classified report context to category '{emergency_type}'."

    resources = _get_resources_text(emergency_type, location_str)
    unit = _extract_resource(resources, "service")
    vol = _extract_resource(resources, "volunteer")

    _save_incident({
        "type": emergency_type,
        "severity": severity,
        "area": location_str,
        "lat": lat,
        "lng": lng,
        "user_message": message_text[:120],
    })

    is_mass_event, sitrep = _mass_event_check(location_str)

    if has_llm:
        agent_log = [
            f"Language Router Agent: Scanned emergency transmission. Detected: '{detected_language}'.",
            f"Emergency Triage Paramedic: Classified incident as '{emergency_type}' (Severity: {severity}/5) via local RAG.",
            f"Field Asset Coordinator: Alerted volunteer {vol['name']} ({vol['distance']} away, phone: {vol['phone']}).",
            f"Mass Event Analyst: Cluster check complete. Mass event: {is_mass_event}."
        ]
    else:
        agent_log = [
            "SYSTEM: Offline fallback mode activated (No valid GEMINI_API_KEY).",
            f"Emergency Triage Paramedic: Matched keywords. Category: '{emergency_type}' (Severity: {severity}/5).",
            f"Field Asset Coordinator: Matched mock databases. Dispatch: {unit['name']}.",
        ]

    return JSONResponse(content={
        "type": emergency_type,
        "severity": severity,
        "description": message_text,
        "detected_language": detected_language,
        "first_aid_steps": first_aid_steps,
        "nearest_service": {
            "name": unit["name"],
            "type": "Ambulance / Hospital",
            "phone": unit["phone"],
            "distance_km": unit["distance"].replace(" km", "") if " km" in unit["distance"] else unit["distance"]
        },
        "nearest_volunteer": {
            "name": vol["name"],
            "skills": vol["skills"] if "skills" in vol else "First Aid & CPR",
            "phone": vol["phone"],
            "distance_km": vol["distance"].replace(" km", "") if " km" in vol["distance"] else vol["distance"]
        },
        "is_mass_event": is_mass_event,
        "sitrep": sitrep,
        "agent_log": agent_log
    })

# ─── CONFIG & ADMIN ENDPOINTS ────────────────────────────────────────────────
@app.get("/api/config")
def get_config():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    is_valid_key = bool(api_key and api_key != "your_maps_key_here")
    return {
        "google_maps_api_key": api_key,
        "is_valid_key": is_valid_key
    }

@app.get("/admin", response_class=HTMLResponse)
def get_admin():
    html_path = PROJECT_ROOT / "templates" / "admin.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="admin.html template not found")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/api/admin/volunteers")
def get_admin_volunteers():
    from tools import DATA_DIR, _load_json
    try:
        volunteers = _load_json(DATA_DIR / "volunteers.json")
        return volunteers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/services")
def get_admin_services():
    from tools import DATA_DIR, _load_json
    try:
        services = _load_json(DATA_DIR / "services.json")
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/clear-incidents")
def clear_incidents():
    path = PROJECT_ROOT / "incident_log.json"
    try:
        path.write_text(json.dumps([], indent=2, ensure_ascii=False), encoding="utf-8")
        return {"status": "success", "message": "All incidents cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteIncidentRequest(BaseModel):
    time: str
    area: str
    type: str

@app.post("/api/admin/delete-incident")
def delete_incident(request: DeleteIncidentRequest):
    path = PROJECT_ROOT / "incident_log.json"
    try:
        incidents = _load_incidents()
        filtered = []
        removed = False
        for inc in incidents:
            if not removed and inc.get("time") == request.time and inc.get("area") == request.area and inc.get("type") == request.type:
                removed = True
                continue
            filtered.append(inc)
        path.write_text(json.dumps(filtered, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"status": "success", "message": "Incident removed." if removed else "Incident not found."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ToggleVolunteerRequest(BaseModel):
    id: str

@app.post("/api/admin/toggle-volunteer")
def toggle_volunteer(request: ToggleVolunteerRequest):
    from tools import DATA_DIR, _load_json
    path = DATA_DIR / "volunteers.json"
    try:
        volunteers = _load_json(path)
        updated = False
        for vol in volunteers:
            if vol.get("id") == request.id:
                current = vol.get("availability", "on call")
                vol["availability"] = "available" if current == "on call" else "on call"
                updated = True
                break
        if updated:
            path.write_text(json.dumps(volunteers, indent=2, ensure_ascii=False), encoding="utf-8")
            return {"status": "success", "message": "Volunteer status toggled.", "volunteers": volunteers}
        raise HTTPException(status_code=404, detail="Volunteer not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    if len(_load_incidents()) < 2:
        for inc in _demo_incidents():
            _save_incident({
                "type": inc["type"], "severity": inc["severity"], "area": inc["area"],
                "lat": inc["lat"], "lng": inc["lng"], "user_message": inc["user_message"],
            })
    print("[Haalat] Starting FastAPI Command Center on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
```
