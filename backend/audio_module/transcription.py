from transformers import pipeline
import torch
import os
from utils.groq_utils import get_config

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Transformers Whisper Pipeline (openai/whisper-base)
    """
    config = get_config()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"LOADING TRANSFORMERS WHISPER PIPELINE (openai/whisper-base) ON {device}...")
    
    # Initialize pipeline
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        device=0 if device == "cuda" else -1
    )
    
    # Robust audio loading
    audio = None
    try:
        import librosa
        audio, _ = librosa.load(audio_file_path, sr=16000, mono=True)
    except Exception as e:
        print(f"Librosa load failed: {e}, using fallback...")
        import torchaudio
        w, s = torchaudio.load(audio_file_path)
        if s != 16000: 
            resampler = torchaudio.transforms.Resample(s, 16000)
            w = resampler(w)
        if w.shape[0] > 1: 
            w = torch.mean(w, dim=0)
        audio = w.squeeze().numpy()

    print(f"Executing Transformer-based Transcription...")
    # Execute transcription with timestamp return for timeline support
    result = pipe(audio, return_timestamps=True)
    
    # Format chunks to match the 'segments' structure previously used
    segments = []
    for chunk in result.get("chunks", []):
        ts = chunk.get("timestamp")
        segments.append({
            "start": ts[0] if isinstance(ts, tuple) else 0,
            "end": ts[1] if isinstance(ts, tuple) and len(ts) > 1 else (ts[0] if isinstance(ts, tuple) else 0),
            "text": chunk.get("text", "").strip()
        })
    
    return {
        "text": result["text"],
        "segments": segments,
        "chunks": result.get("chunks", [])
    }

