"""
Upload Routes - Handle file uploads
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import uuid
from utils.file_handler import save_uploaded_file, get_file_info
from utils.logger import setup_logger

logger = setup_logger('upload_routes')

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

@upload_bp.route('/file', methods=['POST'])
def upload_file():
    """
    Upload a single file (image, video, audio, or report)
    
    Request:
        - file: File to upload
        - case_id: Optional case ID (generated if not provided)
    
    Response:
        - success: Boolean
        - message: Status message
        - case_id: Case identifier
        - file_info: File information
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Get or generate case ID
        case_id = request.form.get('case_id', str(uuid.uuid4()))
        
        # Save file
        success, message, file_path = save_uploaded_file(file, case_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Get file info
        file_info = get_file_info(file_path)
        
        # Automatic object detection for images
        detections = []
        if file_info['type'] == 'image':
            from services.vision_service import vision_service
            logger.info(f"Triggering auto-detection for uploaded image: {file_path}")
            detection_results = vision_service.detect_objects(file_path)
            detections = detection_results.get('detections', [])
        
        logger.info(f"File uploaded successfully: {file_path}")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'case_id': case_id,
            'file_info': file_info,
            'detections': detections
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error uploading file: {str(e)}'
        }), 500

@upload_bp.route('/batch', methods=['POST'])
def upload_batch():
    """
    Upload multiple files at once
    
    Request:
        - files: Multiple files
        - case_id: Optional case ID
    
    Response:
        - success: Boolean
        - message: Status message
        - case_id: Case identifier
        - uploaded_files: List of uploaded file info
    """
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({
                'success': False,
                'message': 'No files selected'
            }), 400
        
        # Get or generate case ID
        case_id = request.form.get('case_id', str(uuid.uuid4()))
        
        # Upload all files
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file.filename == '':
                continue
            
            success, message, file_path = save_uploaded_file(file, case_id)
            
            if success:
                file_info = get_file_info(file_path)
                
                # Auto-detect objects if it's an image
                detections = []
                if file_info['type'] == 'image':
                    from services.vision_service import vision_service
                    logger.info(f"Triggering auto-detection for batch uploaded image: {file_path}")
                    detection_results = vision_service.detect_objects(file_path)
                    detections = detection_results.get('detections', [])
                
                file_info['detections'] = detections
                uploaded_files.append(file_info)
            else:
                failed_files.append({
                    'filename': file.filename,
                    'error': message
                })
        
        logger.info(f"Batch upload: {len(uploaded_files)} succeeded, {len(failed_files)} failed")
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {len(uploaded_files)} files',
            'case_id': case_id,
            'uploaded_files': uploaded_files,
            'failed_files': failed_files
        }), 200
    
    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error in batch upload: {str(e)}'
        }), 500

@upload_bp.route('/status/<case_id>', methods=['GET'])
def get_upload_status(case_id):
    """
    Get upload status for a case
    
    Response:
        - case_id: Case identifier
        - files: List of uploaded files
    """
    try:
        from config import IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, REPORTS_DIR
        from pathlib import Path
        
        files = []
        
        # Check all upload directories
        for directory in [IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, REPORTS_DIR]:
            case_dir = directory / case_id
            if case_dir.exists():
                for file_path in case_dir.iterdir():
                    if file_path.is_file():
                        files.append(get_file_info(str(file_path)))
        
        return jsonify({
            'case_id': case_id,
            'total_files': len(files),
            'files': files
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting upload status: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting upload status: {str(e)}'
        }), 500
