import cv2
import os
from pathlib import Path
from typing import List, Tuple

def extract_frames(video_path: str, fps: int = 1, max_duration: int = 60) -> List[Tuple[float, str]]:
    """
    Extract frames from video every `fps` seconds.
    Returns list of (timestamp, frame_path).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Create temporary directory for frames
    temp_dir = Path("data/uploads/video/temp_frames")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Clear previous frames
    for f in temp_dir.glob("*.jpg"):
        try:
            os.remove(f)
        except:
            pass

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0

    # Limit duration for performance
    process_duration = min(duration, max_duration)
    
    print(f"Video duration: {duration:.2f}s")
    print(f"Processing up to: {process_duration:.2f}s at {fps} FPS")
    
    frames_info = []
    current_sec = 0.0
    processed_count = 0
    
    # Process exactly second by second
    while current_sec < process_duration:
        frame_idx = int(current_sec * video_fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            break
            
        frame_name = f"frame_{int(current_sec)}.jpg"
        frame_path = str(temp_dir / frame_name)
        
        # Resize frame to speed up analysis (max 640px height)
        h, w = frame.shape[:2]
        if h > 640:
            scale = 640 / h
            frame = cv2.resize(frame, (int(w * scale), 640))
            
        cv2.imwrite(frame_path, frame)
        frames_info.append((current_sec, frame_path))
        
        current_sec += 1.0/fps
        processed_count += 1
        
    cap.release()
    print(f"Frames processed: {processed_count}")
    return frames_info
