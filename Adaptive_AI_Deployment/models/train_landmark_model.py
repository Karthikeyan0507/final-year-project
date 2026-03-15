import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Geometric Features for Emotions (Synthetic "Large" Dataset for training)
# Features: [ear, mar, brow_ratio]
# Emotions: 0:Angry, 1:Happy, 2:Sad, 3:Surprise, 4:Neutral, 5:Fear/Anxious, 6:Stressed

def generate_synthetic_landmarks(n_samples=1000):
    data = []
    labels = []
    
    for _ in range(n_samples):
        # Happy
        data.append([np.random.normal(0.3, 0.02), np.random.normal(0.4, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Happy")
        
        # Sad
        data.append([np.random.normal(0.22, 0.02), np.random.normal(0.15, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Sad")
        
        # Angry
        data.append([np.random.normal(0.28, 0.02), np.random.normal(0.1, 0.02), np.random.normal(0.5, 0.05)])
        labels.append("Angry")
        
        # Surprise
        data.append([np.random.normal(0.4, 0.03), np.random.normal(0.6, 0.05), np.random.normal(0.8, 0.05)])
        labels.append("Surprise")
        
        # Neutral
        data.append([np.random.normal(0.3, 0.02), np.random.normal(0.2, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Neutral")
        
        # Fear / Anxious (Wide eyes, tense mouth)
        data.append([np.random.normal(0.38, 0.02), np.random.normal(0.3, 0.05), np.random.normal(0.65, 0.05)])
        labels.append("Fear")
        
        # Stressed (Tense eyes, furrowed brows)
        data.append([np.random.normal(0.25, 0.02), np.random.normal(0.15, 0.05), np.random.normal(0.5, 0.05)])
        labels.append("Stressed")

    return np.array(data), np.array(labels)

print("Generating synthetic landmark dataset...")
X, y = generate_synthetic_landmarks(2000)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Landmark-based RF Classifier...")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(f"Landmark Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# Save the model
model_path = os.path.join(os.path.dirname(__file__), 'face_landmark_model.pkl')
print(f"Saving landmark model to {model_path}...")
with open(model_path, 'wb') as f:
    pickle.dump(clf, f)

print("Landmark training complete.")
