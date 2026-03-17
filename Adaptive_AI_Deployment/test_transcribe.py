import requests
import os

API_URL = "http://127.0.0.1:5000/transcribe"

def test_transcribe():
    # We need a sample wav file to test
    # If one doesn't exist, we can't test properly without a real file
    # But we can at least check if the endpoint is alive
    
    print("Testing /transcribe endpoint...")
    try:
        # Just a dummy request to check if it's there
        response = requests.post(API_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcribe()
