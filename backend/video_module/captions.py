from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from typing import List, Dict
from utils.groq_utils import get_config

# Global cache for model
_blip_cache = None

def get_blip_model():
    global _blip_cache
    if _blip_cache is None:
        config = get_config()
        model_name = config["caption_model"]
        print(f"Loading BLIP model: {model_name}...")
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name)
        _blip_cache = {"processor": processor, "model": model}
    return _blip_cache

def generate_frame_captions(frames_info: List[Dict]) -> List[Dict]:
    """
    Generate captions for extracted frames.
    """
    model_data = get_blip_model()
    processor = model_data["processor"]
    model = model_data["model"]
    
    captions = []
    
    # Analyze more frames for captioning for forensic coverage (max 12 frames)
    # Using 12 ensures we catch at least 2-3 frames per action phase in a 30s video
    step = max(1, len(frames_info) // 12)
    sampled_frames = frames_info[::step][:12]
    
    for timestamp, frame_path in sampled_frames:
        image = Image.open(frame_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            output = model.generate(**inputs)
            
        caption = processor.decode(output[0], skip_special_tokens=True)
        captions.append({
            "timestamp": timestamp,
            "caption": caption
        })
        
    return captions

def summarize_captions(captions: List[Dict], groq_client, config) -> str:
    """
    Combine frame captions using Groq LLM.
    """
    if not captions:
        return "No visual evidence found."
        
    combined_text = "\n".join([f"Time {c['timestamp']}s: {c['caption']}" for c in captions])
    
    prompt = f"""
    Summarize the following visual sequence from a crime scene video into 1-2 professional sentences.
    Focus on actions, persons, and key events.

    Details:
    {combined_text}

    Format: raw string only, no prefixes like 'Summary is:'.
    """
    
    try:
        completion = groq_client.chat.completions.create(
            model=config["groq_model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Caption summarization failed: {e}")
        return captions[0]["caption"] if captions else "Analysis unavailable."
