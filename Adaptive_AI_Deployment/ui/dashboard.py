import sys
import os
import time
import streamlit as st
import requests

# =====================================================
# PROJECT PATH FIX
# =====================================================
import uuid
import json

# =====================================================
# PROJECT PATH FIX
# =====================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# CONFIGURATION
# =====================================================
API_URL = "http://127.0.0.1:5000/analyze"
API_BASE_URL = "http://127.0.0.1:5000"
SESSION_FILE = "user_session.json"

def get_persistent_session_id():
    """Load or create a persistent session ID."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("session_id", str(uuid.uuid4()))
        except:
            pass
            
    new_id = str(uuid.uuid4())
    with open(SESSION_FILE, "w") as f:
        json.dump({"session_id": new_id}, f)
    return new_id

# Initialize Session
if "user_session_id" not in st.session_state:
    st.session_state.user_session_id = get_persistent_session_id()


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="LYKA AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS (Glassmorphism & Modern UI)
# =====================================================
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background with premium Midnight Serenity animated gradient */
    .stApp {
        background: linear-gradient(-45deg, #020617, #1e1b4b, #312e81, #5b21b6);
        background-size: 400% 400%;
        animation: gradient 20s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Containers - Improved for Serenity */
    .glass-container {
        background: rgba(15, 23, 42, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 0 10px rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2.2rem;
        margin-bottom: 2rem;
    }

    /* Section Headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        line-height: 1.2;
    }
    
    h1 {
        letter-spacing: -0.02em;
    }
    
    p, label {
        color: #94a3b8;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Input Area */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #f8fafc;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4);
        border-color: transparent;
    }

    /* Result Cards - Enhanced Visual Depth */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 20px;
        padding: 1.8rem;
        text-align: center;
        box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(30, 41, 59, 0.7);
        border-color: #818cf8;
        box-shadow: 0 20px 40px -12px rgba(99, 102, 241, 0.3);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.01em;
    }

    /* Therapy Recommendation */
    .therapy-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 24px;
        text-align: center;
        color: #f8fafc;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
        margin-top: 1.5rem;
        animation: fadeIn 1s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .therapy-title {
        font-size: 1.1rem;
        color: #6366f1;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
    }
    .therapy-content {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: #475569;
        font-size: 0.9rem;
    }

    /* WhatsApp Style Chat Bubbles */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 1rem;
    }
    .user-row {
        justify-content: flex-end;
    }
    .ai-row {
        justify-content: flex-start;
    }
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 18px;
        max-width: 75%;
        color: #f1f5f9;
        font-size: 1.05rem;
        line-height: 1.55;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .user-bubble {
        background-color: #005c4b; /* WhatsApp Dark Green */
        border-top-right-radius: 0;
        text-align: left; /* Text inside is typically left aligned even if bubble is right */
    }
    .ai-bubble {
        background-color: #202c33; /* WhatsApp Dark Grey */
        border-top-left-radius: 0;
    }

    /* --- WhatsApp Style UI Integration --- */
    
    /* Force transparency on the layout containers to remove the white 'card' boxes */
    div[data-testid="stHorizontalBlock"]:has(input[placeholder="Message"]), 
    div[data-testid="stColumn"], 
    div[class*="stElementContainer"] {
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Style the dark rounded bar for the message input */
    div[data-testid="stTextInput"] {
        background-color: #2a3942 !important; 
        border-radius: 25px !important;
        padding: 0 15px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Hide internal Streamlit shadows/backgrounds */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
    }

    div[data-testid="stTextInput"] input {
        color: #e9edef !important;
        font-size: 16px !important;
    }

    /* Green Mic Button */
    div[data-testid="stAudioInput"] button {
        border-radius: 50% !important;
        width: 52px !important;
        height: 52px !important;
        min-width: 52px !important;
        background-color: #00a884 !important; 
        color: white !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white' width='28px' height='28px'%3E%3Cpath d='M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z'/%3E%3Cpath d='M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 26px 26px !important;
        color: transparent !important;
    }

    /* Hide other Streamlit elements in mic area */
    div[data-testid="stAudioInput"] label,
    div[data-testid="stAudioInput"] svg,
    div[data-testid="stAudioInput"] [role="toolbar"],
    div[data-testid="stAudioInput"] [class*="Waveform"] {
        display: none !important;
    }
</style>





""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png" width="80" style="filter: hue-rotate(240deg) brightness(1.2);">
        <h2 style="color: #f8fafc; margin-top: 1rem;">LYKA AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Interaction Mode Switcher
    st.subheader("🎭 Interaction Mode")
    interaction_mode = st.radio(
        "Choose your experience:",
        ["Wholesome Conversation", "Therapy Recommendations"],
        index=0,
        help="Switch between chat-focused or recommendation-focused views.",
        key="interaction_mode"
    )
    
    st.markdown("---")

    st.header("⚙️ Settings")
    
    # Camera only available in Therapy Mode
    if interaction_mode == "Therapy Recommendations":
        use_camera = st.checkbox("Enable Facial Analysis", value=True, help="Uses your webcam to analyze facial expressions")
    else:
        use_camera = False

    # Audio Input (Removed from Sidebar)
    audio_value = None

    st.markdown("---")
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.latest_analysis = {}
        st.rerun()

    st.markdown("---")
    st.caption("© 2026 LYKA AI")

    # Sidebar Wellness Panel (Always shows latest results)
    if "latest_analysis" in st.session_state and st.session_state.latest_analysis:
        st.markdown("---")
        st.markdown("### 🧘 Latest Wellness Insights")
        data = st.session_state.latest_analysis
        
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <p style="margin-bottom: 0.2rem; font-size: 0.8rem; color: #818cf8; text-transform: uppercase; font-weight: 700;">Overall State</p>
            <h4 style="margin: 0; color: #f8fafc;">{data.get('final_emotion', 'N/A')}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Suggestion:** {data.get('therapy')}")
        
        with st.expander("More details"):
            st.write(f"**Text:** {data.get('text_emotion')}")
            st.write(f"**Face:** {data.get('face_emotion')}")
            if data.get('face_feature_desc'):
                st.info(data.get('face_feature_desc'))

# =====================================================
# MAIN CONTENT
# =====================================================

# =====================================================
# RENDER FUNCTIONS
# =====================================================

def render_chat_interface():
    """Renders the WhatsApp-style split chat UI"""
    
    # Add a spacer at the bottom of the chat to make room for the fixed input bar
    st.markdown('<div style="margin-bottom: 80px;"></div>', unsafe_allow_html=True)
    
    # Display Chat History with Custom Bubbles
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-row user-row">
                <div class="chat-bubble user-bubble">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-row ai-row">
                <div class="chat-bubble ai-bubble">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # WhatsApp-style Bottom Input Bar
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    user_input = None
    
    # Simple Layout: [ Dark Bar Input ] [ Mic Circle ]
    col_input, col_mic = st.columns([6, 1])
    
    with col_input:
        # Define callback to handle text submission and clear input
        def on_msg_submit():
            if st.session_state.temp_chat_input:
                st.session_state.chat_input_final = st.session_state.temp_chat_input
                st.session_state.temp_chat_input = "" # Clear it

        # Single text input with no label, acting as the bar itself
        st.text_input(
            "Message",
            key="temp_chat_input",
            placeholder="Message",
            label_visibility="collapsed",
            on_change=on_msg_submit
        )
        
        # Check if we have a final submission from the callback
        if st.session_state.get("chat_input_final"):
            user_input = st.session_state.chat_input_final
            st.session_state.chat_input_final = None # Reset for next turn

    with col_mic:
        # Mic logic with dynamic reset
        if "mic_reset_counter" not in st.session_state:
            st.session_state.mic_reset_counter = 0

        chat_audio = st.audio_input(
            "Record", 
            label_visibility="collapsed", 
            key=f"chat_mic_final_{st.session_state.mic_reset_counter}"
        )
        
        if chat_audio and chat_audio != st.session_state.get("last_chat_audio"):
            st.session_state.last_chat_audio = chat_audio
            st.session_state.pending_audio = chat_audio
            st.session_state.mic_reset_counter += 1
            st.rerun()
            
    return user_input

def render_therapy_interface():
    """Renders the new Therapy Session Dashboard UI"""
    
    st.markdown("## 🛋️ Therapy Session Check-In")
    
    # Top Section: Input
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.4); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 2rem;">
        <h4 style="margin-top:0; color: #94a3b8; font-weight: 500;">How are you feeling right now?</h4>
    </div>
    """, unsafe_allow_html=True)

    # Input Row (Text & Voice)
    col1, col_mic, col_btn = st.columns([4, 1, 1.2])
    with col1:
        def submit_therapy_text():
            st.session_state.prompt_input = st.session_state.therapy_input
            st.session_state.therapy_input = ""
            
        st.text_input(
            "Share your thoughts...", 
            key="therapy_input", 
            on_change=submit_therapy_text,
            label_visibility="collapsed",
            placeholder="I'm feeling..."
        )
    
    with col_mic:
        therapy_audio = st.audio_input("Record", label_visibility="collapsed", key=f"therapy_mic_{st.session_state.get('mic_reset_counter', 0)}")
        if therapy_audio and therapy_audio != st.session_state.get("last_therapy_audio"):
            st.session_state.last_therapy_audio = therapy_audio
            st.session_state.pending_audio = therapy_audio
            st.session_state.mic_reset_counter = st.session_state.get('mic_reset_counter', 0) + 1
            st.rerun()

    with col_btn:
        if st.button("Analyze", use_container_width=True):
            submit_therapy_text()

    if use_camera:
        st.caption("📷 Facial Analysis Active")

    # Results Section - Only verify if we have a LATEST analysis that matches the current session interaction
    # For now, we just show the latest analysis if it exists
    if st.session_state.latest_analysis:
        data = st.session_state.latest_analysis
        
        # Face Tracking Dashboard (New Feature)
        if data.get("processed_frame"):
            with st.expander("👁️ Face Tracking Dashboard (Golden Ratio Analysis)", expanded=True):
                col_video, col_info = st.columns([2, 1])
                with col_video:
                    # Decode base64 image
                    import base64
                    try:
                        img_bytes = base64.b64decode(data["processed_frame"])
                        st.image(img_bytes, caption="Live Facial Analysis & Golden Ratio", use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not display face tracking: {e}")
                
                with col_info:
                    st.markdown("### Analysis Details")
                    st.markdown(f"**Emotion:** {data.get('final_emotion', 'N/A')}")
                    st.markdown(f"**Description:** {data.get('face_feature_desc', 'No details')}")
                    st.caption("The golden lines represent aesthetic geometric ratios used for facial symmetry analysis.")

        st.markdown("---")
        st.subheader("💡 Analysis & Insights")
        
        # 0. Final Declaration (Hero Section)
        final_decl = data.get('final_declaration', f"You seem {data.get('text_emotion', 'neutral')} and your face looks {data.get('face_emotion', 'neutral')}.")
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%); 
                    border-left: 5px solid #818cf8; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #e2e8f0; font-weight: 300; font-style: italic;">"{final_decl}"</h3>
        </div>
        """, unsafe_allow_html=True)

        # 1. Detailed Analytics (Split View)
        col_text, col_face = st.columns(2)
        
        with col_text:
            text_emo = data.get('text_emotion', 'Neutral')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="color: #94a3b8;">📝 Text Analysis</div>
                <div class="metric-value" style="color: #fca5a5;">{text_emo}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">Based on your words</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_face:
            face_emo = data.get('face_emotion', 'Neutral')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="color: #94a3b8;">😶 Face Analysis</div>
                <div class="metric-value" style="color: #93c5fd;">{face_emo}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">Based on expressions</div>
            </div>
            """, unsafe_allow_html=True)

        # 1.5 AI Therapist Notes (Restored)
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 16px; padding: 1.5rem; margin-top: 1.5rem; border: 1px solid rgba(167, 139, 250, 0.2);">
            <div style="color: #a78bfa; font-weight: 600; margin-bottom: 0.5rem;">💬 AI Therapist Notes</div>
            <div style="color: #e2e8f0; font-size: 1.05rem; line-height: 1.6;">
                {data.get('conversational_response', 'Analysis complete. See recommendations below.')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Recommendations Grid
        st.markdown("### 🌟 Recommended For You")
        
        # Helper for Feedback
        def send_feedback(emotion, action, reward, category_name):
            try:
                payload = {
                    "session_id": st.session_state.user_session_id,
                    "emotion": data.get("final_emotion"),
                    "action": action,
                    "reward": reward
                }
                requests.post(f"{API_BASE_URL}/feedback", json=payload)
                st.toast(f"Thanks! I'll improve my {category_name} suggestions. 🧠")
            except:
                st.error("Could not send feedback.")

        # Row 1: Activity & Therapy
        r1_col1, r1_col2 = st.columns(2)
        
        # Activity
        with r1_col1:
            activity_item = data.get('activity', 'N/A')
            search_url = f"https://www.google.com/search?q={activity_item.replace(' ', '+')}"
            st.markdown(f"""
            <a href="{search_url}" target="_blank" class="link-card">
                <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4);">
                    <div class="metric-label" style="color: #34d399;">🏃 Activity</div>
                    <div style="color: #f1f5f9; font-weight: 500;">{activity_item}</div>
                    <div class="action-link">Get Details</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        # Therapy Strategy
        with r1_col2:
            therapy_item = data.get('therapy', 'N/A')
            # Import THERAPY_DETAILS to get description
            from rl_engine.therapy_rl import THERAPY_DETAILS
            details = THERAPY_DETAILS.get(therapy_item, {"description": "No detailed information available.", "link": "https://www.google.com/search?q=" + therapy_item.replace(' ', '+')})
            
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4);">
                <div class="metric-label" style="color: #f472b6;">🧘 Therapy Strategy</div>
                <div style="color: #f1f5f9; font-weight: 500; margin-bottom: 0.5rem;">{therapy_item}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📖 View Therapy Details", expanded=False):
                st.markdown(f"<p style='color: #e2e8f0;'>{details['description']}</p>", unsafe_allow_html=True)
                st.markdown(f"<a href='{details['link']}' target='_blank' style='color: #6366f1; text-decoration: none;'>Learn More ↗</a>", unsafe_allow_html=True)
            
        # Row 2: Entertainment (Music, Movie, Game) with FEEDBACK
        r2_col1, r2_col2, r2_col3 = st.columns(3)
        
        # Music (YouTube Link)
        with r2_col1:
            music_item = data.get('music', 'N/A')
            yt_url = f"https://www.youtube.com/results?search_query={music_item.replace(' ', '+')}"
            st.markdown(f"""
            <a href="{yt_url}" target="_blank" class="link-card">
                <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                    <div class="metric-label" style="color: #fbbf24;">🎵 Song</div>
                    <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 2rem;">{music_item}</div>
                    <div class="action-link">Play on YouTube</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_music", use_container_width=True):
                send_feedback(data.get("final_emotion"), music_item, 1, "music")
            if fb_c2.button("👎", key=f"dislike_music", use_container_width=True):
                 send_feedback(data.get("final_emotion"), music_item, -1, "music")

        # Movie (Google Search Link)
        with r2_col2:
            movie_item = data.get('movie', 'N/A')
            movie_url = f"https://www.google.com/search?q={movie_item.replace(' ', '+')}+movie"
            st.markdown(f"""
            <a href="{movie_url}" target="_blank" class="link-card">
                <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                    <div class="metric-label" style="color: #a78bfa;">🎬 Movie</div>
                    <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 2rem;">{movie_item}</div>
                    <div class="action-link">Search Movie</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_movie", use_container_width=True):
                send_feedback(data.get("final_emotion"), movie_item, 1, "movie")
            if fb_c2.button("👎", key=f"dislike_movie", use_container_width=True):
                 send_feedback(data.get("final_emotion"), movie_item, -1, "movie")

        # Game (Google Search Link)
        with r2_col3:
            game_item = data.get('game', 'N/A')
            game_url = f"https://www.google.com/search?q={game_item.replace(' ', '+')}+game"
            st.markdown(f"""
            <a href="{game_url}" target="_blank" class="link-card">
                <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                    <div class="metric-label" style="color: #2dd4bf;">🎮 Game</div>
                    <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 2rem;">{game_item}</div>
                    <div class="action-link">Play/Search Game</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_game", use_container_width=True):
                send_feedback(data.get("final_emotion"), game_item, 1, "game")
            if fb_c2.button("👎", key=f"dislike_game", use_container_width=True):
                 send_feedback(data.get("final_emotion"), game_item, -1, "game")

    return None

# =====================================================
# MAIN CONTENT CONTROLLER
# =====================================================

# Title Section
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem; padding: 0 1rem;">
    <h1 style="font-size: 3.8rem; margin-bottom: 1rem; font-weight: 800; line-height: 1.1; background: linear-gradient(to right, #a5b4fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">LYKA AI</h1>
    <p style="font-size: 1.25rem; color: #94a3b8; max-width: 700px; margin: 0 auto;">I'm here to listen, support, and help you find peace. Every conversation is a step toward feeling better. 💙</p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = {}

# Render Interface based on Mode
chat_input_value = None
if interaction_mode == "Wholesome Conversation":
    chat_input_value = render_chat_interface()
else:
    render_therapy_interface()


# =====================================================
# DATA PROCESSING (COMMON)
# =====================================================

# Prompt Handling Logic
prompt = None

# Check for persistent audio from a previous reset
if st.session_state.get("pending_audio"):
    chat_input_value = {"audio_bytes": st.session_state.pending_audio}
    st.session_state.pending_audio = None

# 1. Text Input via custom chat column (High Priority)
if chat_input_value:
    if isinstance(chat_input_value, dict) and "audio_bytes" in chat_input_value:
        # Handle inline audio
        audio_data = chat_input_value["audio_bytes"]
        with st.spinner("Transcribing your voice..."):
            try:
                files = {"file": ("audio.wav", audio_data, "audio/wav")}
                transcribe_res = requests.post(f"{API_BASE_URL}/transcribe", files=files)
                if transcribe_res.status_code == 200:
                    prompt = transcribe_res.json().get("text")
                else:
                    st.error("Could not transcribe audio.")
            except Exception as e:
                st.error(f"Error during transcription: {e}")
    else:
        # Standard text
        prompt = chat_input_value

# 2. explicit text submission via other box (Therapy Mode)
elif "prompt_input" in st.session_state and st.session_state.prompt_input:
    prompt = st.session_state.prompt_input
    st.session_state.prompt_input = None

# Process Input if prompt exists
if prompt:
    # Add user message to history (for chat mode mostly, but good to keep record)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process with Backend
    with st.spinner("🔄 Analying your state..."):
        try:
            # Prepare payload
            payload = {
                "text": prompt, 
                "use_camera": use_camera,
                "session_id": st.session_state.user_session_id
            }
            
            # Make API Request
            response = requests.post(API_URL, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.latest_analysis = data
                
                # Get the conversational response (new empathetic format)
                conversational_response = data.get("conversational_response")
                
                if conversational_response:
                    
                    # TTS Playback
                    try:
                        tts_response = requests.post(f"{API_BASE_URL}/tts", json={"text": conversational_response})
                        if tts_response.status_code == 200:
                            st.audio(tts_response.content, format="audio/mp3", autoplay=True)
                    except Exception as e:
                        print(f"TTS Error: {e}")

                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": conversational_response,
                        "analysis": data
                    })
                    
                else:
                    # Fallback
                    ai_response = f"I've analyzed your emotional state and detected a **{data.get('final_emotion', 'neutral')}** tone."
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_response,
                        "analysis": data
                    })
                
                # Rerun to update UI
                st.rerun()
                
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown error")
                    st.error(f"❌ Server Error: {response.status_code} - {error_msg}")
                except:
                    st.error(f"❌ Server Error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection Error: Backend server is not accessible.")
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")


# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    Developed for Adaptive AI Emotional Intelligence System • 2026
</div>
""", unsafe_allow_html=True)
