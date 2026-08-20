import json
import re
import math
from utils.groq_utils import get_groq_client, get_config
from utils.session_store import session_store

def parse_time_from_question(question):
    """
    Detect time references using regex:
    - 0.5 sec, 10s, 1 second
    - 00:12, 01:30
    """
    # Pattern 1: seconds (e.g., 0.5s, 10 sec, 5 seconds)
    sec_match = re.search(r'(\d+(\.\d+)?)\s*(sec|second|seconds|s)\b', question, re.IGNORECASE)
    if sec_match:
        return math.floor(float(sec_match.group(1)))

    # Pattern 2: MM:SS (e.g., 00:12, 01:05)
    ms_match = re.search(r'(\d{2}):(\d{2})', question)
    if ms_match:
        minutes = int(ms_match.group(1))
        seconds = int(ms_match.group(2))
        return minutes * 60 + seconds
    
    return None

def get_event_at_time(timeline, second):
    """
    Direct lookup in the second-by-second timeline array.
    """
    if second < 0 or second >= len(timeline):
        return "Time outside video duration"
    
    entry = timeline[second]
    # Handle both list of dicts and raw strings if needed
    if isinstance(entry, dict):
        return f"At {entry.get('time', 'unknown')}, {entry.get('event', 'no activity recorded')}"
    return entry

def query_chat(session_id, question, mode="image"):
    """
    Queries Groq LLM using analysis results as context.
    For Video: Prioritizes direct timeline lookup for time-based queries.
    """
    context = session_store.get_session(session_id)
    if not context:
        return "Session expired or not found. Please re-analyze the file."

    # --- VIDEO MODE: TIME-BASED QUERY DETECTION ---
    if mode == "video":
        detected_sec = parse_time_from_question(question)
        if detected_sec is not None:
            timeline = context.get("timeline", [])
            event = get_event_at_time(timeline, detected_sec)
            
            # Mandatory Debug Logs
            print(f"User question: {question}")
            print(f"Detected second: {detected_sec}")
            print(f"Timeline length: {len(timeline)}")
            print(f"Event returned: {event}")
            
            return event
    # -----------------------------------------------

    client = get_groq_client()
    config = get_config()

    # Model for chat - using a standard Groq model
    model = config.get("groq_model", "llama-3.3-70b-versatile")

    prompt = f"""
    You are a professional crime scene analysis assistant.
    You must answer the user's question based ONLY on the provided structured analysis results.
    
    GUIDELINES:
    1. Answer concisely and professionally.
    2. If the answer is not in the data, say: "Informantion not found in the analyzed evidence."
    3. Do NOT hallucinate objects, times, or people that are not listed.
    4. Provide specific details like counts, timestamps, and labels when available.

    CONTEXT ({mode.upper()} Analysis Results):
    {json.dumps(context, indent=2)}

    USER QUESTION:
    "{question}"

    AI RESPONSE:
    """

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Chat query failed: {e}")
        return f"Error connecting to AI: {str(e)}"
