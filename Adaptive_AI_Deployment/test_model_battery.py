import sys
import os
import json
from pprint import pprint

# Allow import from project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from models.emotion_text import detect_text_emotion
from models.emotion_face import detect_face_emotion
from rl_engine.therapy_rl import choose_therapy

def test_text_model():
    print("\n" + "="*50)
    print("TESTING TEXT MODEL (ENSEMBLE)")
    print("="*50)
    
    test_cases = [
        ("I'm feeling really happy today!", "Happy"),
        ("Everything is falling apart and I'm stressed.", "Stressed"),
        ("I feel so lonely, nobody cares.", "Lonely"),
        ("i am facing financial struggle right now", "Stressed"),
        ("I am helpless... i gonna endup my life soon", "Crisis")
    ]
    
    passed = 0
    for text, expected in test_cases:
        res = detect_text_emotion(text)
        detected = res[0]["label"]
        status = "PASS" if detected == expected else f"FAIL (Got {detected})"
        if detected == expected: passed += 1
        print(f"Input: '{text}' -> {status}")
        
    print(f"\nText Model Score: {passed}/{len(test_cases)}")

def test_face_model_refinement():
    print("\n" + "="*50)
    print("TESTING FACE MODEL (LANDMARK REFINEMENT)")
    print("="*50)
    
    # We can't easily test visual FER without a webcam, 
    # but we can test the refinement logic in emotion_face.py
    # or simulate the feature detection.
    
    # Let's test if the landmark model exists and refine logic is safe
    try:
        from models.emotion_face import landmark_clf
        if landmark_clf:
            print("Landmark Classifier: LOADED")
            # Mock a stressed landmark set [ear, mar, brow_ratio]
            # Stressed pattern roughly: [0.25, 0.15, 0.5]
            test_landmark = [[0.25, 0.15, 0.5]]
            pred = landmark_clf.predict(test_landmark)[0]
            print(f"Landmark Test (Stressed Params): Predicted {pred}")
        else:
            print("Landmark Classifier: NOT FOUND")
    except Exception as e:
        print(f"Landmark Test Error: {e}")

def test_combined_logic():
    print("\n" + "="*50)
    print("TESTING COMBINED FUSION LOGIC")
    print("="*50)
    
    # Simulate the logic found in backend/app.py
    def simulate_fusion(text_emo, face_emo):
        # Logic from app.py: final_emotion = face_emotion if face_emotion != "Neutral" else text_emotion
        final = face_emo if face_emo != "Neutral" else text_emo
        return final

    cases = [
        ("Happy", "Neutral", "Happy"),
        ("Sad", "Angry", "Angry"),
        ("Neutral", "Happy", "Happy"),
        ("Crisis", "Neutral", "Crisis")
    ]
    
    for t, f, expected in cases:
        result = simulate_fusion(t, f)
        status = "PASS" if result == expected else "FAIL"
        print(f"Text: {t}, Face: {f} -> Fused: {result} ({status})")

if __name__ == "__main__":
    test_text_model()
    test_face_model_refinement()
    test_combined_logic()
    print("\n" + "="*50)
    print("TEST BATTERY COMPLETE")
    print("="*50)
