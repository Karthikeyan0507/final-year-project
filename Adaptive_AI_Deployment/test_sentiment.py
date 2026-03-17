import sys
import os

sys.path.append(os.path.abspath("."))
from models.emotion_text import detect_text_emotion

text = "i am helpless right now . i gonna endup my life soon "
result = detect_text_emotion(text)
print(f"Result for text: '{text}' -> {result}")

text2 = "help"
result2 = detect_text_emotion(text2)
print(f"Result for text: '{text2}' -> {result2}")
