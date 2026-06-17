"""
Haalat (حالت) — Pakistan's First Real-Time Multi-Agent Emergency Intelligence System
World-Class Edition: FastAPI Web App, Custom HTML/CSS/JS UI, Geolocation Auto-Detection, Live Agent Console
"""

from __future__ import annotations

import os
import json
import re
import time
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

# ─── RAG INITIALIZATION ──────────────────────────────────────────────────────
def _init_rag():
    from rag.knowledge_base import build_knowledge_base
    build_knowledge_base(quiet=True)

_init_rag()

from tools import (
    REGION_AREAS,
    REGION_CENTERS,
    generate_incident_map,
    get_services_for_region,
    get_volunteers_for_region,
    location_finder_tool,
)
from rag.retriever import retrieve_protocol_context

# Initialize FastAPI
app = FastAPI(title="Haalat Emergency Intelligence System")

# Constants & Configuration
REQUESTED_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL = "gemini-2.0-flash"

EMERGENCY_GIF_MAP = {
    "Cardiac Event": {
        "url": "/instruction-assets/cardiac-cpr.svg",
        "label": "CPR Compression Loop",
        "alt": "Animated CPR compression technique loop",
    },
    "Severe Bleeding": {
        "url": "/instruction-assets/severe-bleeding-pressure.svg",
        "label": "Pressure / Tourniquet Loop",
        "alt": "Animated direct pressure and tourniquet instruction loop",
    },
    "Gas Leak": {
        "url": "/instruction-assets/gas-leak-evacuate.svg",
        "label": "Evacuate / No Sparks Loop",
        "alt": "Animated gas leak evacuation and hazard warning loop",
    },
    "Default": {
        "url": "/instruction-assets/default-radar-alert.svg",
        "label": "Emergency Radar Alert",
        "alt": "Animated amber emergency radar scan loop",
    },
}

INSTRUCTION_VISUAL_SVGS = {
    "cardiac-cpr.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">
<rect width="640" height="360" rx="24" fill="#090d16"/>
<g opacity=".25"><path d="M0 300h640M0 260h640M0 220h640M0 180h640M0 140h640M0 100h640M80 0v360M160 0v360M240 0v360M320 0v360M400 0v360M480 0v360M560 0v360" stroke="#00b0ff"/></g>
<circle cx="320" cy="180" r="125" fill="none" stroke="#ff4a4a" stroke-width="3" opacity=".45"><animate attributeName="r" values="86;145;86" dur="1.1s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;.15;.8" dur="1.1s" repeatCount="indefinite"/></circle>
<path d="M145 232c74 40 226 42 350 0" fill="none" stroke="#eaf2ff" stroke-width="18" stroke-linecap="round"/>
<circle cx="246" cy="185" r="34" fill="#dce8f8"/>
<path d="M276 187c52-20 114-20 166 0l26 52H250z" fill="#22314d" stroke="#eaf2ff" stroke-width="6"/>
<g><path d="M316 74h44v108h-44z" rx="16" fill="#00e676"/><path d="M292 104h92" stroke="#00e676" stroke-width="28" stroke-linecap="round"/><animateTransform attributeName="transform" type="translate" values="0 -22;0 32;0 -22" dur=".58s" repeatCount="indefinite"/></g>
<text x="320" y="318" fill="#ff4a4a" font-size="27" font-family="Arial" font-weight="700" text-anchor="middle">PUSH HARD AND FAST - 100 TO 120 / MIN</text>
</svg>""",
    "severe-bleeding-pressure.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">
<rect width="640" height="360" rx="24" fill="#090d16"/>
<g opacity=".22"><path d="M0 72h640M0 144h640M0 216h640M0 288h640M96 0v360M192 0v360M288 0v360M384 0v360M480 0v360M576 0v360" stroke="#ffb300"/></g>
<path d="M100 215c95-38 330-38 440 0" fill="none" stroke="#f2d1b1" stroke-width="54" stroke-linecap="round"/>
<ellipse cx="325" cy="203" rx="70" ry="28" fill="#ff4a4a"><animate attributeName="rx" values="70;46;70" dur="1s" repeatCount="indefinite"/></ellipse>
<rect x="235" y="151" width="178" height="76" rx="12" fill="#eaf2ff" stroke="#00b0ff" stroke-width="5"><animateTransform attributeName="transform" type="translate" values="0 -12;0 20;0 -12" dur=".72s" repeatCount="indefinite"/></rect>
<path d="M226 132h196" stroke="#00e676" stroke-width="18" stroke-linecap="round"><animate attributeName="stroke-width" values="10;26;10" dur=".72s" repeatCount="indefinite"/></path>
<path d="M260 88h120l-22 36h-76z" fill="#00e676"/>
<text x="320" y="318" fill="#ffb300" font-size="27" font-family="Arial" font-weight="700" text-anchor="middle">APPLY FIRM DIRECT PRESSURE</text>
</svg>""",
    "gas-leak-evacuate.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">
<rect width="640" height="360" rx="24" fill="#090d16"/>
<g opacity=".2"><path d="M0 300h640M0 240h640M0 180h640M0 120h640M0 60h640M80 0v360M160 0v360M240 0v360M320 0v360M400 0v360M480 0v360M560 0v360" stroke="#ffb300"/></g>
<path d="M318 54l205 248H113z" fill="#2d1c08" stroke="#ffb300" stroke-width="8"/>
<text x="318" y="197" fill="#ffb300" font-size="118" font-family="Arial" font-weight="900" text-anchor="middle">!</text>
<g fill="none" stroke="#00e676" stroke-width="10" stroke-linecap="round">
<path d="M160 258h110"/>
<path d="M230 222l44 36-44 36"><animateTransform attributeName="transform" type="translate" values="-20 0;32 0;-20 0" dur="1s" repeatCount="indefinite"/></path>
<path d="M386 258h94"/>
<path d="M440 222l44 36-44 36"><animateTransform attributeName="transform" type="translate" values="-18 0;28 0;-18 0" dur=".9s" repeatCount="indefinite"/></path>
</g>
<g fill="none" stroke="#ff4a4a" stroke-width="5" opacity=".75"><path d="M214 99c42 28-34 48 13 80"/><path d="M421 95c-42 28 34 50-13 82"/><animate attributeName="opacity" values=".2;.9;.2" dur="1.2s" repeatCount="indefinite"/></g>
<text x="320" y="334" fill="#ffb300" font-size="25" font-family="Arial" font-weight="700" text-anchor="middle">EVACUATE - DO NOT USE SWITCHES</text>
</svg>""",
    "default-radar-alert.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">
<rect width="640" height="360" rx="24" fill="#090d16"/>
<g transform="translate(320 180)">
<circle r="132" fill="none" stroke="#ffb300" stroke-width="3" opacity=".35"/>
<circle r="88" fill="none" stroke="#ffb300" stroke-width="2" opacity=".3"/>
<circle r="44" fill="none" stroke="#ffb300" stroke-width="2" opacity=".25"/>
<path d="M0 0L0-142A142 142 0 0 1 122-71z" fill="#ffb300" opacity=".34"><animateTransform attributeName="transform" type="rotate" values="0;360" dur="1.8s" repeatCount="indefinite"/></path>
<circle r="8" fill="#ff4a4a"><animate attributeName="r" values="7;15;7" dur=".8s" repeatCount="indefinite"/></circle>
</g>
<text x="320" y="324" fill="#ffb300" font-size="27" font-family="Arial" font-weight="700" text-anchor="middle">EMERGENCY CONTEXT SCAN ACTIVE</text>
</svg>""",
}

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

# Request Pydantic Schemas
class ReportRequest(BaseModel):
    message: str
    audio_path: str | None = None
    region: str
    area: str
    lat: float | None = None
    lng: float | None = None

# ─── DATABASE HELPERS ────────────────────────────────────────────────────────
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
        {"time": "22:14", "area": "Garden East, Karachi", "type": "Gas Leak", "severity": 4, "lat": 24.8662, "lng": 67.0239},
        {"time": "22:16", "area": "Garden West, Karachi", "type": "Gas Leak", "severity": 4, "lat": 24.8648, "lng": 67.0207},
        {"time": "22:18", "area": "Saddar, Rawalpindi", "type": "Cardiac Event", "severity": 5, "lat": 33.6010, "lng": 73.0510},
        {"time": "22:21", "area": "Gulshan, Karachi", "type": "Severe Bleeding", "severity": 4, "lat": 24.8770, "lng": 67.0412},
    ]

def _classify_emergency(query: str) -> dict:
    q = query.lower()
    CATEGORIES = [
        ("Cardiac Event", 5, ["dil", "heart", "cardiac", "chest", "behosh", "unconscious", "cpr", "pulse", "saans nahi", "dil ka dorah", "seene mein dard", "dharkan"]),
        ("Severe Bleeding", 4, ["bleed", "blood", "khoon", "zakhm", "cut", "wound", "gehra", "chot"]),
        ("Gas Leak", 4, ["gas", "smell", "boo", "cylinder", "sui gas", "dhuaan", "saans mein jalan", "leak", "explosion"]),
        ("Burn Injury", 3, ["burn", "jal", "aag", "fire", "hot water", "steam", "oil", "chemical", "tezaab"]),
        ("Drowning", 5, ["drown", "pani", "water", "doob", "river", "sea", "swimming"]),
        ("Choking", 5, ["choke", "choking", "saans nahi aa rahi", "dum ghut", "throat", "gala"]),
        ("Allergic Reaction", 3, ["allergic", "allergy", "rash", "swelling", "hives", "anaphylaxis", "reaction"]),
        ("Stroke", 5, ["stroke", "paralysis", "falaaj", "face droop", "slurred speech", "half body"]),
        ("Seizure", 4, ["seizure", "fit", "mirgi", "convuls", "shaking", "dant peesna"]),
        ("Road Accident", 4, ["accident", "crash", "road", "traffic", "hit", "vehicle", "gaari", "car", "truck"]),
        ("Diabetic Emergency", 4, ["diabetes", "sugar", "shakkar", "diabetic", "insulin", "hypo", "hyper"]),
    ]
    for name, severity, keywords in CATEGORIES:
        if any(k in q for k in keywords):
            return {"type": name, "severity": severity}
    return {"type": "General Emergency", "severity": 3}

def _extract_json_object(raw_value: str) -> dict:
    try:
        parsed = json.loads(raw_value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{.*\}", raw_value, flags=re.DOTALL)
    if not json_match:
        return {}
    try:
        parsed = json.loads(json_match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}

def _coerce_pipeline_payload(crew_output: dict | str) -> dict:
    if isinstance(crew_output, dict):
        return crew_output
    if not isinstance(crew_output, str):
        return {}

    parsed = _extract_json_object(crew_output)
    if parsed:
        return parsed

    type_match = re.search(r"(?:type|emergency)\s*[:=-]\s*([A-Za-z /-]+)", crew_output, flags=re.IGNORECASE)
    severity_match = re.search(r"severity\s*[:=-]\s*(\d)", crew_output, flags=re.IGNORECASE)
    payload: dict[str, str | int] = {}
    if type_match:
        payload["type"] = type_match.group(1).strip()
    if severity_match:
        payload["severity"] = int(severity_match.group(1))
    return payload

def _gif_key_for_emergency(emergency_type: str) -> str:
    normalized = (emergency_type or "").lower()
    if "cardiac" in normalized or "heart" in normalized or "cpr" in normalized:
        return "Cardiac Event"
    if "bleeding" in normalized or "blood" in normalized or "hemorrhage" in normalized:
        return "Severe Bleeding"
    if "gas" in normalized or "leak" in normalized:
        return "Gas Leak"
    return "Default"

def display_pipeline_results(crew_output: dict | str) -> dict:
    """Parse classifier output and return the visual state consumed by the UI."""
    payload = _coerce_pipeline_payload(crew_output)
    emergency_type = str(payload.get("type") or payload.get("emergency_type") or "Default")
    try:
        severity = int(payload.get("severity", 3))
    except (TypeError, ValueError):
        severity = 3

    gif_key = _gif_key_for_emergency(emergency_type)
    visual = EMERGENCY_GIF_MAP.get(gif_key, EMERGENCY_GIF_MAP["Default"])
    tone = "critical" if severity >= 4 else "warning" if severity == 3 else "stable"

    return {
        "classified_type": emergency_type,
        "gif_key": gif_key,
        "gif_url": visual["url"],
        "label": visual["label"],
        "alt": visual["alt"],
        "tone": tone,
        "severity": severity,
    }

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
        return {"name": "---", "phone": "---", "distance": "---"}
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
            f"CIVIL DEFENSE SITUATION REPORT\n"
            f"Cluster: {area_part.title()}\nActive linked incidents: {len(recent)}\n"
            "Assessment: Multi-incident pattern detected.\n"
            "Action: Escalate ambulance staging, volunteer triage, hospital pre-alert.\n\n"
            "شہری دفاعی صورتحال رپورٹ\n"
            f"علاقہ: {area_part.title()}\nمنسلک واقعات: {len(recent)}\n"
            "ہدایت: ایمبولینس، رضاکار، اور اسپتال رابطہ فوری تیز کریں۔"
        )
        return True, report
    return False, "No active mass-event clusters flagged in district."

# ─── MULTIMODAL AUDIO & RAG SERVICES ─────────────────────────────────────────
def transcribe_audio_if_possible(audio_path: str) -> str:
    api_key = _gemini_api_key()
    if not api_key:
        print("[Haalat] Gemini API key not found. Skipping transcription.")
        return "[Audio Report Saved]"
    
    try:
        client = genai.Client(api_key=api_key)
        audio_file = Path(audio_path)
        if audio_file.exists():
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    genai.types.Part.from_bytes(
                        data=audio_file.read_bytes(),
                        mime_type="audio/wav"
                    ),
                    "Transcribe the spoken audio and translate it to English. If the audio is already in English, just return the transcription. Provide ONLY the final English translation/transcription, with no extra text, notes, or labels."
                ]
            )
            return response.text.strip()
    except Exception as e:
        print(f"[Haalat] Error transcribing audio with Gemini: {e}")
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
        print(f"[Haalat] Error classifying emergency with Gemini: {e}")
    return {}

# ─── FASTAPI ROUTING ENDPOINTS ───────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def get_home():
    html_path = PROJECT_ROOT / "templates" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html template not found")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/logo.png")
def get_logo():
    logo_path = PROJECT_ROOT / "haalat_logo_1781643712746.png"
    if logo_path.exists():
        return FileResponse(logo_path)
    raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/instruction-assets/{asset_name}")
def get_instruction_asset(asset_name: str):
    svg = INSTRUCTION_VISUAL_SVGS.get(asset_name)
    if not svg:
        raise HTTPException(status_code=404, detail="Instruction asset not found")
    return Response(content=svg, media_type="image/svg+xml")

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
    
    # Process audio if uploaded
    if request.audio_path:
        transcription = transcribe_audio_if_possible(request.audio_path)
        if message_text and message_text != "[AUDIO REPORT TRANSMITTED]":
            message_text = f"{message_text} [Transcribed: {transcription}]"
        else:
            message_text = transcription

    # Format location string
    city_map = {"karachi": "Karachi", "islamabad": "Islamabad", "rawalpindi": "Rawalpindi"}
    city = city_map.get(request.region.lower(), "Karachi")
    location_str = f"{request.area}, {city}"

    # Use coordinates if sent by browser, otherwise match names
    if request.lat is not None and request.lng is not None:
        lat, lng = request.lat, request.lng
    else:
        try:
            from tools import _parse_location
            lat, lng = _parse_location(location_str)
        except Exception:
            lat, lng = REGION_CENTERS.get(request.region.lower(), (24.8665, 67.0235))

    # Triage and classification
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

    # Service & Volunteer matches
    resources = _get_resources_text(emergency_type, location_str)
    unit = _extract_resource(resources, "service")
    vol = _extract_resource(resources, "volunteer")

    # Log incident to City Memory
    _save_incident({
        "type": emergency_type,
        "severity": severity,
        "area": location_str,
        "lat": lat,
        "lng": lng,
        "user_message": message_text[:120],
    })

    # Check mass event
    is_mass_event, sitrep = _mass_event_check(location_str)
    instruction_visual = display_pipeline_results({
        "type": emergency_type,
        "severity": severity,
    })

    # Build agent simulation logs
    if has_llm:
        agent_log = [
            f"Language Router Agent: Scanned emergency transmission input. Detected language: '{detected_language}'.",
            f"Emergency Triage Paramedic: Classified incident as '{emergency_type}' (Severity: {severity}/5) grounded on RAG context.",
            f"Emergency Triage Paramedic: Reasoning details: {reasoning}",
            f"Field Asset Coordinator: Loaded local maps. Closest dispatch: {unit['name']} ({unit['distance']}).",
            f"Field Asset Coordinator: Alerted volunteer {vol['name']} ({vol['distance']} away, phone: {vol['phone']}).",
            f"Mass Event Intelligence Analyst: Event window scan complete. Mass event: {is_mass_event}.",
            f"City Emergency Intelligence Recorder: Successfully saved anonymized record to local Chroma & incident databases."
        ]
    else:
        agent_log = [
            "SYSTEM: Offline fallback mode activated (No valid GEMINI_API_KEY).",
            f"Language Router Agent: Routing request as local text payload.",
            f"Emergency Triage Paramedic: Matched keywords to static category rules. Event: '{emergency_type}' (Severity: {severity}/5).",
            f"Field Asset Coordinator: Matched mock Karachi/Islamabad databases. Mapped dispatch unit: {unit['name']}.",
            f"Field Asset Coordinator: Notified nearest skill-matched volunteer {vol['name']} via local push.",
            f"Mass Event Intelligence Analyst: Executing bounding-box area scan. Mass event: {is_mass_event}.",
            "City Emergency Intelligence Recorder: Written incident logs to incident_log.json."
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
        "instruction_visual": instruction_visual,
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

# ─── MAIN APP ENTRY ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ensure seeded incidents exist
    if len(_load_incidents()) < 2:
        for inc in _demo_incidents():
            _save_incident({
                "type": inc["type"], "severity": inc["severity"], "area": inc["area"],
                "lat": inc["lat"], "lng": inc["lng"], "user_message": "Demo seed",
            })

    print("[Haalat] Starting FastAPI World-Class Command Center on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
