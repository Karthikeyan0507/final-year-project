import os
import sys
import numpy as np
import scipy.io.wavfile as wav
import base64

# Add parent directory to path to allow importing models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from models.emotion_voice import detect_voice_emotion

def generate_synthetic_audio(filename, duration_sec=3, sample_rate=16000):
    """Generates a synthetic sine wave audio file with noise."""
    print(f"Generating synthetic audio: {filename}")
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    # Generate a 440 Hz sine wave
    tone = np.sin(440 * 2 * np.pi * t)
    
    # Add some random noise
    noise = np.random.normal(0, 0.1, tone.shape)
    audio = tone + noise
    
    # Normalize to 16-bit range
    audio_normalized = np.int16(audio / np.max(np.abs(audio)) * 32767)
    
    # Save the file
    filepath = os.path.join(os.path.dirname(__file__), filename)
    wav.write(filepath, sample_rate, audio_normalized)
    return filepath

def test_voice_emotion():
    print("=" * 50)
    print("  Testing Voice Emotion Detection (Synthetic)")
    print("=" * 50)
    
    filename = "sample_audio_test.wav"
    filepath = generate_synthetic_audio(filename)
    
    print("\nReading generated audio file...")
    with open(filepath, "rb") as f:
        audio_bytes = f.read()
        
    print("Encoding audio to base64...")
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    print("\nRunning detect_voice_emotion(audio_b64)...")
    try:
        predicted_emotion = detect_voice_emotion(audio_b64)
        print("\n" + "=" * 50)
        print(f"  RESULT: Predicted Emotion = {predicted_emotion}")
        print("=" * 50)
    except Exception as e:
        print(f"\n[ERROR] Detection failed: {e}")
    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"\nCleaned up generated file: {filename}")

if __name__ == "__main__":
    test_voice_emotion()
