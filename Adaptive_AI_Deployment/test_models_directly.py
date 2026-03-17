import sys
import os
from pprint import pprint

# Allow import from project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

print("--- Testing Text Emotion Analysis ---")
try:
    from models.emotion_text import detect_text_emotion
    text1 = "I am feeling so overwhelmed and hopeless about my future."
    res1 = detect_text_emotion(text1)
    print(f"Result for '{text1}':")
    pprint(res1)
    print("\n")
    text2 = "Today was a fantastic day, I finally got the promotion!"
    res2 = detect_text_emotion(text2)
    print(f"Result for '{text2}':")
    pprint(res2)
except Exception as e:
    print(f"Failed to test text emotion: {e}")

print("\n--- Testing Face Emotion Analysis ---")
try:
    from models.emotion_face import detect_face_emotion
    face_emotion, face_details, processed_frame, face_features, feature_desc = detect_face_emotion()
    print(f"Detected Face Emotion: {face_emotion}")
    print(f"Face Features Description: {feature_desc}")
    print("Detailed Face Features:")
    pprint(face_features)
    print(f"Face Details Found: {bool(face_details)}")
    print(f"Processed Frame Returned: {bool(processed_frame)}")
except Exception as e:
    print(f"Failed to test face emotion: {e}")
