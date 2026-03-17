import requests
import json
import time

url = "http://127.0.0.1:5000/analyze"

print("--- Testing Text Emotion Analysis ---")
data_text = {
    "text": "i am helpless right now . i gonna endup my life soon",
    "use_camera": False
}
try:
    response = requests.post(url, json=data_text, timeout=10)
    print(f"Status Code: {response.status_code}")
    res = response.json()
    print("Text Emotion:", res.get("text_emotion"))
    print("Final Emotion:", res.get("final_emotion"))
except Exception as e:
    print(f"Text Request failed: {e}")

print("\n--- Testing Face Emotion Analysis ---")
data_face = {
    "text": "I am looking at the camera.",
    "use_camera": True
}
try:
    response = requests.post(url, json=data_face, timeout=15)
    print(f"Status Code: {response.status_code}")
    res = response.json()
    print("Face Emotion:", res.get("face_emotion"))
    print("Final Emotion:", res.get("final_emotion"))
    print("Face Details Length:", len(str(res.get("face_details"))))
except Exception as e:
    print(f"Face Request failed: {e}")
