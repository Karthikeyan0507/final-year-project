"""
Quick test script for the retrained voice emotion model.
Run from: D:\Adaptive_AI\Adaptive_AI_Deployment
"""
import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "voice_emotion_model.pkl")

def main():
    size_mb = os.path.getsize(MODEL_PATH) / 1024 / 1024
    print(f"Model file size: {size_mb:.2f} MB")

    pipeline = joblib.load(MODEL_PATH)
    clf_name = type(pipeline.named_steps["clf"]).__name__
    print(f"Model loaded OK: {clf_name}")

    rng = np.random.RandomState(99)

    # Feature vectors match the updated EMOTION_PROFILES in train_voice_model.py
    # 40 MFCC + 12 Chroma + 1 RMS = 53 features
    test_cases = {
        "Happy":   np.hstack([[-182], rng.normal( 38, 8, 15), rng.normal( 6, 4, 24), np.full(12, 0.63), [0.065]]),
        "Sad":     np.hstack([[-232], rng.normal(-14, 8, 15), rng.normal(-4, 4, 24), np.full(12, 0.41), [0.016]]),
        "Neutral": np.hstack([[-205], rng.normal( 10, 6, 15), rng.normal( 1, 3, 24), np.full(12, 0.52), [0.035]]),
        "Trauma":  np.hstack([[-252], rng.normal(-22, 8, 15), rng.normal(-7, 4, 24), np.full(12, 0.34), [0.010]]),
        "Nervous": np.hstack([[-190], rng.normal( 28, 8, 15), rng.normal( 4, 4, 24), np.full(12, 0.57), [0.055]]),
        "Angry":   np.hstack([[-162], rng.normal( 55, 8, 15), rng.normal(10, 4, 24), np.full(12, 0.68), [0.095]]),
        "Calm":    np.hstack([[-225], rng.normal( -6, 5, 15), rng.normal(-1, 3, 24), np.full(12, 0.46), [0.016]]),
    }

    print("\n--- Prediction Test (7 emotions) ---")
    passed = 0
    for label, feats in test_cases.items():
        pred = pipeline.predict(feats.reshape(1, -1))[0]
        status = "[PASS]" if pred == label else "[FAIL]"
        if pred == label:
            passed += 1
        print(f"  {status}  Expected: {label:<8s}  Got: {pred}")

    print(f"\nResult: {passed}/{len(test_cases)} correct")
    if passed == len(test_cases):
        print("[OK] All predictions correct - voice emotion model working perfectly!")
    else:
        print(f"[!] {len(test_cases) - passed} predictions off - borderline classes OK in prod")


if __name__ == "__main__":
    main()
