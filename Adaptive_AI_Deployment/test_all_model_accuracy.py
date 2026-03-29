import sys
import os
import numpy as np
import joblib

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from models.emotion_text import detect_text_emotion
from models.emotion_voice import _get_model as get_voice_model

def test_text_accuracy():
    print("\n" + "="*50)
    print("TEXT EMOTION ACCURACY TEST")
    print("="*50)
    
    test_cases = {
        "I am so happy and excited today!": "Happy",
        "This is a normal day, everything is fine.": "Neutral",
        "I'm feeling very sad and low.": "Sad",
        "I'm extremely stressed and have too much work.": "Stressed",
        "I feel very anxious and nervous about the exam.": "Anxious",
        "I am so angry right now!": "Angry"
    }
    
    passed = 0
    for text, expected in test_cases.items():
        result = detect_text_emotion(text)
        label = result[0]['label']
        status = "PASS" if label == expected or (expected == "Anxious" and label == "Nervous") else "FAIL"
        if status == "PASS": passed += 1
        print(f"[{status}] Input: '{text}' -> Got: {label} (Expected: {expected})")
        
    print(f"\nText Accuracy: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")

def test_voice_accuracy():
    print("\n" + "="*50)
    print("VOICE EMOTION ACCURACY TEST (Synthetic Features)")
    print("="*50)
    
    model = get_voice_model()
    if not model:
        print("Voice model not found. Skipping.")
        return

    # Generate synthetic features similar to training biases
    # 53 features (40 MFCC + 12 Chroma + 1 RMS)
    test_cases = {
        "Happy":  dict(mfcc_shift=+3.5, chroma_shift=+0.08, rms=0.12),
        "Sad":    dict(mfcc_shift=-4.0, chroma_shift=-0.06, rms=0.04),
        "Neutral":dict(mfcc_shift=0.0,  chroma_shift=0.0,   rms=0.07),
        "Nervous":dict(mfcc_shift=+1.5, chroma_shift=+0.04, rms=0.10)
    }
    
    passed = 0
    rng = np.random.RandomState(42)
    
    for expected, b in test_cases.items():
        # Create a synthetic feature vector
        mfccs = rng.normal(loc=b["mfcc_shift"], scale=0.5, size=40)
        chroma = np.clip(rng.normal(loc=0.5 + b["chroma_shift"], scale=0.05, size=12), 0, 1)
        rms = np.clip(rng.normal(loc=b["rms"], scale=0.01, size=1), 0.001, 1)
        features = np.hstack([mfccs, chroma, rms]).reshape(1, -1)
        
        label = model.predict(features)[0]
        status = "PASS" if label == expected else "FAIL"
        if status == "PASS": passed += 1
        print(f"[{status}] Synthetic {expected} Features -> Got: {label}")

    print(f"\nVoice Accuracy (Synthetic): {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")

def test_face_import():
    print("\n" + "="*50)
    print("FACE MODEL VERIFICATION")
    print("="*50)
    try:
        from models.emotion_face import HAS_MEDIAPIPE
        print(f"Face model components loaded. MediaPipe available: {HAS_MEDIAPIPE}")
        print("[PASS] Imports and initialization successful.")
    except Exception as e:
        print(f"[FAIL] Face model import error: {e}")

if __name__ == "__main__":
    test_text_accuracy()
    test_voice_accuracy()
    test_face_import()
