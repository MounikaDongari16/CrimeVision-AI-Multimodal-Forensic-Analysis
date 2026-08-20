import json
from typing import List, Dict

def build_timeline(captions: List[Dict], detections: List[Dict], groq_client, config, duration: float) -> Dict:
    """
    Build structured timeline ensuring every second is covered.
    """
    
    # 1. Create a dictionary for quick lookup by second
    caption_map = {int(c['timestamp']): c['caption'] for c in captions}
    detection_map = {int(d['timestamp']): [det['label'] for det in d['detections']] for d in detections}
    
    timeline_raw = []
    duration_rounded = int(duration)
    
    for s in range(duration_rounded + 1):
        caption = caption_map.get(s)
        objs = detection_map.get(s, [])
        
        if not caption and not objs:
            timeline_raw.append({
                "seconds": s,
                "event": "No significant activity"
            })
        else:
            # Prepare contextual data for LLM refinement
            event_ctx = f"Visual: {caption or 'N/A'}. Objects: {', '.join(objs) if objs else 'N/A'}"
            timeline_raw.append({
                "seconds": s,
                "context": event_ctx
            })

    # 2. Use LLM to refine only the active moments
    active_moments = [item for item in timeline_raw if "context" in item]
    
    refined_map = {}
    if active_moments:
        prompt = f"""
        You are a forensic AI. Convert these raw video detection observations into concise, natural language event descriptions.
        
        Observations:
        {json.dumps(active_moments)}
        
        Rule: Return JSON with a "refinements" list of strings, one description per observation in order.
        No timestamps in description.
        """
        try:
            completion = groq_client.chat.completions.create(
                model=config["groq_model"],
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            res = json.loads(completion.choices[0].message.content)
            refinements = res.get("refinements", [])
            for i, item in enumerate(active_moments):
                if i < len(refinements):
                    refined_map[item['seconds']] = refinements[i]
        except Exception as e:
            print(f"LLM Timeline refinement failed: {e}")

    # 3. Assemble Final Gap-Free Timeline
    final_timeline = []
    for s in range(duration_rounded + 1):
        m = s // 60
        sec = s % 60
        time_str = f"{m:02d}:{sec:02d}"
        
        description = refined_map.get(s) or caption_map.get(s) or "No significant activity"
        
        final_timeline.append({
            "time": time_str,
            "event": description
        })

    print(f"Timeline entries: {len(final_timeline)}")
    return {
        "timeline": final_timeline,
        "conflicts": []
    }
