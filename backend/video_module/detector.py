import torch
from PIL import Image
from typing import List, Dict
import os
from utils.model_loader import load_rt_detr_model

def detect_objects_in_frames(frames_info: List[Dict]) -> List[Dict]:
    """
    Run high-accuracy object detection on extracted frames using RT-DETR.
    """
    model_data = load_rt_detr_model()
    if not model_data:
        print("RT-DETR model loading failed for video analysis.")
        return []
        
    processor = model_data["processor"]
    model = model_data["model"]
    device = model_data["device"]
    
    results = []
    
    for timestamp, frame_path in frames_info:
        image = Image.open(frame_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            
        target_sizes = torch.tensor([image.size[::-1]]).to(device)
        processed_results = processor.post_process_object_detection(outputs, threshold=0.3, target_sizes=target_sizes)[0]
        
        frame_detections = []
        for score, label, box in zip(processed_results["scores"], processed_results["labels"], processed_results["boxes"]):
            label_idx = label.item()
            raw_label = model.config.id2label[label_idx]
            # Map person to Human for consistency
            label_name = "Human" if raw_label.lower() == 'person' else raw_label
            
            frame_detections.append({
                "label": label_name,
                "confidence": round(score.item(), 2)
            })
            
        results.append({
            "timestamp": timestamp,
            "detections": frame_detections
        })
        
    return results

def aggregate_objects(detection_results: List[Dict]) -> List[Dict]:
    """
    Summarize unique objects found across all frames.
    """
    counts = {}
    for entry in detection_results:
        # For each frame, we take unique objects to avoid overcounting slightly
        unique_labels = set(d["label"] for d in entry["detections"])
        for label in unique_labels:
            counts[label] = counts.get(label, 0) + 1
            
    # We'll return the list of objects that appeared in any frame
    return [{"label": label, "occurrence_count": count} for label, count in counts.items()]
