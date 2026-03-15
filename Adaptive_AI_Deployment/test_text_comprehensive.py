import sys
import os
import json

# Allow import from project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from models.emotion_text import detect_text_emotion

def run_comprehensive_text_test():
    print("="*60)
    print("COMPREHENSIVE TEXT EMOTION MODEL TEST")
    print("="*60)
    
    test_cases = [
        # Basic Emotions
        ("I am so happy and excited!", "Happy"),
        ("I feel terrible and sad.", "Sad"),
        ("I am so angry right now!", "Angry"),
        ("I'm worried about the future.", "Anxious"),
        
        # Complex/Specific
        ("I feel completely overwhelmed with work.", "Stressed"),
        ("I have no one to talk to and I feel isolated.", "Lonely"),
        ("I feel like I'm worth nothing.", "Worthless"),
        ("Thank you so much for your help!", "Grateful"),
        
        # Financial / Crisis
        ("I lost my job and can't pay rent.", "Crisis"),
        ("i am facing financial struggle right now", "Stressed"), # User specifically mentioned this before
        ("I don't want to live anymore.", "Crisis"),
        
        # Neutral / Ambiguous
        ("The weather is okay today.", "Neutral"),
        ("I am just sitting here.", "Neutral"),
        ("Just a normal day.", "Neutral"),
        
        # Edge Cases
        ("hey", "Neutral"),
        ("ok", "Neutral"),
        ("i'm fine", "Neutral")
    ]
    
    results = []
    passed = 0
    
    for text, expected in test_cases:
        res = detect_text_emotion(text)
        detected = res[0]["label"]
        confidence = res[0].get("confidence", 0.0)
        
        success = (detected == expected)
        if success: passed += 1
        
        results.append({
            "text": text,
            "expected": expected,
            "detected": detected,
            "confidence": f"{confidence:.3f}",
            "status": "PASS" if success else "FAIL"
        })
        
    for r in results:
        indicator = "[PASS]" if r["status"] == "PASS" else "[FAIL]"
        print(f"{indicator} Input: '{r['text']}'")
        print(f"   Expected: {r['expected']:<10} | Detected: {r['detected']:<10} | Conf: {r['confidence']}")
        print("-" * 40)
        
    print(f"\nFINAL SCORE: {passed}/{len(test_cases)} ({(passed/len(test_cases))*100:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    run_comprehensive_text_test()
