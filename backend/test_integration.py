import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Environmental setup
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
os.environ['USE_TF'] = 'NO'

from services.vision_service import vision_service
from services.audio_service import audio_service
from utils.model_loader import preload_models

print("--- AI PIPELINE DIAGNOSTIC START ---")
preload_models()

# 1. Test Vision Enrichment
image_path = "C:/Users/mouni/.gemini/antigravity/brain/9744e5bc-7c0d-4075-a224-c543161887e1/uploaded_image_0_1769191838606.png"
print(f"\n[Vision] Analyzing scene: {image_path}")
v_res = vision_service.analyze_crime_scene(image_path)
v_summary = v_res.get('summary', {})
print(f"Results: Location={v_summary.get('location')}, People={v_summary.get('people_count')}, Weapons={v_summary.get('weapon_types')}")

# 2. Test Audio Transformers Pipeline
# Note: We need a valid audio file. I'll search for one in the data folder.
print("\n[Audio] Testing Transformers Whisper pipeline...")
# Find any .wav or .mp3 in data/uploads
import glob
audio_files = glob.glob("../data/uploads/audio/**/*.wav", recursive=True) + glob.glob("../data/uploads/audio/**/*.mp3", recursive=True)

if audio_files:
    test_audio = audio_files[0]
    print(f"Using uploaded audio: {test_audio}")
    try:
        a_res = audio_service.process_audio_file(test_audio, v_summary)
        if 'error' in a_res:
            print(f"❌ Error in audio processing: {a_res['error']}")
        else:
            trans = a_res.get('transcription', {})
            print(f"Results: En_Text='{str(trans.get('english', ''))[:50]}...'")
            print(f"Scenarios: {len(a_res.get('scenarios', []))} generated.")
            print(f"Timeline items: {len(a_res.get('timeline', []))}")
    except Exception as e:
        print(f"❌ Diagnostic failed with error: {str(e)}")
else:
    print("No audio files found to test. Skipping audio inference step.")

print("\n--- DIAGNOSTIC COMPLETE ---")
