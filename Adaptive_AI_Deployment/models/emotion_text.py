import os
import pickle

# Load the trained text emotion model once when this module is imported
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'text_emotion_model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        emotion_model = pickle.load(f)
    print("Successfully loaded the trained Text Emotion ML model.")
except Exception as e:
    print(f"Warning: Could not load the Text Emotion ML model from {MODEL_PATH}. Reason: {e}")
    emotion_model = None

def get_text_intensity(text_lower):
    # Intensity indicators
    intensity_high = ["very", "so", "extremely", "really", "incredibly", "completely", "totally", "absolutely"]
    intensity_low = ["a bit", "a little", "somewhat", "kind of", "sort of", "slightly"]
    
    intensity = "moderate"
    for intensifier in intensity_high:
        if intensifier in text_lower:
            intensity = "high"
            break
            
    if intensity == "moderate":
        for reducer in intensity_low:
            if reducer in text_lower:
                intensity = "low"
                break
    return intensity

def detect_text_emotion(text):
    """
    Detect emotion from text using a trained scikit-learn ML classification model.
    Returns a list with a 'label' key to match backend usage.
    Detects granular emotions: Lonely, Anxious, Stressed, Sad, Happy, Angry, Grateful, Worthless, Crisis, Neutral.
    """
    if not text:
        return [{"label": "Neutral", "confidence": 1.0, "intensity": "moderate"}]
        
    text_lower = text.lower()
    intensity = get_text_intensity(text_lower)
    
    # Check for direct panic keywords to ensure model resilience (fallback guardrail)
    panic_words = ["kill myself", "suicide", "end my life", "gonna endup my life", "die soon"]
    if any(pw in text_lower for pw in panic_words):
        return [{"label": "Crisis", "confidence": 0.99, "intensity": "high"}]

    if emotion_model:
        # Use ML Model
        try:
            # Predict probability for confidence score
            probs = emotion_model.predict_proba([text])[0]
            max_prob_idx = probs.argmax()
            confidence = probs[max_prob_idx]
            label = emotion_model.classes_[max_prob_idx]
            
            # Map low confidence generic predictions to Neutral
            if confidence < 0.20:
                label = "Neutral"
                
            return [{"label": label, "confidence": float(confidence), "intensity": intensity}]
        except Exception as e:
            print(f"Emotion ML model prediction failed: {e}. Falling back to neutral.")
    
    # Fallback if model missing
    return [{"label": "Neutral", "confidence": 1.0, "intensity": "moderate"}]

