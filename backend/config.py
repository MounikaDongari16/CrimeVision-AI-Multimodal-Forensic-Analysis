"""
Configuration file for the Crime Scene Reconstruction System
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Upload directories
UPLOAD_DIR = DATA_DIR / "uploads"
IMAGES_DIR = UPLOAD_DIR / "images"
VIDEOS_DIR = UPLOAD_DIR / "videos"
AUDIO_DIR = UPLOAD_DIR / "audio"
REPORTS_DIR = UPLOAD_DIR / "reports"

# Output directories
OUTPUT_DIR = DATA_DIR / "outputs"
ANNOTATIONS_DIR = OUTPUT_DIR / "annotations"
RECONSTRUCTIONS_DIR = OUTPUT_DIR / "reconstructions"
REPORTS_OUTPUT_DIR = OUTPUT_DIR / "reports"
SESSIONS_DIR = OUTPUT_DIR / "sessions"
TEMP_DIR = OUTPUT_DIR / "temp"

# Create directories if they don't exist
for directory in [IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, REPORTS_DIR, 
                  ANNOTATIONS_DIR, RECONSTRUCTIONS_DIR, REPORTS_OUTPUT_DIR, SESSIONS_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File upload settings
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}
ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.flac'}
ALLOWED_REPORT_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx'}

# Model configurations
MODEL_CONFIG = {
    'rt_detr': {
        'model_name': 'PekingU/rtdetr_r101vd_coco_o365',
        'device': 'cuda',  # Will fallback to 'cpu' if CUDA not available
        'confidence_threshold': 0.3,
        'target_classes': [
            'person', 'weapon', 'knife', 'gun', 'car', 'truck', 'motorcycle',
            'backpack', 'handbag', 'cell phone', 'bottle', 'bloodstain'
        ]
    },
    'sam': {
        'model_type': 'vit_h',
        'checkpoint': None,  # Path to SAM checkpoint
        'device': 'cuda'
    },
    'clip': {
        'model_name': 'openai/clip-vit-base-patch32',
        'device': 'cuda'
    },
    'whisper': {
        'model_name': 'base',  # Options: tiny, base, small, medium, large
        'device': 'cuda',
        'language': 'en'
    },
    'llm': {
        'model_name': 'meta-llama/Llama-2-7b-chat-hf',  # Or GPT API
        'device': 'cuda',
        'max_length': 2048,
        'temperature': 0.7
    },
    'llava': {
        'model_name': 'llava-hf/llava-1.5-7b-hf',
        'device': 'cuda'
    }
}

# Processing settings
PROCESSING_CONFIG = {
    'video_frame_rate': 1,  # Extract 1 frame per second
    'max_video_duration': 600,  # 10 minutes max
    'audio_chunk_size': 30,  # Process audio in 30-second chunks
    'enable_gpu': True,
    'batch_size': 8
}

# 3D Reconstruction settings
RECONSTRUCTION_CONFIG = {
    'default_room_size': [30, 30, 15],  # Significantly increased for massive image visibility
    'object_scale_factor': 1.0,
    'point_cloud_density': 1000,
    'export_format': 'json'  # json, ply, obj
}

# Report settings
REPORT_CONFIG = {
    'pdf_template': 'default',
    'include_images': True,
    'include_timeline': True,
    'include_3d_snapshot': True,
    'confidence_threshold': 0.3
}

# API settings
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'cors_origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
    'max_content_length': MAX_FILE_SIZE
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'logs' / 'app.log'
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)
