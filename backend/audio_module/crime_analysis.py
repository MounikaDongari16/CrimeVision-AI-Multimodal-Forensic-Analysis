import json
from utils.groq_utils import get_groq_client, get_config

def generate_summary(text):
    """
    Generate a one-line scenario description using Groq
    """
    client = get_groq_client()
    config = get_config()
    
    prompt = f"Summarize this crime scene witness statement in exactly one clear, professional sentence.\n\nText: {text}"
    
    try:
        completion = client.chat.completions.create(
            model=config["groq_model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary failed: {str(e)}"

def extract_crime_intelligence(text):
    """
    Extract structured JSON intelligence from witness statement using Groq
    """
    client = get_groq_client()
    config = get_config()
    
    prompt = f"""
    Extract crime scene intelligence from the following witness statement. 
    Return the result as a raw JSON object with these EXACT keys:
    - location: (road / hall / bedroom / bathroom / store)
    - event: (robbery / murder / fight / theft / accident)
    - suspect_description: description of people involved
    - who_what_where_when: one sentence summary
    - timeline_description: brief sequence of events
    - actions_detected: list of verbs
    - objects_detected: list of items mentioned
    - scene_description: visual/atmospheric summary

    Statement: {text}
    """
    
    try:
        completion = client.chat.completions.create(
            model=config["groq_model"],
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        return {
            "error": str(e),
            "location": "unknown",
            "event": "unknown",
            "suspect_description": "unknown",
            "who_what_where_when": "unknown",
            "timeline_description": "unknown",
            "actions_detected": [],
            "objects_detected": [],
            "scene_description": "unknown"
        }
