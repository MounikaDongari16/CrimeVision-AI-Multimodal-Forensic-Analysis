import torch
import os

# Disable TensorFlow to avoid protobuf registration conflicts between TF and Torch
# This project uses PyTorch exclusively.
os.environ['USE_TF'] = 'NO'
os.environ['USE_TORCH'] = 'YES'
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
# Force TF to be invisible if it still tries to load
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from typing import Dict, Any, Optional
from config import MODEL_CONFIG, PROCESSING_CONFIG
from utils.logger import setup_logger

logger = setup_logger('model_loader')

class ModelCache:
    """Singleton class for caching loaded models"""
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelCache, cls).__new__(cls)
        return cls._instance
    
    def get_model(self, model_name: str):
        """Get cached model or return None"""
        return self._models.get(model_name)
    
    def set_model(self, model_name: str, model: Any):
        """Cache a model"""
        self._models[model_name] = model
        logger.info(f"Model cached: {model_name}")
    
    def clear_cache(self):
        """Clear all cached models"""
        self._models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Model cache cleared")

# Global cache instance
model_cache = ModelCache()

def get_device() -> str:
    """
    Get the appropriate device for model inference
    
    Returns:
        Device string ('cuda' or 'cpu')
    """
    if PROCESSING_CONFIG['enable_gpu'] and torch.cuda.is_available():
        device = 'cuda'
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        logger.info("Using CPU for inference")
    return device

def load_rt_detr_model():
    """
    Load RT-DETR model for object detection
    
    Returns:
        RT-DETR model and processor
    """
    cached = model_cache.get_model('rt_detr')
    if cached:
        return cached
    
    try:
        from transformers import AutoImageProcessor, AutoModelForObjectDetection
        
        config = MODEL_CONFIG['rt_detr']
        device = get_device()
        
        logger.info(f"Loading RT-DETR model: {config['model_name']}")
        
        processor = AutoImageProcessor.from_pretrained(config['model_name'])
        model = AutoModelForObjectDetection.from_pretrained(config['model_name'])
        model.to(device)
        model.eval()
        
        result = {'model': model, 'processor': processor, 'device': device}
        model_cache.set_model('rt_detr', result)
        
        logger.info("RT-DETR model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading RT-DETR model: {str(e)}")
        return None

def load_clip_model():
    """
    Load CLIP model for vision-language matching
    
    Returns:
        CLIP model and processor
    """
    cached = model_cache.get_model('clip')
    if cached:
        return cached
    
    try:
        from transformers import CLIPProcessor, CLIPModel
        
        config = MODEL_CONFIG['clip']
        device = get_device()
        
        logger.info(f"Loading CLIP model: {config['model_name']}")
        
        processor = CLIPProcessor.from_pretrained(config['model_name'])
        model = CLIPModel.from_pretrained(config['model_name'])
        model.to(device)
        model.eval()
        
        result = {'model': model, 'processor': processor, 'device': device}
        model_cache.set_model('clip', result)
        
        logger.info("CLIP model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading CLIP model: {str(e)}")
        return None

def load_whisper_model():
    """
    Load Whisper model for speech-to-text using Transformers pipeline
    """
    cached = model_cache.get_model('whisper')
    if cached:
        return cached
    
    try:
        from transformers import pipeline
        
        config = MODEL_CONFIG['whisper']
        device = get_device()
        
        logger.info(f"Loading Whisper pipeline: {config['model_name']} on {device}")
        
        pipe = pipeline(
            "automatic-speech-recognition",
            model=config['model_name'],
            device=0 if device == 'cuda' else -1
        )
        
        result = {'model': pipe}
        model_cache.set_model('whisper', result)
        
        logger.info("Whisper pipeline loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading Whisper pipeline: {str(e)}")
        return None

def load_llm_model():
    """
    Load LLM model for text processing
    
    Returns:
        LLM model and tokenizer
    """
    cached = model_cache.get_model('llm')
    if cached:
        return cached
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        config = MODEL_CONFIG['llm']
        device = get_device()
        
        logger.info(f"Loading LLM model: {config['model_name']}")
        
        tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        model = AutoModelForCausalLM.from_pretrained(
            config['model_name'],
            torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            device_map='auto' if device == 'cuda' else None
        )
        
        if device == 'cpu':
            model.to(device)
        
        model.eval()
        
        result = {'model': model, 'tokenizer': tokenizer, 'device': device}
        model_cache.set_model('llm', result)
        
        logger.info("LLM model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading LLM model: {str(e)}")
        # Return None - can use GPT API as fallback
        return None

def load_llava_model():
    """
    Load LLaVA model for multimodal fusion
    
    Returns:
        LLaVA model and processor
    """
    cached = model_cache.get_model('llava')
    if cached:
        return cached
    
    try:
        from transformers import LlavaForConditionalGeneration, AutoProcessor
        
        config = MODEL_CONFIG['llava']
        device = get_device()
        
        logger.info(f"Loading LLaVA model: {config['model_name']}")
        
        processor = AutoProcessor.from_pretrained(config['model_name'])
        model = LlavaForConditionalGeneration.from_pretrained(
            config['model_name'],
            torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            device_map='auto' if device == 'cuda' else None
        )
        
        if device == 'cpu':
            model.to(device)
        
        model.eval()
        
        result = {'model': model, 'processor': processor, 'device': device}
        model_cache.set_model('llava', result)
        
        logger.info("LLaVA model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading LLaVA model: {str(e)}")
        return None

def load_blip2_model():
    """
    Load BLIP-Large model for high-accuracy Image Captioning
    
    Returns:
        BLIP model and processor
    """
    cached = model_cache.get_model('blip2')
    if cached:
        return cached
    
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        # Using Large model (much more accurate than base, but manageable size)
        model_name = "Salesforce/blip-image-captioning-large" 
        device = get_device()
        
        logger.info(f"Loading BLIP-Large model: {model_name}")
        
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name)
        model.to(device)
        model.eval()
        
        result = {'model': model, 'processor': processor, 'device': device}
        model_cache.set_model('blip2', result)
        
        logger.info("BLIP-Large model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading BLIP model: {str(e)}")
        return None

def load_sam_model():
    """
    Load SAM (Segment Anything Model) for precision masking
    """
    cached = model_cache.get_model('sam')
    if cached:
        return cached
    
    try:
        from transformers import SamModel, SamProcessor
        
        config = MODEL_CONFIG['sam']
        # Using huggingface version if checkpoint not path
        model_id = "facebook/sam-vit-base" # Using base for local speed/memory, huge is very big
        device = get_device()
        
        logger.info(f"Loading SAM model: {model_id}")
        
        processor = SamProcessor.from_pretrained(model_id)
        model = SamModel.from_pretrained(model_id)
        model.to(device)
        model.eval()
        
        result = {'model': model, 'processor': processor, 'device': device}
        model_cache.set_model('sam', result)
        
        logger.info("SAM model loaded successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error loading SAM model: {str(e)}")
        return None

def preload_models():
    """
    Preload all models at startup
    """
    logger.info("Preloading models...")
    
    models_to_load = [
        ('RT-DETR', load_rt_detr_model),
        ('CLIP', load_clip_model),
        ('BLIP-2', load_blip2_model),
        ('SAM', load_sam_model), # Added SAM
        ('Whisper', load_whisper_model),
    ]
    
    for name, loader in models_to_load:
        try:
            loader()
        except Exception as e:
            logger.warning(f"Failed to preload {name}: {str(e)}")
    
    logger.info("Model preloading complete")
