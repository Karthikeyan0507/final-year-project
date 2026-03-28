import os
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Load the large dataset
dataset_path = os.path.join(os.path.dirname(__file__), 'large_text_dataset.csv')
if os.path.exists(dataset_path):
    print(f"Loading large dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
else:
    print("Dataset not found. Falling back to small hardcoded dataset.")
    data = [("Hello", "Neutral"), ("I'm sad", "Sad"), ("I'm happy", "Happy")]
    df = pd.DataFrame(data, columns=['text', 'emotion'])

# Data Augmentation — lowercase only to reduce noise
df_lower = df.copy()
df_lower['text'] = df_lower['text'].str.lower()
df = pd.concat([df, df_lower]).drop_duplicates(subset=['text'])
df = df.dropna(subset=['text'])

print(f"Total training examples after augmentation: {len(df)}")

X = df['text']
y = df['emotion']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# TF-IDF Vectorizer — keep pronouns by not removing stop words
tfidf = TfidfVectorizer(ngram_range=(1, 3), max_features=15000, min_df=2)

# Fast LogisticRegression — 10-50x faster inference than a RandomForest ensemble
# saga solver handles L2 regularization well on multi-class problems
lr = LogisticRegression(
    class_weight='balanced',
    C=5.0,
    max_iter=2000,
    solver='saga',
    multi_class='multinomial',
    n_jobs=-1  # use all CPU cores
)

# Single-step Pipeline (no ensemble overhead)
pipeline = Pipeline([
    ('tfidf', tfidf),
    ('clf', lr)
])

print("Training the fast LogisticRegression text emotion model...")
pipeline.fit(X_train, y_train)

print("Evaluating the model...")
y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Validation Accuracy: {acc * 100:.2f}%\n")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Save
models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(models_dir, exist_ok=True)
model_path = os.path.join(models_dir, 'text_emotion_model.pkl')
print(f"Saving the model to {model_path}...")
with open(model_path, 'wb') as f:
    pickle.dump(pipeline, f)

print("Training complete. Fast LogisticRegression model saved.")
