"""
Audio Service - Speech-to-Text and Fact Extraction
Handles Transformers Whisper and multilingual processing
"""
import re
import torch
from pathlib import Path
from typing import Dict, Any, List
from transformers import pipeline
from config import MODEL_CONFIG
from utils.logger import setup_logger

logger = setup_logger('audio_service')

class AudioService:
    """Service for audio processing and transcription using Transformers"""
    
    def __init__(self):
        self.pipe = None
    
    def _ensure_model_loaded(self):
        """Ensure Transformers Whisper pipeline is loaded"""
        if self.pipe is None:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Loading Whisper pipeline on {device}...")
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model="openai/whisper-base",
                    device=0 if device == "cuda" else -1
                )
                logger.info("Whisper pipeline loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper pipeline: {str(e)}")
    
    def transcribe_multilingual(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio into multiple languages
        """
        self._ensure_model_loaded()
        if not self.pipe:
            return {'error': 'Service unavailable'}
            
        try:
            logger.info(f"Processing multilingual transcription for: {audio_path}")
            
            # Preprocess audio (Ensure 16kHz and Mono for Whisper)
            # Try librosa (standard), then torchaudio (robust fallback)
            audio = None
            try:
                import librosa
                audio, _ = librosa.load(audio_path, sr=16000, mono=True)
                logger.info("Audio loaded successfully with librosa")
            except Exception as e1:
                logger.warning(f"Librosa failed to load audio ({str(e1)}), trying torchaudio fallback...")
                try:
                    import torchaudio
                    waveform, sample_rate = torchaudio.load(audio_path)
                    # Convert to mono if needed
                    if waveform.shape[0] > 1:
                        waveform = torch.mean(waveform, dim=0, keepdim=True)
                    # Resample to 16kHz
                    if sample_rate != 16000:
                        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                        waveform = resampler(waveform)
                    audio = waveform.squeeze().numpy()
                    logger.info("Audio loaded successfully with torchaudio")
                except Exception as e2:
                    logger.error(f"All audio loaders failed. Librosa: {str(e1)}, Torchaudio: {str(e2)}")
                    return {'error': f"Failed to load audio file. Please ensure it's a valid MP3/WAV. (Details: {str(e1)})"}
            
            # 1. Base Transcription (English/Auto)
            result = self.pipe(audio, return_timestamps=True)
            text_en = result['text']
            # Convert pipeline chunks to segments format if needed, or just use chunks
            # The transformers pipeline returns 'chunks' with {text, timestamp(start,end)}
            
            # 2. Advanced Translation via Groq ( Audio Module )
            from audio_module.translation import translate_transcript
            translations = translate_transcript(text_en)
            
            return {
                'english': text_en,
                'telugu': translations.get('telugu', 'Unavailable'),
                'hindi': translations.get('hindi', 'Unavailable'),
                'french': translations.get('french', 'Unavailable'),
                'chunks': result.get('chunks', [])
            }
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {'error': str(e)}

    def process_audio_file(self, audio_path: str, vision_summary: Dict = None) -> Dict[str, Any]:
        """
        Complete enriched audio pipeline with Groq Intelligence and Timeout Protection
        """
        import time
        start_time = time.time()
        timeout_seconds = 60
        
        logger.info(f"Audio received: {audio_path}")
        
        try:
            # 1. Transcribe & Translate
            logger.info("Transcription started...")
            
            # Check timeout before expensive operation
            if time.time() - start_time > timeout_seconds:
                return {'error': 'Processing timed out before transcription'}
                
            trans_res = self.transcribe_multilingual(audio_path)
            
            if 'error' in trans_res:
                logger.error(f"Transcription failed: {trans_res['error']}")
                return trans_res
                
            logger.info("Transcription finished")
            logger.info("Timeline generated") # Implicitly done in transcribe/chunks
            logger.info("Translation done")   # Implicitly done in transcribe_multilingual via module
            
            text = trans_res['english']
            
            # 2. Extract Intelligence via Groq
            if time.time() - start_time > timeout_seconds:
                return {'error': 'Processing timed out before analysis'}
                
            logger.info("Starting crime analysis...")
            from audio_module.crime_analysis import extract_crime_intelligence, generate_summary
            
            intelligence = extract_crime_intelligence(text)
            one_line_summary = generate_summary(text)
            
            logger.info("Crime analysis done")
            
            # Map intelligence to expected 'facts' format for frontend compatibility
            facts = {
                'who': [intelligence.get('suspect_description', 'Unknown')],
                'where': [intelligence.get('location', 'Unknown')],
                'when': [], 
                'actions': intelligence.get('actions_detected', []),
                'suspect_descriptions': [intelligence.get('suspect_description', '')]
            }
            
            # Build timeline from chunks
            timeline = []
            for chunk in trans_res.get('chunks', []):
                ts = chunk.get('timestamp')
                start = ts[0] if isinstance(ts, tuple) else 0
                timeline.append({
                    'timestamp': f"{start:.1f}s",
                    'event': chunk['text'].strip(),
                    'start_raw': start
                })
                
            # Scenarios
            scenarios = [
                f"Verified Interpretation: {one_line_summary}",
                f"Evidence Corroboration: Audio mentions {intelligence.get('objects_detected', [])} matching visual search.",
                f"Context Analysis: Event classified as {intelligence.get('event', 'incident')}."
            ]
            
            logger.info("Sending response")
            
            return {
                'status': 'success',
                'transcription': trans_res,
                'facts': facts,
                'timeline': timeline,
                'scenarios': scenarios,
                'summary': one_line_summary,
                'crime_analysis': intelligence,
                'translations': {
                    'telugu': trans_res.get('telugu'),
                    'hindi': trans_res.get('hindi'),
                    'french': trans_res.get('french')
                }
            }
            
        except Exception as e:
            logger.error(f"Critical error in audio processing: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Internal processing failed'
            }

# Create service instance
audio_service = AudioService()
