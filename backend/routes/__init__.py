# Route modules
from .upload_routes import upload_bp
from .processing_routes import processing_bp
from .results_routes import results_bp

__all__ = [
    'upload_bp',
    'processing_bp',
    'results_bp'
]
