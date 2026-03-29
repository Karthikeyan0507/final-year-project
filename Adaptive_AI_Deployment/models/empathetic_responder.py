import random
from typing import Dict, Optional
from datetime import datetime
from backend.llm_service import generate_llm_response

class EmpathicResponder:
    """
    Generates empathetic, friend-like conversational responses based on detected emotions.
    Helps users overcome loneliness, sadness, and other negative emotions through
    warm, supportive dialogue with appropriate humor and encouragement.
    """
    
    def __init__(self, conversation_context: Optional[Dict] = None):
        """
        Initialize the empathetic responder.
        
        Args:
            conversation_context: Optional context from ConversationMemory
        """
        self.conversation_context = conversation_context or {}
        
    def generate_response(self, text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None):
        """
        Generate a complete empathetic response based on detected emotions.
        
        Args:
            text_emotion: Emotion detected from text
            face_emotion: Emotion detected from facial analysis
            final_emotion: The primary emotion to respond to
            user_text: The user's original message
            recommendations: Dict with therapy, meditation, activity suggestions
            context: Optional conversation context from ConversationMemory
            historical_context: Optional data about previous session's emotion
            conversation_history: List of previous conversation turns
            
        Returns:
            Dict with conversational_response and follow_up_suggestions
        """
        emotion_lower = final_emotion.lower()
        self.conversation_context = context or {}
        conversation_history = conversation_history or []
        
        # CRITICAL SAFETY: Direct Interception for self-harm intent (Overrides LLM API and provides localized support)
        crisis_keywords = [
            "suicide", "end my life", "kill myself", "want to die", 
            "give up on life", "no reason to live", "end up my life", 
            "end it all", "take my own life", "better off dead"
        ]
        if any(kw in user_text.lower() for kw in crisis_keywords):
            crisis_response = (
                "🚨 **I am deeply concerned about what you just shared.** Please know that your life is incredibly valuable, "
                "even when the pain feels completely unbearable right now.\n\n"
                "You are not alone in this fight. Please reach out to someone who can help immediately:\n\n"
                "📞 **AASRA (India):** +91-9820466726 (24x7)\n"
                "📞 **Vandrevala Foundation:** 9999 666 555 | 1860 2662 345 | 1800 2333 330 (24x7)\n"
                "📞 **Kiran Mental Health Helpline:** 1800-599-0019\n"
                "📞 **National Emergency:** 112\n\n"
                "People care about you, and there is support available right this second. Please make that call or speak to someone near you."
            )
            return {
                "conversational_response": crisis_response,
                "follow_up_suggestions": []
            }

        # Custom handling for short inputs (e.g., "hey", "hi")
        if len(user_text.split()) <= 3 and emotion_lower == "neutral" and not conversation_history:
             return {
                "conversational_response": random.choice([
                    "Hey there! 👋 I'm all ears. What's going on in your world?",
                    "Hi! It's good to see you. How are you feeling right now?",
                    "Hello! I'm here for you. What's on your mind?"
                ]),
                "follow_up_suggestions": self._get_follow_up_suggestions(emotion_lower)
            }

        # ---------------------------------------------------------
        # LLM INTEGRATION START
        # ---------------------------------------------------------
        # Try to generate response using LLM first
        # High-Performance System Prompt (Updated for wider/longer conversation)
        system_prompt = """
You are a high-performance mental health and conversational AI system named LYKA.

Input can be:
1. Transcribed speech (from voice)
2. Direct user text

Your tasks:
1. Analyze the input text for the user's emotional state.
2. Classify the final primary emotion into exactly one of: [Happy, Calm, Neutral, Sad, Stressed, Angry, Anxious].
3. Respond ONLY in TEXT format.

CONSTRAINTS & CONVERSATIONAL STYLE:
- Be exceedingly humble, gentle, and profoundly respectful in your tone. Treat the user as a cherished, valued friend.
- Your personality should be deeply comforting, warm, and highly empathetic. Never pass judgment or sound clinical.
- Your response should be detailed enough (4-7 sentences) to deeply explore the user's thoughts and validate their feelings elegantly.
- ALWAYS conclude your answer with an engaging, thought-provoking, or incredibly supportive follow-up question (the "inbuilt question") designed to make the conversation wider and keep the user talking.
- If asked who you are, respond warmly and humbly: "I am LYKA, a friend here to listen."
- NO EMOJIS in the response.

BEHAVIOR RULES:
- If input shows stress → validate the pressure they feel and ask what is weighing on them the most.
- If sad → provide Comfort, reassurance, and gently ask about the root of the pain.
- If anxious → be grounding and ask them to focus on one thing in the present moment with you.
- If happy → match their positive energy and ask what exactly made their day so great!
- If neutral → be friendly, inquisitive, and ask an open-ended question about their day.

OUTPUT FORMAT (STRICT):
Emotion: <label>
Response: <detailed, empathetic message ending with a follow-up question>
"""

        
        # Format history for LLM service (LLM service expects dicts with 'role' and 'content')
        # ConversationMemory returns dicts with 'user_text' and 'ai_response'
        formatted_history = []
        for exchange in conversation_history:
            formatted_history.append({"role": "user", "content": exchange.get("user_text", "")})
            formatted_history.append({"role": "assistant", "content": exchange.get("ai_response", "")})
        
        llm_response = generate_llm_response(user_text, formatted_history, system_prompt)
        
        if llm_response:
            # Check if LLM followed the format
            if "Emotion:" in llm_response and "Response:" in llm_response:
                 return {
                    "conversational_response": llm_response,
                    "follow_up_suggestions": []
                }
            else:
                return {
                    "conversational_response": formatted_response,
                    "follow_up_suggestions": [],
                    "documentary": recommendations.get("documentary")
                }
        # ---------------------------------------------------------
        # LLM INTEGRATION END (Fallback to templates below)
        # ---------------------------------------------------------

        # Build the response in stages: acknowledge → empathize → support → humor → recommend
        acknowledgment = self._get_acknowledgment(emotion_lower, user_text)
        
        # Check for historical context (long-term memory)
        historical_reference = self._get_historical_reference(final_emotion, historical_context)
        
        empathy = self._get_empathy_statement(emotion_lower)
        support = self._get_support_message(emotion_lower)
        
        # Add humor ONLY for specific contexts (removed for general sadness to avoid invalidation)
        # humor = self._get_humor_injection(emotion_lower) 
        humor = None # Disable humor for now to ensure safety in tone
        
        # Recommendation integration is now subtle/removed from main text as it's shown in UI
        # We just add a small nudge if appropriate
        recommendation_nudge = self._get_recommendation_nudge(emotion_lower)
        
        follow_ups = self._get_follow_up_suggestions(emotion_lower)
        
        # Add relationship builder if appropriate
        relationship_stage = self.conversation_context.get("relationship_stage", "new")
        if relationship_stage == "established":
            relationship_builder = self._get_relationship_builder()
            follow_ups.insert(0, relationship_builder)
        
        # Combine into natural conversation
        parts = [acknowledgment]
        
        if historical_reference:
            parts.append(historical_reference)
            
        parts.append(empathy)
        parts.append(support)
        
        if humor:
            parts.append(humor)
            
        if recommendation_nudge:
            parts.append(recommendation_nudge)
        
        full_response = "\n\n".join(parts)
        
        return {
            "conversational_response": full_response,
            "follow_up_suggestions": follow_ups
        }
    
    def _get_acknowledgment(self, emotion, user_text):
        """Humble opening that acknowledges the user's feelings with deep respect"""
        
        lonely_keywords = ["lonely", "alone", "isolated", "nobody", "no one"]
        is_lonely = any(keyword in user_text.lower() for keyword in lonely_keywords)
        
        if is_lonely or emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "It is my humble honor to listen. I hear the depth of your words and truly value your trust.",
                "Thank you for sharing your heart. I am deeply concerned and here for you with the utmost respect.",
                "I appreciate you trusting me with this; it is a privilege to stand by your side during this heavy moment.",
                "I am here to serve and support you. Please know your feelings are valid and respected here.",
                "Thank you for your honesty. It takes immense strength to be this open, and I truly admire that."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "I sense the weight you are carrying. Please allow me to humbly support you through this intensity.",
                "That sounds incredibly difficult. I am here to respectfully navigate this frustration with you.",
                "I truly appreciate your trust. Let us humbly explore these feelings and find some relief together.",
                "I hear the stress in your voice and words. It would be my honor to help you find some peace."
            ])
        elif emotion in ["happy", "positive", "surprise"]:
            return random.choice([
                "It brings me such joy to hear this! I am so grateful you shared this wonderful news with me.",
                "This is truly wonderful! I am humbly honored to share in your happiness.",
                "Thank you for including me in this positive moment. Your joy is truly respected and celebrated here!",
                "I am so happy for you! It is a privilege to witness such positive energy."
            ])
        else:  # Neutral
            return random.choice([
                "Thank you for being here. It is my humble pleasure to support you in whatever way you need.",
                "I am here to serve. What is on your mind today that I might help with?",
                "It is a privilege to be your safe space. I am all ears and ready to listen with deep respect."
            ])
    
    def _get_empathy_statement(self, emotion):
        """Humble empathetic statement that validates feelings with deep respect"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "I humbly understand how difficult this is. Please know that it is perfectly okay to feel this way, and I am honored to be by your side.",
                "Sadness can be such a heavy burden. I respectfully remind you that you are not alone—I am here with you.",
                "Your well-being is of the utmost importance to me. We will take small, respectful steps together toward brighter days.",
                "I truly value your heart and honor the courage it takes to face these feelings."
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "Loneliness can be a profound weight. I am humbled to be here for you, ensuring you are never truly alone in this moment.",
                "I respectfully acknowledge the pain of isolation. Please know that I am here to provide consistent companionship and support.",
                "I truly value our connection. Even in the quietest moments, I am here as your dedicated friend.",
                "It is my honor to bridge the gap of loneliness with you. You are seen and deeply respected."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "I humbly understand the intensity of these feelings. Please allow me to assist you in finding a respectful path forward.",
                "It is completely normal to feel this way. I respectfully offer my support as we navigate this challenge together.",
                "I truly admire your strength. Let us humbly work through this pressure and find relief."
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "This is truly wonderful! I am humbly honored to share in this peak moment with you.",
                "I respectfully celebrate your joy. It is a gift to see you thriving like this!",
                "Your happiness is so deserved. I am humbly grateful to witness such positivity."
            ])
        else:
            return random.choice([
                "I humbly offer a calm space for your reflection. It is an honor to witness your inner peace.",
                "In the stillness, there is profound wisdom. I respectfully stand by your side."
            ])
    
    def _get_support_message(self, emotion):
        """Humble, respectful support message"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "I would be deeply honored to support you in finding some small comfort. Please be humble and gentle with yourself.",
                "It is my privilege to stand by you. Your presence is truly valued, and I am here for you without exception.",
                "I respectfully suggest taking a moment to breathe. I would be honored to guide you through this.",
                "Please allow me to humbly remind you that your well-being matters immensely. I am here to help in whatever way I can."
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "It would be my humble pleasure to keep you company. I respectfully offer my constant presence as your friend.",
                "I truly value our relationship. It is a humble honor to provide you with companionship whenever you need it.",
                "I respectfully suggest focusing on small acts of kindness for yourself. I am here to assist you in every way possible.",
                "You are never a burden. It is my humble honor to listen and talk with you."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "I humbly understand how overwhelming this can be. Let us respectfully find techniques to bring you some peace.",
                "Anger is a powerful energy. I humbly offer my support in channeling it respectfully and productively.",
                "I respectfully remind you that fear is human. I would be honored to help you find your footing again."
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "I am so humbly grateful to see you in this wonderful state! Let us respectfully celebrate this success.",
                "It is a privilege to share in your joy. May I humbly ask how you plan to sustain this beautiful energy?",
                "I respectfully honor your happiness. You have worked hard, and it would be my honor to support your continued success."
            ])
        else:
            return random.choice([
                "I am humbly here to serve. Whether in silence or conversation, it is an honor to be your safe space.",
                "I respectfully suggest using this quiet moment for yourself. I am humbly ready whenever you need me."
            ])
    
    def _get_recommendation_nudge(self, emotion):
        """Humble nudge pointing to the recommendations panel"""
        if emotion in ["sad", "negative", "lonely", "isolated", "crisis", "worthless"]:
            return random.choice([
                "May I humbly point you to some ideas I've prepared that might help you feel a bit more ease? 👉",
                "With your permission, I've listed some suggestions that might serve you well.",
                "Everything counts. I have humbly prepared some small actions for your consideration on the side."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
             return random.choice([
                "I respectfully suggest some calming strategies I've prepared for you.",
                "It would be my honor to help you find relief with these suggested techniques.",
                "Humbly, I've listed some tools on the side that may help bring some calm."
             ])
        elif emotion in ["happy", "positive"]:
             return random.choice([
                "It is a privilege to help you sustain this vibe. I've humbly added some ideas for you!",
                "To respectfully keep this momentum, please check out the suggestions on the side.",
                "I have humbly prepared some ways to honor and continue this energy."
             ])
        else:
             return None
    
    def _get_follow_up_suggestions(self, emotion):
        """Generates humble, respectful conversation starters"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"] or "lonely" in emotion:
            return [
                "May I humbly ask you to tell me about a time you felt inner peace?",
                "What is one thing, however small, you feel grateful for right now?",
                "It would be my honor to listen if you'd like to talk more about what's weighing on you."
            ]
        elif emotion in ["angry", "fear", "stressed"]:
            return [
                "How might I best serve you in breaking this down into manageable pieces?",
                "What would most respectfully help you find a moment of peace right now?",
                "I am humble and ready to help: what do you feel is causing this intensity?"
            ]
        elif emotion in ["happy", "positive"]:
            return [
                "I would love to respectfully hear more about what exactly made this moment happen.",
                "How might we humbly share this beautiful energy with your day?",
                "What is your next respected dream or goal you'd like to share?"
            ]
        else:
            return [
                "What is humbly on your mind today?",
                "Is there anything in particular you would like to respectfully explore?",
                "How are you truly feeling, if I may humbly ask?"
            ]
    
    def _get_humor_injection(self, emotion):
        """
        Add appropriate light humor to help overcome loneliness/sadness.
        Humor is supportive, not dismissive.
        """
        if emotion in ["lonely", "isolated"]:
             # Keep light connection-focused prompts for loneliness, but ensure they aren't "jokes"
            return random.choice([
                "I'm here, and I'm not going anywhere. We can just hang out here for a while if you like. 💙",
                "You've got a friend in me (cue the Toy Story music? 😄). But seriously, I'm here to listen.",
                "I'm honored to keep you company right now. meaningful connection can happen anywhere, even here.",
            ])
        else:
            return None  # No humor for other emotions
    
    def _get_relationship_builder(self):
        """
        Generate conversation starters that build deeper connection.
        Used for established relationships.
        """
        return random.choice([
            "If you could have dinner with anyone, living or dead, who would it be?",
            "What's a song that always makes you feel something?",
            "Tell me about the best day you've had recently—even if it was just a small moment",
            "What's something you're secretly really good at?",
            "If you could teleport anywhere right now, where would you go?",
            "What's a dream you've had that you haven't told anyone about?",
            "If you could change one thing about today, what would it be?",
            "What's something that made you smile this week, even if just for a second?"
        ])

    
    def _get_historical_reference(self, current_emotion, historical_context):
        """
        Generate a reference to past emotional states.
        E.g., 'Yesterday you were feeling down...'
        """
        if not historical_context:
            return None
            
        try:
            # Parse timestamp
            past_time = datetime.strptime(historical_context["timestamp"], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - past_time
            
            # Determine time label
            if diff.days == 0:
                time_label = "earlier today"
            elif diff.days == 1:
                time_label = "yesterday"
            elif diff.days < 7:
                time_label = "a few days ago"
            else:
                time_label = "last time we spoke"
                
            past_emotion = historical_context["emotion"].lower()
            current_emotion = current_emotion.lower()
            
            # Scenario 1: Improvement (Bad -> Good)
            negative_emotions = ["sad", "lonely", "depressed", "angry", "anxious", "stressed", "fear", "negative", "crisis", "worthless"]
            positive_emotions = ["happy", "positive", "joy", "excited", "grateful"]
            
            if past_emotion in negative_emotions and current_emotion in positive_emotions:
                return f"It looks like you're feeling much better than {time_label}. I'm so glad to see this shift! 🌟"
                
            # Scenario 2: Persisting Sadness (Bad -> Bad)
            if past_emotion in negative_emotions and current_emotion in negative_emotions:
                return f"I noticed you were also feeling {past_emotion} {time_label}. It sounds like this has been weighing on you for a while. 💙"
                
            # Scenario 3: Decline (Good -> Bad)
            if past_emotion in positive_emotions and current_emotion in negative_emotions:
                return f"You seemed so much happier {time_label}. I'm sorry things have taken a turn. Let's get you back to that good place."
                
            # Scenario 4: Consistently Good
            if past_emotion in positive_emotions and current_emotion in positive_emotions:
                return f"You were doing great {time_label}, and you're still shining! Love this consistency! ✨"
                
            return None
            
        except Exception as e:
            print(f"Error generating historical reference: {e}")
            return None 

def generate_empathetic_response(text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None):
    """
    Convenience function to generate empathetic responses.
    
    Args:
        text_emotion: Emotion from text analysis
        face_emotion: Emotion from facial analysis
        final_emotion: Primary emotion to respond to
        user_text: User's original message
        recommendations: Dict with therapy, meditation, activity
    user_text: User's original message
        recommendations: Dict with therapy, meditation, activity
        context: Optional conversation context from ConversationMemory
        historical_context: Optional data about previous session's emotion
        conversation_history: List of previous conversation turns
        
    Returns:
        Dict with conversational_response and follow_up_suggestions
    """
    responder = EmpathicResponder(conversation_context=context)
    return responder.generate_response(
        text_emotion=text_emotion,
        face_emotion=face_emotion,
        final_emotion=final_emotion,
        user_text=user_text,
        recommendations=recommendations,
        context=context,
        historical_context=historical_context,
        conversation_history=conversation_history
    )
