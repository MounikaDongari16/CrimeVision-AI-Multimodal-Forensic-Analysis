import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.audio_service import audio_service

# Environmental setup
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

def test_pipeline():
    print("--- STARTING INTEGRATED AUDIO SERVICE TEST ---")
    
    # 1. Generate a dummy audio file for testing
    test_audio = "test_audio_gen.wav"
    import wave
    import struct
    import math
    import random

    print(f"Generating synthetic audio file: {test_audio}...")
    try:
        # Generate 3 seconds of "noise" / tone
        sample_rate = 16000
        duration = 3.0
        frequency = 440.0
        
        with wave.open(test_audio, 'w') as obj:
            obj.setnchannels(1) # mono
            obj.setsampwidth(2)
            obj.setframerate(sample_rate)
            
            for i in range(int(duration * sample_rate)):
                value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                data = struct.pack('<h', value)
                obj.writeframesraw(data)
                
    except Exception as e:
        print(f"❌ Failed to generate audio: {str(e)}")
        return

    try:
        # Step A: Process through main service
        print("\n[STEP A] Processing via AudioService...")
        # Mock vision summary
        v_summary = {'location': 'test_loc', 'people_count': 1}
        
        res = audio_service.process_audio_file(test_audio, v_summary)
        
        if 'error' in res:
            print(f"❌ Service returned error: {res['error']}")
            return

        # Step B: Verify Translations
        trans = res.get('transcription', {})
        print(f"Transcript (EN): {trans.get('english', '')[:50]}...")
        print(f"Telugu: {trans.get('telugu', 'Missing')[:50]}...")
        print(f"French: {trans.get('french', 'Missing')[:50]}...")

        # Step C: Verify Intelligence
        intel = res.get('facts', {})
        print(f"Actions Detected: {intel.get('actions', [])}")
        print(f"Suspect Info: {intel.get('suspect_descriptions', [])}")
        
        print(f"Summary: {res.get('summary', 'Missing')}")
        
        print("\n✅ INTEGRATED PIPELINE TEST SUCCESSFUL.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
