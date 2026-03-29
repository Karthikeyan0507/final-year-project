import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from models.empathetic_responder import generate_empathetic_response

def test_responder():
    test_cases = [
        "I am feeling very overwhelmed with work today.",
        "I just won a contest, I'm so happy!",
        "Everything is just okay, nothing much happening.",
        "I feel so lonely and sad lately."
    ]
    
    print("\n" + "="*50)
    print("TESTING HIGH-PERFORMANCE LLM RESPONDER")
    print("="*50)
    
    for text in test_cases:
        print(f"\nUser: {text}")
        response = generate_empathetic_response(
            text_emotion="Neutral",
            face_emotion="Neutral",
            final_emotion="Neutral",
            user_text=text,
            recommendations={},
            conversation_history=[]
        )
        ai_text = response.get("conversational_response")
        print(f"AI Response:\n{ai_text}")
        
        # Verify format
        if "Emotion:" in ai_text and "Response:" in ai_text:
            print("Status: [PASS] Format correct")
        else:
            print("Status: [FAIL] Format incorrect")

if __name__ == "__main__":
    test_responder()
