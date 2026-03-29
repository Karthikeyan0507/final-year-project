import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Allow import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from models.emotion_text import detect_text_emotion
from models.emotion_face import detect_face_emotion
from models.emotion_voice import detect_voice_emotion
from models.empathetic_responder import generate_empathetic_response
from models.conversation_context import get_session_memory
from rl_engine.therapy_rl import choose_therapy, update_recommendation_model
from backend.database import init_db, save_analysis, save_conversation_turn, get_conversation_history, get_previous_emotional_state, save_feedback
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Streamlit iframe

# Initialize database on startup
init_db()

# ── In-memory audio bridge ──────────────────────────────────────────────────
# Stores temporarily uploaded audio bytes keyed by session_id
_pending_audio_store: dict = {}

@app.route("/upload_audio", methods=["POST", "OPTIONS"])
def upload_audio():
    """Receives raw audio bytes POSTed by the embedded JS mic."""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    session_id = request.args.get("session_id", "default")
    _pending_audio_store[session_id] = request.data
    return jsonify({"status": "ok"}), 200

@app.route("/get_audio", methods=["GET"])
def get_audio():
    """Returns and clears the pending audio for a session."""
    session_id = request.args.get("session_id", "default")
    audio = _pending_audio_store.pop(session_id, None)
    if audio:
        import base64
        return jsonify({"audio_b64": base64.b64encode(audio).decode("utf-8")})
    return jsonify({"audio_b64": None})
# ────────────────────────────────────────────────────────────────────────────


# --- FEEDBACK ENDPOINT (RL) ---
@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Recieve user feedback (Thumbs Up/Down) for a specific recommendation.
    Update the RL model and save to history.
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        emotion = data.get("emotion")
        action = data.get("action") 
        reward = data.get("reward") # +1 or -1
        
        if not all([session_id, emotion, action, reward is not None]):
             return jsonify({"error": "Missing data fields"}), 400

        # Update the RL Model
        updated_category = update_recommendation_model(emotion, action, reward)
        
        # Save to DB
        save_feedback(session_id, emotion, action, reward)
        
        return jsonify({
            "status": "success", 
            "message": f"RL Model updated for {updated_category}."
        })
        
    except Exception as e:
        print(f"Feedback Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        use_camera = data.get("use_camera", False)
        session_id = data.get("session_id", str(uuid.uuid4()))  # Generate if not provided
        emergency_contact = data.get("emergency_contact", None)
        audio_data = data.get("audio_data", None)

        text_result = detect_text_emotion(text)
        text_emotion = text_result[0].get("label", "Neutral")
        emotion_intensity = text_result[0].get("intensity", "moderate")

        # Check if user wants facial analysis
        face_emotion = "Neutral"
        face_details = {}
        processed_frame = None
        face_features = {}
        feature_desc = ""
        
        if use_camera:
            try:
                face_emotion, face_details, processed_frame, face_features, feature_desc = detect_face_emotion()
            except Exception as e:
                print(f"Camera error: {e}")
                face_emotion = "Neutral"
                face_details = {}
                processed_frame = None
                face_features = {}
                feature_desc = "Camera error."

        # Check for voice emotion if audio data was provided
        voice_emotion = "Neutral"
        if audio_data:
            voice_emotion = detect_voice_emotion(audio_data)

        # Final emotion priority: Face > Voice > Text
        if face_emotion != "Neutral":
            final_emotion = face_emotion
        elif voice_emotion != "Neutral":
            final_emotion = voice_emotion
        else:
            final_emotion = text_emotion
        
        # --- EMOTION REFINEMENT LOGIC ---
        # Refine Face Emotion Labels
        refined_face_emotion = face_emotion
        ear = face_features.get("ear", 0.5)
        
        if face_emotion == "Fear":
            refined_face_emotion = "Nervous"
        elif face_emotion == "Happy" and ear > 0.32:
             refined_face_emotion = "Enjoying"
        elif face_emotion == "Sad":
            # Check for high intensity or physical cues of crying (e.g., very low EAR or specific mesh patterns if we had them)
            # For now, use intensity or low EAR as a proxy for "shut town" sadness
            if ear < 0.22 or emotion_intensity == "high":
                refined_face_emotion = "Crying"
        
        # Refine Text Emotion Labels (Simple Mapping)
        refined_text_emotion = text_emotion
        if text_emotion == "Anxious":
            refined_text_emotion = "Nervous"
            
        # Construct Final Declaration
        if refined_face_emotion == "Neutral" and refined_text_emotion == "Neutral":
             final_declaration = "You seem calm and balanced today."
        elif refined_face_emotion != "Neutral":
            final_declaration = f"You seem {refined_text_emotion.lower()}, and your face shows signs of being {refined_face_emotion.lower()}."
        else:
             final_declaration = f"I sense you are feeling {refined_text_emotion.lower()}."

        # --- EMOTION DELIVERY LOGIC (Priority Weightage System) ---
        emergency_notified = False
        simulated_message = ""
        
        # Calculate criticality score based on emotion level and weightage
        criticality_score = 0
        
        # 1. Immediate Crisis Keywords (Weight 4: Guaranteed Notification)
        crisis_keywords = [
            "suicide", "end my life", "kill myself", "want to die", 
            "give up on life", "no reason to live", "end up my life", 
            "end it all", "take my own life", "better off dead"
        ]
        if any(kw in text.lower() for kw in crisis_keywords):
            criticality_score += 4
            
        # 2. Critical Emotions (Weight 3)
        weight_3_emotions = ["Trauma", "Severe Stress", "Depression", "Crying"]
        if refined_text_emotion in weight_3_emotions or refined_face_emotion in weight_3_emotions:
            criticality_score += 3
            
        # 3. High Emotions (Weight 2)
        weight_2_emotions = ["Sadness", "Sad", "Fear", "Disgust"]
        if (refined_text_emotion in weight_2_emotions and emotion_intensity == "high") or refined_face_emotion in weight_2_emotions:
            criticality_score += 2
            
        # 4. Moderate Distress (Weight 1)
        if refined_text_emotion in ["Anxious", "Nervous"] and emotion_intensity == "high":
            criticality_score += 1
        
        # Trigger notification if score is >= 3 (Critical threshold)
        is_critical = criticality_score >= 3
        
        has_contact = emergency_contact and (emergency_contact.get("beloved_phone") or emergency_contact.get("beloved_email"))
        if is_critical and has_contact:
            rel = emergency_contact.get("relationship", "loved one")
            u_name = emergency_contact.get("user_name", "your " + rel)
            b_name = emergency_contact.get("beloved_name", "there")
            
            contact_email = emergency_contact.get("beloved_email", "")
            contact_phone = emergency_contact.get("beloved_phone", "")
            contact_number_or_email = contact_email if contact_email else contact_phone
            
            simulated_message = f"Hello {b_name}. I am LYKA, an AI companion. Your {rel} {u_name} is currently experiencing significant emotional distress (Priority Level: {criticality_score}). Please take a moment to reach out and care for them. Thank you."
            
            print("==================================================")
            print(f"🚨 [EMOTION DELIVERY TRIGGERED - SCORE {criticality_score}] 🚨")
            print(f"To: {contact_number_or_email}")
            print(f"Message: {simulated_message}")
            print("==================================================")
            
            # --- REAL NOTIFICATION DISPATCHER ---
            try:
                from backend.notifier import dispatch_notification
                dispatch_notification(contact_number_or_email, f"URGENT: LYKA Alert for {u_name}", simulated_message)
            except Exception as e:
                print(f"[DISPATCHER ERROR] Could not import/send via notifier: {e}")
                
            emergency_notified = True

        # Use the feature description from the model if available, otherwise fallback
        face_feature_desc = feature_desc if feature_desc else "No specific physical cues detected."

        # Get conversation context from session memory (NEEDED for AI recommendations)
        session_memory = get_session_memory(session_id)
        conversation_context = session_memory.get_context_for_response()
        
        # Get explicit conversation history (last 20 turns)
        recent_history = session_memory.get_recent_exchanges(20)

        # -------------------------------------------------------------------
        # ML THERAPY RECOMMENDATION ENGINE
        # Fuses Text, Voice, and Face features to calculate optimal therapy
        # -------------------------------------------------------------------
        print(f"[RECS] Engaging Unified Therapy ML Model for T:{text_emotion} V:{voice_emotion} F:{face_emotion}")
        recommendations = choose_therapy(
            text_emotion=text_emotion,
            voice_emotion=voice_emotion,
            face_emotion=face_emotion,
            face_features=face_features
        )

        # Get historical emotional state (long-term memory)
        historical_context = get_previous_emotional_state(session_id)

        # Generate empathetic conversational response with context
        empathetic_response = generate_empathetic_response(
            text_emotion=text_emotion,
            face_emotion=face_emotion,
            final_emotion=final_emotion,
            user_text=text,
            recommendations=recommendations,
            context=conversation_context,
            historical_context=historical_context,
            conversation_history=recent_history
        )
        
        ai_response = empathetic_response.get("conversational_response")
        
        # Parse official emotion from LLM if provided in the strict format
        if ai_response and "Emotion:" in ai_response:
            try:
                llm_lines = ai_response.split('\n')
                parsed_emotion = None
                parsed_message_lines = []
                capture_response = False
                
                for line in llm_lines:
                    if line.startswith("Emotion:"):
                        trimmed_emotion = line.replace("Emotion:", "").strip()
                        if trimmed_emotion in ["Happy", "Calm", "Neutral", "Sad", "Stressed", "Angry", "Anxious"]:
                            parsed_emotion = trimmed_emotion
                    elif line.startswith("Response:"):
                        capture_response = True
                        parsed_message_lines.append(line.replace("Response:", "").strip())
                    elif capture_response:
                        parsed_message_lines.append(line.strip())
                
                if parsed_emotion:
                    final_emotion = parsed_emotion
                if parsed_message_lines:
                    ai_response = "\n".join(parsed_message_lines).strip()
            except Exception as e:
                print(f"Error parsing LLM emotion: {e}")
        
        # Save conversation turn to memory and database
        session_memory.add_exchange(
            user_text=text,
            ai_response=ai_response,
            emotion=final_emotion,
            emotion_intensity=emotion_intensity
        )
        
        save_conversation_turn(
            session_id=session_id,
            user_text=text,
            ai_response=ai_response,
            emotion=final_emotion,
            emotion_intensity=emotion_intensity
        )

        # Save to analysis history (existing functionality)
        save_analysis(
            text_input=text,
            text_emotion=text_emotion,
            face_emotion=face_emotion,
            final_emotion=final_emotion,
            recs=recommendations
        )

        return jsonify({
            "session_id": session_id,  # Return session ID for client to maintain
            "text_emotion": refined_text_emotion,
            "face_emotion": refined_face_emotion,
            "voice_emotion": voice_emotion,
            "final_declaration": final_declaration,
            "face_details": face_details,
            "processed_frame": processed_frame,
            "face_feature_desc": face_feature_desc,
            "final_emotion": final_emotion,
            "emotion_intensity": emotion_intensity,
            "therapy": recommendations.get("therapy"),
            "meditation": recommendations.get("meditation"),
            "activity": recommendations.get("activity"),
            "music": recommendations.get("music"),
            "movie": recommendations.get("movie"),
            "game": recommendations.get("game"),
            "documentary": recommendations.get("documentary"),
            # New conversational fields
            "conversational_response": ai_response,
            "follow_up_suggestions": empathetic_response.get("follow_up_suggestions", []),
            "emergency_notified": emergency_notified,
            "simulated_message": simulated_message,
            # Context information
            "conversation_context": {
                "relationship_stage": conversation_context.get("relationship_stage"),
                "emotion_trend": conversation_context.get("emotion_trend"),
                "total_turns": conversation_context.get("total_turns")
            }
        })

    except Exception as e:
        print("Error processing request:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500




from backend.llm_service import transcribe_audio
from backend.tts_service import speak_text
import tempfile
import io
from flask import send_file

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        # Save temp file with the actual file extension
        import os
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".webm" # default to webm if missing
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
            file.save(temp.name)
            temp_path = temp.name
            
        # Transcribe
        text = transcribe_audio(temp_path)
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass
        
        if text:
            return jsonify({"text": text})
        else:
            return jsonify({"error": "Transcription failed"}), 500
            
    except Exception as e:
        print(f"Transcription Endpoint Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/tts", methods=["POST"])
def tts_endpoint():
    try:
        data = request.json
        text = data.get("text")
        lang = data.get("lang", "en") # Default to english
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        audio_bytes = speak_text(text, lang)
        
        if audio_bytes:
            return send_file(
                io.BytesIO(audio_bytes),
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name="output.mp3"
            )
        else:
            return jsonify({"error": "TTS failed"}), 500
            
    except Exception as e:
        print(f"TTS Endpoint Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # LOCAL RUN ONLY
    app.run(debug=True, use_reloader=False)
