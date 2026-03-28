"""
Voice Emotion Model Training Script
Trains a Random Forest classifier with 53 audio features:
  - 40 MFCCs (higher → better discrimination)
  - 12 Chroma (pitch/tonality)
  -  1 RMS Energy (loudness/stress)

NOTE: This uses synthetic data tuned by emotion-specific patterns to produce
a functional model. Replace X and y with real labeled audio features
(e.g. from RAVDESS or CREMA-D) for production-grade accuracy.
"""
import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MODEL_PATH = os.path.join(os.path.dirname(__file__), "voice_emotion_model.pkl")

NUM_FEATURES = 53  # 40 MFCC + 12 Chroma + 1 RMS — must match emotion_voice.py

EMOTIONS = {
    # label: (num_samples, feature_bias_vector hints)
    "Happy":     400,
    "Sad":       400,
    "Neutral":   300,
    "Trauma":    300,
    "Nervous":   300,
}

def generate_samples():
    """
    Generate synthetic feature samples per emotion with distinctive biases
    so the model learns meaningful separations even without real data.
    """
    X, y = [], []
    rng = np.random.RandomState(42)

    # Emotion-specific parameter biases:
    # Each emotion gets a shifted mean and scaled std to create clusters.
    biases = {
        #              MFCC base   Chroma  RMS
        "Happy":   dict(mfcc_shift=+3.5, chroma_shift=+0.08, rms=0.12,  noise=1.2),
        "Sad":     dict(mfcc_shift=-4.0, chroma_shift=-0.06, rms=0.04,  noise=1.0),
        "Neutral": dict(mfcc_shift=0.0,  chroma_shift=0.0,   rms=0.07,  noise=0.8),
        "Trauma":  dict(mfcc_shift=-6.0, chroma_shift=-0.10, rms=0.02,  noise=1.5),
        "Nervous": dict(mfcc_shift=+1.5, chroma_shift=+0.04, rms=0.10,  noise=1.6),
    }

    for emotion, n_samples in EMOTIONS.items():
        b = biases[emotion]
        for _ in range(n_samples):
            # MFCCs: 40 values centered around a biased mean
            mfccs  = rng.normal(loc=b["mfcc_shift"], scale=b["noise"], size=40)
            # Chroma: 12 values in [0,1] biased around some mean
            chroma = np.clip(rng.normal(loc=0.5 + b["chroma_shift"], scale=0.12, size=12), 0, 1)
            # RMS: 1 value representing energy
            rms    = np.clip(rng.normal(loc=b["rms"], scale=0.02, size=1), 0.001, 1)

            features = np.hstack([mfccs, chroma, rms])
            X.append(features)
            y.append(emotion)

    return np.array(X), np.array(y)


def train():
    print("=" * 50)
    print("  LYKA Voice Emotion Model Training")
    print("=" * 50)

    print(f"\nGenerating synthetic dataset ({sum(EMOTIONS.values())} samples, {NUM_FEATURES} features)...")
    X, y = generate_samples()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])

    print("\nRunning 5-fold cross-validation...")
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="accuracy")
    print(f"  CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"  Per-fold:    {[f'{s:.3f}' for s in cv_scores]}")

    print("\nFitting final model on full training set...")
    pipeline.fit(X_train, y_train)

    test_acc = pipeline.score(X_test, y_test)
    print(f"  Hold-out test accuracy: {test_acc:.3f}")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print("=" * 50)
    print("Training complete!")


if __name__ == "__main__":
    train()
