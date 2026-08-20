import json
from utils.groq_utils import get_groq_client, get_config

def format_time(seconds):
    """
    Convert seconds to mm:ss format
    """
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def generate_timeline(segments):
    """
    Generate a structured crime event timeline using Groq LLM
    """
    if not segments:
        print("No segments provided for timeline.")
        return []

    client = get_groq_client()
    config = get_config()
    
    # Debug logging
    print("Whisper segments:", segments[:3], "...") # Show sample
    
    # 1. Prepare segments for the LLM
    segments_data = []
    for s in segments:
        segments_data.append({
            "start": round(s["start"], 2),
            "text": s["text"].strip()
        })
    
    # 2. Construct Prompt
    prompt = f"""
    You are a crime investigation AI.
    From the following transcript segments with timestamps:

    {json.dumps(segments_data[:50])} 

    Extract key crime-related events (e.g. suspect enters/exits, arguments, attacks, weapon usage, falling, alarm, suspicious noises).

    Return ONLY a raw JSON array of objects:
    [
      {{ "time_sec": 4.2, "event": "description" }}
    ]

    Rules:
    - Use the exact 'start' value as 'time_sec'
    - Do NOT invent time
    - Return strictly JSON array
    """
    
    try:
        completion = client.chat.completions.create(
            model=config["groq_model"],
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        raw_content = completion.choices[0].message.content
        print("LLM timeline raw:", raw_content)
        
        res_data = json.loads(raw_content)
        
        # Handle cases where LLM might wrap list in a dict
        timeline_list = []
        if isinstance(res_data, list):
            timeline_list = res_data
        elif isinstance(res_data, dict):
            for val in res_data.values():
                if isinstance(val, list):
                    timeline_list = val
                    break
        
        # 3. Format and clean timeline
        final_timeline = []
        for item in timeline_list:
            time_sec = item.get("time_sec", 0)
            final_timeline.append({
                "time": format_time(float(time_sec)),
                "event": item.get("event", "Unknown event")
            })
            
        print("Formatted timeline:", final_timeline)
        return final_timeline
        
    except Exception as e:
        print(f"Timeline generation failed: {e}")
        # Fallback to segments
        fallback = []
        for s in segments[:10]:
            fallback.append({
                "time": format_time(s["start"]),
                "event": s["text"].strip()
            })
        return fallback
