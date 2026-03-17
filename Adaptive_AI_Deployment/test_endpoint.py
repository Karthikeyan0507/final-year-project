import json
import sys
import os

sys.path.append(os.path.abspath("."))
from backend.app import app

def run_test():
    with app.test_client() as client:
        # Our primary test phrase that was failing
        payload = {
            "text": "i am helpless right now . i gonna endup my life soon ",
            "use_camera": False
        }
        
        print(f"Sending payload: {payload}")
        response = client.post('/analyze', json=payload)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print("\n--- ML Model Diagnostics ---")
            print(f"Detected Text Emotion: {data.get('text_emotion')}")
            print(f"Final Emotion: {data.get('final_emotion')}")
            
            print("\n--- Conversational Output (Empathetic Responder) ---")
            print(f"Final Declaration: {data.get('final_declaration')}")
            print(f"Conversational Response:\n{data.get('conversational_response')}")
            
            print("\n--- Recommendations (Therapy RL) ---")
            print(f"Therapy: {data.get('therapy')}")
            print(f"Activity: {data.get('activity')}")
        else:
            print(response.data)

if __name__ == "__main__":
    run_test()
