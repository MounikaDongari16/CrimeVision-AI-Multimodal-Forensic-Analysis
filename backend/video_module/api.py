from flask import Blueprint, request, jsonify
import os
import time
from pathlib import Path
from werkzeug.utils import secure_filename

from .processor import extract_frames
from .detector import detect_objects_in_frames, aggregate_objects
from .captions import generate_frame_captions, summarize_captions
from .classifier import classify_crime
from .timeline import build_timeline
from utils.groq_utils import get_groq_client, get_config

video_analysis_bp = Blueprint('video_analysis', __name__, url_prefix='/api/analyze-video')

UPLOAD_FOLDER = Path("data/uploads/video")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@video_analysis_bp.route('', methods=['POST'])
def analyze_video():
    """
    Main endpoint for video analysis.
    """
    try:
        print("Video received", flush=True)
        
        if 'video' not in request.files and 'file' not in request.files:
            return jsonify({"status": "error", "message": "No video file provided"}), 400
        
        file = request.files.get('video') or request.files.get('file')
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
            
        # 1. Save Video
        timestamp = int(time.time())
        filename = secure_filename(file.filename)
        save_path = UPLOAD_FOLDER / f"video_{timestamp}_{filename}"
        file.save(str(save_path))
        print(f"Video saved to: {save_path}")

        # 1.5 Get Duration
        import cv2
        _cap = cv2.VideoCapture(str(save_path))
        _fps = _cap.get(cv2.CAP_PROP_FPS)
        _total = _cap.get(cv2.CAP_PROP_FRAME_COUNT)
        video_duration = _total / _fps if _fps > 0 else 0
        _cap.release()

        # 2. Extract Frames (1 FPS, max 60s)
        print("Extracting frames...")
        frames_info = extract_frames(str(save_path))
        print(f"Extracted {len(frames_info)} frames.")

        if not frames_info:
            return jsonify({"status": "error", "message": "Could not extract frames from video"}), 500

        # 3. Model Logic (Parallel/Sequential)
        groq_client = get_groq_client()
        config = get_config()

        # Object Detection
        print("Running object detection...")
        detection_results = detect_objects_in_frames(frames_info)
        aggregated_objects = aggregate_objects(detection_results)
        print(f"Detected {len(aggregated_objects)} unique object categories.")

        # Captioning
        print("Generating frame captions...")
        frame_captions = generate_frame_captions(frames_info)
        video_description = summarize_captions(frame_captions, groq_client, config)
        print(f"Description: {video_description}")

        # Classification
        print("Classifying crime situation...")
        crime_data = classify_crime(video_description, aggregated_objects, groq_client, config)

        # Timeline & Conflicts
        print("Building event timeline...")
        timeline_data = build_timeline(frame_captions, detection_results, groq_client, config, video_duration)

        # 5. Store in Session for Chat
        from utils.session_store import session_store
        session_data = {
            "video_description": video_description,
            "objects_detected": aggregated_objects,
            "crime_type": crime_data,
            "timeline": timeline_data.get("timeline", []),
            "timeline_conflicts": timeline_data.get("conflicts", [])
        }
        session_id = session_store.create_session(session_data)

        # Cleanup video (optional, keep for demo)
        # os.remove(str(save_path))

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "video_duration": video_duration,
            "video_description": video_description,
            "objects_detected": aggregated_objects,
            "crime_type": crime_data,
            "timeline": timeline_data.get("timeline", []),
            "timeline_conflicts": timeline_data.get("conflicts", []),
            "video_url": f"/api/results/video/{save_path.name}" # Placeholder for serving
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Video Analysis Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
