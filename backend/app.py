"""
Main Flask Application for Crime Scene Reconstruction System
"""
import os
# Deep Environment Fix - Must be set BEFORE any other imports to prevent protobuf/tensorflow conflicts
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
os.environ['USE_TF'] = 'NO'
os.environ['USE_TORCH'] = 'YES'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, jsonify
from flask_cors import CORS
from config import API_CONFIG
from routes import upload_bp, processing_bp, results_bp
from audio_module.api import audio_analysis_bp
from video_module.api import video_analysis_bp
from routes.chat_routes import chat_bp
from utils.logger import setup_logger, app_logger
from utils.model_loader import preload_models

# Create Flask app
app = Flask(__name__)

# Configure CORS - Allow all origins for development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure app
app.config['MAX_CONTENT_LENGTH'] = API_CONFIG['max_content_length']

# Setup logger
logger = setup_logger('flask_app')

# Register blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(processing_bp)
app.register_blueprint(results_bp)
app.register_blueprint(audio_analysis_bp)
app.register_blueprint(video_analysis_bp)
app.register_blueprint(chat_bp)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'Crime Scene Reconstruction System',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'upload': '/api/upload',
            'processing': '/api/process',
            'results': '/api/results'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'System is operational'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        'success': False,
        'message': 'File size exceeds maximum limit'
    }), 413

def initialize_app():
    """Initialize application"""
    logger.info("Initializing Crime Scene Reconstruction System")
    
    # Preload models at startup for stability (prevents on-demand loading crashes)
    preload_models()
    
    logger.info("Application initialized successfully")

if __name__ == '__main__':
    initialize_app()
    
    logger.info(f"Starting server on {API_CONFIG['host']}:{API_CONFIG['port']}")
    
    # Disable debug reloader which can cause memory issues and duplicate model loads
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=False,
        threaded=True
    )
