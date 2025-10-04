from typing import List, Dict, Generator, Any, Optional, Tuple
import requests
import json
import os
import base64
import mimetypes
import PyPDF2
import time
from datetime import date

"""
Standalone Medical Assistant module (no Django)
- Uses Google Gemini 1.5 Flash for chat and vision (PDF/images)
- Keeps patient-context building, document extraction, and streaming
- System Prompt is defined in `DEFAULT_SYSTEM_PROMPT` and injected by `format_chat_messages()`

⚠️ Safety note: This module uses a responsible healthcare assistant prompt.
   It does NOT instruct the model to ignore safety or provide definitive medical diagnoses.
"""

# =====================
# Gemini API configuration
# =====================
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCi4LebK3sHoI-qL58OEdkcsyEndFWFYo4")
REQUEST_TIMEOUT = 15
DOCUMENT_TIMEOUT = 60

# Models
TEXT_MODEL = "gemini-1.5-flash"
VISION_MODEL = "gemini-1.5-flash"  # same model handles multimodal

# =====================
# System Prompt (location here)
# =====================
DEFAULT_SYSTEM_PROMPT = (
    "You are Dr. AI, a careful and knowledgeable medical assistant. "
    "Use the provided patient records and documents to offer educational, evidence-informed guidance. "
    "Be clear, structured, and empathetic. You are not a replacement for a clinician. "
    "When advice might affect safety, recommend consulting a licensed professional or emergency care as appropriate. "
    "Cite specific findings from the patient context when relevant."
)

# =====================
# Patient Context
# =====================
def get_patient_context(patient: Dict[str, Any]) -> str:
    """Generate context string from a simple patient dictionary"""
    context = (
        f"PATIENT INFORMATION:\n"
        f"Name: {patient.get('name','Unknown')}\n"
        f"ID: {patient.get('id','')}\n"
        f"Gender: {patient.get('gender','Unknown')}\n"
        f"Blood Group: {patient.get('blood_group','Not recorded')}\n"
        f"Age: {patient.get('age','Not recorded')}\n"
        f"Contact: {patient.get('phone','')}\n"
        f"Address: {patient.get('address','Not recorded')}\n"
    )

    if patient.get("visits"):
        context += "\n\nMEDICAL HISTORY:\n"
        for i, visit in enumerate(patient["visits"]):
            context += f"\n--- VISIT #{i+1}: {visit.get('date','')} ---"
            context += f"\nDoctor: {visit.get('doctor','')}"
            context += f"\nDiagnosis: {visit.get('diagnosis','')}"
            context += f"\nTreatment: {visit.get('treatment','')}"
            if visit.get('notes'):
                context += f"\nNotes: {visit['notes']}"

            if visit.get('medications'):
                context += "\nMedications:"
                for med in visit['medications']:
                    context += f"\n- {med.get('name')} ({med.get('dosage','')}, {med.get('frequency','')})"

            if visit.get('tests'):
                context += "\nTests:"
                for test in visit['tests']:
                    context += f"\n- {test.get('name')} : {test.get('result','Pending')}"

    return context

# =====================
# Document Extraction
# =====================

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, str]:
    """Extract text from a PDF using PyPDF2. If no text, caller may fall back to vision."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text += f"----- Page {i+1} -----{page_text}"
        if not text.strip() or len(text.strip()) < 50:
            return (
                "PDF text extraction yielded insufficient text. The PDF may be scanned or image-based.",
                "PyPDF2_insufficient",
            )
        return text, "PyPDF2"
    except Exception as e:
        return f"Error extracting text from PDF: {e}", "PyPDF2_failed"


def _read_file_base64(path: str) -> Tuple[Optional[str], Optional[str]]:
    if not path or not os.path.exists(path):
        return None, None
    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return data, (mime or "application/octet-stream")


def extract_text_with_vision(file_path: str, hint_text: str = "") -> Tuple[str, str]:
    """Use Gemini multimodal to transcribe/extract text from PDFs/images.
    Sends the file as inline_data to the model with a text instruction.
    """
    try:
        data_b64, mime = _read_file_base64(file_path)
        if not data_b64:
            return f"File not found: {file_path}", "vision_error"

        url = f"{GEMINI_API_ENDPOINT}/{VISION_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": hint_text or (
                            "Extract and transcribe all text content. "
                            "Preserve structure where helpful. Pay attention to medical terminology.")},
                        {"inline_data": {"mime_type": mime, "data": data_b64}},
                    ],
                }
            ]
        }
        resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=DOCUMENT_TIMEOUT)
        if resp.status_code != 200:
            return f"Vision API error {resp.status_code}: {resp.text[:200]}", "vision_failed"
        data = resp.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return text or "", "gemini_vision"
    except Exception as e:
        return f"Vision error: {e}", "vision_exception"


def extract_text_from_file(file_path: str) -> Tuple[str, str]:
    """Route file extraction: PDFs via PyPDF2, text files direct, images/others via vision.
    Falls back to vision for PDFs if PyPDF2 insufficient.
    """
    if not file_path or not os.path.exists(file_path):
        return f"File not found at {file_path}", "none"

    mime, _ = mimetypes.guess_type(file_path)

    # PDF
    if (mime == 'application/pdf') or str(file_path).lower().endswith('.pdf'):
        text, method = extract_text_from_pdf(file_path)
        if method.endswith('_failed') or method.endswith('_insufficient'):
            fallback_text, fallback_method = extract_text_with_vision(
                file_path,
                hint_text=(
                    "This is a medical PDF. Extract and transcribe the text. "
                    "Capture tables and values faithfully if possible."),
            )
            return fallback_text, f"{method} -> {fallback_method}"
        return text, method

    # Plain text
    if mime and mime.startswith('text/'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), "text_reader"
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read(), "text_reader"
        except Exception as e:
            return f"Error reading text file: {e}", "none"

    # Images / others -> vision
    text, method = extract_text_with_vision(file_path)
    return text, method

# =====================
# Chat & Streaming
# =====================

def query_gemini(messages: List[Dict[str, str]], model: str = TEXT_MODEL) -> str:
    """Non-streaming text/multimodal chat."""
    try:
        url = f"{GEMINI_API_ENDPOINT}/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages
            ]
        }
        resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=REQUEST_TIMEOUT)
        data = resp.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Unexpected response: {data}"
    except Exception as e:
        return f"Error contacting Gemini API: {e}"


def stream_gemini(messages: List[Dict[str, str]], model: str = TEXT_MODEL) -> Generator[str, None, None]:
    """Server-sent-events streaming."""
    url = f"{GEMINI_API_ENDPOINT}/{model}:streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages
        ]
    }
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                if line.startswith(b"data: "):
                    chunk = line[6:]
                    if chunk == b"[DONE]":
                        break
                    try:
                        obj = json.loads(chunk)
                        parts = obj.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        for p in parts:
                            if "text" in p:
                                yield p["text"]
                    except Exception:
                        continue
    except Exception as e:
        yield f"[stream error] {e}"

# =====================
# Message Formatting
# =====================

def format_chat_messages(patient: Dict[str, Any], user_message: str, system_prompt: Optional[str] = None) -> List[Dict]:
    """Prepare messages for chat API including the system prompt and patient context.

    The System Prompt lives here: `system_prompt or DEFAULT_SYSTEM_PROMPT`.
    """
    sys_prompt = (system_prompt or DEFAULT_SYSTEM_PROMPT) + "

Patient context:
" + get_patient_context(patient)
    return [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_message},
    ]

# =====================
# File Analysis Helpers (no DB; pure file paths)
# =====================

def analyze_document_file(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a document file and return structured info.
    file_info: {"path": str, "description": str, "visit_date": str, "uploaded_at": str}
    """
    path = file_info.get("path")
    start = time.time()
    text, method = extract_text_from_file(path)
    dur = time.time() - start

    size = None
    try:
        size = os.path.getsize(path) if path and os.path.exists(path) else None
    except Exception:
        size = None

    mime, _ = mimetypes.guess_type(path or "")

    return {
        "file_name": os.path.basename(path or ""),
        "description": file_info.get("description") or "No description provided",
        "path": path,
        "content": text,
        "upload_date": file_info.get("uploaded_at") or "Unknown",
        "file_type": mime or "Unknown",
        "model_used": method,
        "processing_time": f"{dur:.2f} seconds",
        "size": size,
        "visit_date": file_info.get("visit_date") or "Unknown",
    }


def get_file_contents(files: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Process a list of {path, ...} dicts and extract text content."""
    out: Dict[str, Dict[str, Any]] = {}
    for f in files or []:
        info = analyze_document_file(f)
        out[info["file_name"]] = info
    return out

# =====================
# Age helper
# =====================

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# =====================
# Example usage
# =====================
if __name__ == "__main__":
    # Example patient
    patient = {
        "id": 1,
        "name": "John Doe",
        "gender": "Male",
        "age": 45,
        "phone": "123456789",
        "address": "123 Main St",
        "blood_group": "O+",
        "visits": [
            {
                "date": "2025-08-20",
                "doctor": "Dr. Smith",
                "diagnosis": "Hypertension",
                "treatment": "Lifestyle changes and medication",
                "notes": "Patient reports occasional headaches",
                "medications": [
                    {"name": "Amlodipine", "dosage": "5mg", "frequency": "daily", "reason": "BP control"}
                ],
                "tests": [
                    {"name": "Blood Pressure", "result": "150/95"}
                ],
                "files": [
                    {"path": "./example.pdf", "description": "Lab report", "uploaded_at": "2025-08-21"}
                ]
            }
        ],
    }

    # Prepare messages (System Prompt lives in format_chat_messages)
    messages = format_chat_messages(patient, "What should John do to manage his BP?")

    # Call non-streaming chat
    reply = query_gemini(messages)
    print("AI Reply:", reply)

    # Streamed chat (generator)
    print("Streaming Reply:")
    for chunk in stream_gemini(messages):
        print(chunk, end="", flush=True)

    # Extract a file (auto routes PDF/text/image)
    print("Document analysis example:")
    files = [{"path": "./example.pdf", "description": "CBC report", "uploaded_at": "2025-08-21"}]
    analyzed = get_file_contents(files)
    for k, v in analyzed.items():
        print(f"--- {k} ---")
        print("Type:", v["file_type"]) 
        print("Model:", v["model_used"]) 
        print("Excerpt:", (v["content"] or "").strip()[:400])
