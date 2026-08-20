import json
from utils.groq_utils import get_groq_client, get_config

def classify_crime(video_description, objects, groq_client, config):
    """
    Classify the crime type and extract structured metrics based on findings.
    """
    object_labels = [o['label'] for o in objects]
    
    prompt = f"""
    You are a professional forensic analyst. Analyze the following AI-extracted data from a crime scene video.
    
    Video Evidence (Captions): {video_description}
    Technical Evidence (Objects): {', '.join(object_labels)}
    
    CRITICAL INSTRUCTION: Be decisive. If the evidence suggests a suspicious gathering, shelf-item removal, or physical altercation, elevate the confidence accordingly. Avoid "unknown" unless there is absolute zero activity.
    
    Return a JSON object with strictly these keys:
    - crime_label: (theft / robbery / assault / accident / vandalism / fight / murder / suspicious gathering / normal activity / unknown)
    - crime_confidence: float (0.0 to 1.0) - Use 0.8+ for clear crimes, 0.5-0.7 for suspicious.
    - reason: short forensic explanation
    - forensic_reasoning: detailed explanation of WHY this label was chosen based on the evidence
    - objects_detected: list of unique primary objects from the video
    - people_count: integer (total high-confidence unique people identified)
    - location: short description of location
    - primary_action: the most significant action identified
    """
    
    try:
        completion = groq_client.chat.completions.create(
            model=config["groq_model"],
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        res = json.loads(completion.choices[0].message.content)
        return {
            "label": res.get("crime_label", "unknown"),
            "confidence": res.get("crime_confidence", 0),
            "reason": res.get("reason", "N/A"),
            "extracted_metrics": {
                "objects": res.get("objects_detected", []),
                "people_count": res.get("people_count", 0),
                "location": res.get("location", "unknown"),
                "action": res.get("action", "none")
            }
        }
    except Exception as e:
        print(f"Classification failed: {e}")
        return {
            "label": "unknown", 
            "confidence": 0, 
            "reason": "AI error",
            "extracted_metrics": {
                "objects": object_labels[:5],
                "people_count": 1 if 'person' in object_labels else 0,
                "location": "unknown",
                "action": "unknown"
            }
        }
    except Exception as e:
        print(f"Classification failed: {e}")
        return {"label": "unknown", "confidence": 0, "reason": "AI error"}
