from flask import Blueprint, request, jsonify
from services.chat_service import query_chat
from utils.logger import setup_logger

logger = setup_logger('chat_routes')
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/<mode>', methods=['POST'])
def chat(mode):
    """
    Unified chat endpoint for image, audio, and video.
    """
    if mode not in ['image', 'audio', 'video']:
        return jsonify({"status": "error", "message": "Invalid chat mode"}), 400

    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')

    if not session_id or not question:
        return jsonify({"status": "error", "message": "Session ID and Question are required"}), 400

    logger.info(f"Chat request [{mode}]: {question[:50]}...")
    
    answer = query_chat(session_id, question, mode=mode)
    
    return jsonify({
        "status": "success",
        "answer": answer
    })
