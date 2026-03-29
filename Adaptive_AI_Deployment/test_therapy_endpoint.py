import requests
import time

URL = "http://127.0.0.1:5000/analyze"

data = {
    "text": "I feel so completely alone and isolated right now... no one understands.",
    "session_id": "test_unified_pipeline"
}

def test():
    try:
        print("[TEST] Hitting unified /analyze endpoint with JSON...")
        resp = requests.post(URL, json=data, timeout=30)
        res_json = resp.json()
        
        print(f"Status: {resp.status_code}")
        print("-" * 50)
        print("Final Declaration:", res_json.get("final_declaration", ""))
        
        recs = res_json.get("recommendations", {}) # Note: In my app.py, I return fields directly
        # Wait, let me check my app.py again to see how I return them
        
        print("--- Therapy ML Output (Multimodal Fusion) ---")
        print(f"Therapy Mode:  {res_json.get('therapy')}")
        print(f"Activity:      {res_json.get('activity')}")
        print(f"Meditation:    {res_json.get('meditation')}")
        print(f"Game:          {res_json.get('game')}")
        print(f"Documentary:   {res_json.get('documentary')}")
        print(f"AI Response:   {res_json.get('conversational_response')}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    time.sleep(2) # Give backend a second to register routes
    test()
