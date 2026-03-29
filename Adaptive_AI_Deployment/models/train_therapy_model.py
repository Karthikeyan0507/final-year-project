"""
Trains a predictive Multimodal Therapy Recommendation Model.
Fuses Voice, Text, and Face emotions into a trained Random Forest classifier
to output the statistically optimal therapy path, replacing random/fallback guessing.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = os.path.join(os.path.dirname(__file__), "therapy_recommendation_model.pkl")

# Emotional classes expected from Face, Voice, Text engines
EMOTIONS = ["Neutral", "Happy", "Sad", "Angry", "Fear", "Surprise", "Disgust", "Trauma", "Nervous", "Calm"]

# Therapy Classes (Target)
THERAPIES = [
    "Crisis Intervention & Stabilization",
    "Social Connection Therapy",
    "Positive Psychology Reinforcement",
    "Stress Management Coaching",
    "Sleep Hygiene Education",
    "Cognitive Behavioral Therapy (CBT) Techniques",
    "Dialectical Behavior Therapy (DBT) Skills",
    "Acceptance and Commitment Therapy (ACT)"
]

def generate_synthetic_data(n_samples=5000):
    rng = np.random.RandomState(42)
    data = []
    
    for _ in range(n_samples):
        # Base emotion drives 70% of the variance
        base = rng.choice(["Happy", "Sad", "Angry", "Nervous", "Neutral", "Trauma", "Calm"])
        
        # Text, Voice, Face will mostly follow base, with some realistic divergence
        def get_modality(base_em):
            if rng.rand() > 0.3:
                return base_em
            return rng.choice(EMOTIONS)
            
        t_emt = get_modality(base)
        v_emt = get_modality(base)
        f_emt = get_modality(base)
        
        # Calculate distress/intensity rules
        distress_score = 0.0
        if "Trauma" in [t_emt, v_emt, f_emt]: distress_score += 0.8
        if "Sad" in [t_emt, v_emt, f_emt]: distress_score += 0.4
        if "Nervous" in [t_emt, v_emt, f_emt] or "Fear" in [t_emt, v_emt, f_emt]: distress_score += 0.5
        if "Angry" in [t_emt, v_emt, f_emt]: distress_score += 0.5
        
        # Add random noise
        distress_score += rng.uniform(-0.1, 0.2)
        distress_score = max(0.0, min(1.0, distress_score))
        
        # Target determination (ground truth for training)
        if distress_score > 0.75 or "Trauma" in [t_emt, v_emt, f_emt]:
            target = "Crisis Intervention & Stabilization"
        elif "Sad" in [t_emt, v_emt, f_emt] and distress_score < 0.6:
            target = rng.choice(["Social Connection Therapy", "Cognitive Behavioral Therapy (CBT) Techniques"])
        elif "Nervous" in [t_emt, v_emt, f_emt] or "Fear" in [t_emt, v_emt, f_emt]:
            target = rng.choice(["Stress Management Coaching", "Dialectical Behavior Therapy (DBT) Skills"])
        elif "Angry" in [t_emt, v_emt, f_emt]:
            target = "Acceptance and Commitment Therapy (ACT)"
        elif "Happy" in [t_emt, v_emt, f_emt] or "Calm" in [t_emt, v_emt, f_emt]:
            target = "Positive Psychology Reinforcement"
        else:
            target = rng.choice(["Cognitive Behavioral Therapy (CBT) Techniques", "Sleep Hygiene Education"])
            
        data.append({
            "text_emotion": t_emt,
            "voice_emotion": v_emt,
            "face_emotion": f_emt,
            "distress_score": distress_score,
            "therapy": target
        })
        
    return pd.DataFrame(data)

def train_therapy_model():
    print("============================================================")
    print("   LYKA Therapy ML Model  -  Training  (Fusion v1)")
    print("============================================================")
    
    print("[1/4] Generating combined multimodal dataset...")
    df = generate_synthetic_data(8000)
    
    print("[2/4] Preprocessing categorical features...")
    # Label encode categorical input features
    le_text = LabelEncoder()
    le_voice = LabelEncoder()
    le_face = LabelEncoder()
    
    df['t_enc'] = le_text.fit_transform(df['text_emotion'])
    df['v_enc'] = le_voice.fit_transform(df['voice_emotion'])
    df['f_enc'] = le_face.fit_transform(df['face_emotion'])
    
    X = df[['t_enc', 'v_enc', 'f_enc', 'distress_score']].values
    y = df['therapy'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    print(f"      Train: {len(X_train)}  |  Test: {len(X_test)}")
    print("[3/4] Fitting RandomForest Classifier...")
    
    clf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    print("[4/4] Validating...")
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"      Accuracy: {acc:.4f}\n")
    print(classification_report(y_test, y_pred))
    
    # Save the model and encoders as a single bundle
    bundle = {
        "model": clf,
        "encoders": {
            "text": le_text,
            "voice": le_voice,
            "face": le_face
        }
    }
    
    joblib.dump(bundle, MODEL_PATH)
    print(f"============================================================")
    print(f"  [OK] Model successfully trained and saved!")
    print(f"  Path: {MODEL_PATH}")
    print(f"============================================================")

if __name__ == "__main__":
    train_therapy_model()
