"""
File handling utilities for secure upload and storage
"""
import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from config import (
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS, ALLOWED_REPORT_EXTENSIONS,
    MAX_FILE_SIZE, IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, REPORTS_DIR
)
from utils.logger import setup_logger

logger = setup_logger('file_handler')

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
    
    Returns:
        True if extension is valid, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions

def validate_file_size(file: FileStorage, max_size: int = MAX_FILE_SIZE) -> bool:
    """
    Validate file size
    
    Args:
        file: FileStorage object
        max_size: Maximum allowed size in bytes
    
    Returns:
        True if size is valid, False otherwise
    """
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

def get_file_type(filename: str) -> Optional[str]:
    """
    Determine file type based on extension
    
    Args:
        filename: Name of the file
    
    Returns:
        File type ('image', 'video', 'audio', 'report') or None
    """
    ext = Path(filename).suffix.lower()
    
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    elif ext in ALLOWED_AUDIO_EXTENSIONS:
        return 'audio'
    elif ext in ALLOWED_REPORT_EXTENSIONS:
        return 'report'
    return None

def get_storage_directory(file_type: str) -> Path:
    """
    Get storage directory for file type
    
    Args:
        file_type: Type of file
    
    Returns:
        Path to storage directory
    """
    directories = {
        'image': IMAGES_DIR,
        'video': VIDEOS_DIR,
        'audio': AUDIO_DIR,
        'report': REPORTS_DIR
    }
    return directories.get(file_type, IMAGES_DIR)

def save_uploaded_file(file: FileStorage, case_id: str) -> Tuple[bool, str, Optional[str]]:
    """
    Save uploaded file with validation
    
    Args:
        file: FileStorage object
        case_id: Case identifier for organizing files
    
    Returns:
        Tuple of (success, message, file_path)
    """
    try:
        # Validate filename
        if not file.filename:
            return False, "No filename provided", None
        
        # Determine file type
        file_type = get_file_type(file.filename)
        if not file_type:
            return False, f"Invalid file type. Allowed types: images, videos, audio, reports", None
        
        # Validate extension
        allowed_extensions = {
            'image': ALLOWED_IMAGE_EXTENSIONS,
            'video': ALLOWED_VIDEO_EXTENSIONS,
            'audio': ALLOWED_AUDIO_EXTENSIONS,
            'report': ALLOWED_REPORT_EXTENSIONS
        }
        
        if not validate_file_extension(file.filename, allowed_extensions[file_type]):
            return False, f"Invalid file extension for {file_type}", None
        
        # Validate size
        if not validate_file_size(file):
            return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024):.0f} MB", None
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = Path(original_filename).suffix
        unique_filename = f"{case_id}_{uuid.uuid4().hex}{file_ext}"
        
        # Get storage directory
        storage_dir = get_storage_directory(file_type)
        case_dir = storage_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = case_dir / unique_filename
        file.save(str(file_path))
        
        logger.info(f"File saved: {file_path} (type: {file_type}, size: {file_path.stat().st_size} bytes)")
        
        return True, "File uploaded successfully", str(file_path)
    
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False, f"Error saving file: {str(e)}", None

def get_file_info(file_path: str) -> dict:
    """
    Get file information
    
    Args:
        file_path: Path to file
    
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {'error': 'File not found'}
    
    return {
        'filename': path.name,
        'size': path.stat().st_size,
        'type': get_file_type(path.name),
        'extension': path.suffix,
        'path': str(path)
    }

def cleanup_temp_files(case_id: str):
    """
    Clean up temporary files for a case
    
    Args:
        case_id: Case identifier
    """
    from config import TEMP_DIR
    
    case_temp_dir = TEMP_DIR / case_id
    if case_temp_dir.exists():
        import shutil
        shutil.rmtree(case_temp_dir)
        logger.info(f"Cleaned up temp files for case: {case_id}")
