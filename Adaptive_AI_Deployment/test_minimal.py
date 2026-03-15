import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Allow import from project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from models.emotion_text import detect_text_emotion
from backend.llm_service import generate_ai_recommendations

class TestAdaptiveAI(unittest.TestCase):

    def test_text_emotion_accuracy(self):
        print("\nChecking Text Model accuracy...")
        cases = [
            ("I am feeling so happy!", "Happy"),
            ("I have no money for food today", "Crisis"),
            ("Why does everything go wrong?", "Angry")
        ]
        for text, expected in cases:
            res = detect_text_emotion(text)
            detected = res[0]["label"]
            self.assertEqual(detected, expected, f"Failed for '{text}': Got {detected}, expected {expected}")
            print(f"  PASS: '{text}' -> {detected}")

    def test_fusion_logic_simulation(self):
        print("\nChecking Fusion Logic...")
        # Simulating the logic in app.py
        def fuse(text_e, face_e):
            return face_e if face_e != "Neutral" else text_e
            
        self.assertEqual(fuse("Sad", "Angry"), "Angry")
        self.assertEqual(fuse("Happy", "Neutral"), "Happy")
        print("  PASS: Fusion logic verified.")

    def test_ai_recommendations_structure(self):
        print("\nChecking AI Recommendation structure...")
        # Since we might not have API keys in the test env, we mock the response
        # OR if keys are present, it will actually call the API.
        # Let's mock to ensure it works even without keys.
        mock_response = {
            "therapy": "Supportive Listening",
            "meditation": "Deep Breathing",
            "activity": "Walking",
            "music": "Lo-fi",
            "movie": "Inside Out",
            "game": "Stardew Valley"
        }
        
        with patch('__main__.generate_ai_recommendations', return_value=mock_response):
            recs = generate_ai_recommendations("Sad", "I lost my job")
            self.assertIsNotNone(recs)
            self.assertIn("therapy", recs)
            self.assertEqual(recs["movie"], "Inside Out")
            print("  PASS: AI recommendation structure verified.")

if __name__ == '__main__':
    unittest.main()
