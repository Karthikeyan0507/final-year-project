import requests
import json

url = "http://127.0.0.1:5000/analyze"
data = {
    "text": "I feel very sad and lonely today.",
    "use_camera": False
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")
