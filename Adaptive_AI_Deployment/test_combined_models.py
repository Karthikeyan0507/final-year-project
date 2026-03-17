import sys
import os
import json
from pprint import pprint

sys.path.append(os.path.abspath("."))
from models.emotion_text import detect_text_emotion
from rl_engine.therapy_rl import choose_therapy

def run_tests():
    print("="*50)
    print("TESTING TEXT MODEL & THERAPY RECOMMENDER")
    print("="*50)
    
    test_cases = [
        "I feel so lonely and isolated.",
        "I'm terrified that something bad might happen.",
        "This completely pisses me off.",
        "I am looking at the camera."
    ]
    
    for text in test_cases:
        print(f"\n--- Output for: '{text}' ---")
        text_results = detect_text_emotion(text)
        text_emotion = text_results[0]["label"]
        print(f"Detected Text Emotion: {text_emotion}")
        
        recs = choose_therapy(text_emotion)
        print("Therapy Recs:")
        for k, v in recs.items():
            print(f"  {k.capitalize()}: {v}")
            
    print("\n" + "="*50)
    print("TESTING FACE MODEL & GEOMETRIC OVERRIDES")
    print("="*50)
    
    print("\n--- Simulating Drowsy Face (Low EAR) ---")
    # Low EAR simulation
    mock_face_features = {"ear": 0.18, "brow_ratio": 1.0}
    face_emotion = "Sad" # Or neutral
    
    print(f"Face Features: {mock_face_features}")
    recs = choose_therapy(face_emotion, mock_face_features)
    print("Overrides should enforce Sleep Hygiene and Power Naps.")
    for k, v in recs.items():
        print(f"  {k.capitalize()}: {v}")

    print("\n--- Simulating Stressed Face (Low Brow Ratio) ---")
    mock_face_features2 = {"ear": 0.35, "brow_ratio": 0.45}
    face_emotion2 = "Anxious"
    
    print(f"Face Features: {mock_face_features2}")
    recs2 = choose_therapy(face_emotion2, mock_face_features2)
    print("Overrides should enforce Stress Management Coaching and PMR.")
    for k, v in recs2.items():
        print(f"  {k.capitalize()}: {v}")
        
if __name__ == "__main__":
    run_tests()
