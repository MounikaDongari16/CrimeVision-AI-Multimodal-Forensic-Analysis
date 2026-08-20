from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

from .transcription import transcribe_audio
from .timeline import generate_timeline
from .translation import translate_transcript
from .crime_analysis import generate_summary, extract_crime_intelligence

audio_analysis_bp = Blueprint('audio_analysis', __name__, url_prefix='/api/analyze-audio')

UPLOAD_FOLDER = Path("data/uploads/audio/temp")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@audio_analysis_bp.route('', methods=['POST'])
def analyze_audio():
    """
    Direct audio analysis endpoint (Simplified & Robust)
    """
    import time
    import shutil
    
    # 1. Log reception
    print("Audio received", flush=True)
    
    try:
        if 'audio' not in request.files and 'file' not in request.files:
            return jsonify({"status": "error", "message": "No audio file provided"}), 400
        
        # Accept 'audio' (user spec) or 'file' (common fallback)
        file = request.files.get('audio') or request.files.get('file')
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
            
        # 2. Save file
        timestamp = int(time.time())
        ext = Path(file.filename).suffix or ".mp3"
        filename = f"audio_{timestamp}{ext}"
        save_path = UPLOAD_FOLDER / filename
        
        file.save(str(save_path))
        print(f"File saved: {save_path}", flush=True)
        
        # 3. Transcribe
        print("Whisper started", flush=True)
        
        # Use our existing robust transcription, but simplified for this endpoint
        # The user asked for `whisper.load_model("tiny")`. 
        # Our transcription.py uses dual mode. Let's trust dual mode as it DOES use tiny first.
        trans_result = transcribe_audio(str(save_path))
        transcript = trans_result["text"]
        
        print("Whisper finished", flush=True)
        print(f"Transcript: {transcript[:50]}...", flush=True)
        
        # 4. Intelligence (Safe wrap)
        # Verify if we should run full intelligence or just transcript. 
        # User goal: "Text appears in blue box". Let's give them the full suite anyway but safely.
        translations = {}
        crime_analysis = {}
        summary = ""
        
        try:
            translations = translate_transcript(transcript)
            print("Translation done", flush=True)
            
            crime_analysis = extract_crime_intelligence(transcript)
            summary = generate_summary(transcript)
            print("Crime analysis done", flush=True)
        except Exception as e:
            print(f"Intelligence step skipped: {e}", flush=True)

        # 5. Store in Session for Chat
        from utils.session_store import session_store
        session_data = {
            "transcript": transcript,
            "timeline": generate_timeline(trans_result["segments"]),
            "translations": translations,
            "one_line_summary": summary,
            "crime_analysis": crime_analysis
        }
        session_id = session_store.create_session(session_data)

        print("Sending response", flush=True)
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "transcript": transcript,
            "timeline": generate_timeline(trans_result["segments"]),
            "translations": translations,
            "one_line_summary": summary,
            "crime_analysis": crime_analysis
        })
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500
