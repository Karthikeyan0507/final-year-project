import sys
import os
import time
import streamlit as st
import requests
from datetime import datetime

# =====================================================
# PROJECT PATH FIX
# =====================================================
import uuid
import json
import streamlit.components.v1 as components

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
    initial_sidebar_state="collapsed"  # Start collapsed; user opens via hamburger button
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    /* ============================================================
       LYKA AI - Premium Dark Theme  (Single source of truth CSS)
       ============================================================ */

    /* 1. Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* 2. Root variables */
    :root {
        --bg-deep:      #080c14;
        --bg-mid:       #0d1424;
        --bg-surface:   #111827;
        --bg-elevated:  #1a2236;
        --border:       rgba(255,255,255,0.07);
        --border-glow:  rgba(139,92,246,0.35);
        --accent:       #7c3aed;
        --accent-2:     #6366f1;
        --accent-soft:  rgba(124,58,237,0.15);
        --user-bubble:  #0e4d3d;
        --ai-bubble:    #161f2e;
        --text-primary: #f1f5f9;
        --text-muted:   #8b9bb4;
        --text-dim:     #475569;
    }

    /* 3. Global */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* 4. App background — deep animated nebula */
    .stApp {
        background: linear-gradient(135deg, #060b18 0%, #0d1424 40%, #130d2e 70%, #080c14 100%) !important;
        background-attachment: fixed !important;
    }

    /* Subtle star-field shimmer overlay */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.12) 0%, transparent 100%),
            radial-gradient(1px 1px at 80% 60%, rgba(255,255,255,0.08) 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 80%, rgba(255,255,255,0.06) 0%, transparent 100%);
        pointer-events: none;
        z-index: 0;
    }

    /* 5. Main block */
    .block-container {
        padding: 1rem 0.5rem 160px 0.5rem !important;
        max-width: 100% !important;
    }

    /* 6. Hide Streamlit chrome */
    #MainMenu, header, footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }

    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1424 0%, #111827 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }

    /* Sidebar brand strip */
    .sidebar-brand {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        padding: 1.8rem 1.2rem 1.4rem;
        text-align: center;
        margin: -1rem -1rem 1.5rem;
        border-radius: 0 0 20px 20px;
    }
    .sidebar-brand h2 {
        color: #fff !important;
        margin: 0.6rem 0 0;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-shadow: 0 2px 12px rgba(0,0,0,0.4);
    }

    /* Sidebar text & labels */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-muted) !important;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Sidebar radio buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.3rem;
        display: block;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--text-muted) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        border-color: var(--accent);
        background: var(--accent-soft);
        color: var(--text-primary) !important;
    }

    /* Sidebar button */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: 1px solid rgba(239,68,68,0.3);
        color: #f87171;
        border-radius: 12px;
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(239,68,68,0.1);
        border-color: #f87171;
        color: #fca5a5;
    }

    /* Sidebar divider */
    hr { border-color: var(--border) !important; }

    /* ---- PAGE TITLE ---- */
    .page-title {
        text-align: center;
        padding: 1.2rem 1rem 2rem;
        animation: fadeSlideIn 0.6s ease;
    }
    .page-title h1 {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.6rem;
        line-height: 1.1;
        text-shadow: none;
    }
    .page-title p {
        color: var(--text-muted);
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* ---- CHAT HEADER (pinned) ---- */
    .chat-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 62px;
        background: rgba(13, 20, 36, 0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        padding: 0 1.5rem;
        z-index: 1001;
    }
    .chat-header-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 2px solid var(--accent);
        margin-right: 12px;
        object-fit: cover;
    }
    .chat-header-name {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1rem;
        margin: 0;
    }
    .chat-header-status {
        color: #34d399;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .chat-header-actions {
        margin-left: auto;
        display: flex;
        gap: 1.2rem;
        color: var(--text-muted);
        font-size: 1.15rem;
        cursor: pointer;
    }

    /* ---- CHAT MESSAGES ---- */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 10px;
        animation: messagePop 0.25s ease;
    }
    .user-row  { justify-content: flex-end;   }
    .ai-row    { justify-content: flex-start;  }

    .chat-bubble {
        padding: 8px 12px;
        border-radius: 12px;
        max-width: 85%;
        color: var(--text-primary);
        font-size: 0.98rem;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
    }
    .user-bubble {
        background: #005c4b; /* WhatsApp dark sent color */
        border-top-right-radius: 0px;
    }
    .user-bubble::after {
        content: "";
        position: absolute;
        top: 0;
        right: -8px;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 10px 10px 0 0;
        border-color: #005c4b transparent transparent transparent;
    }
    .ai-bubble {
        background: #202c33; /* WhatsApp dark received color */
        border-top-left-radius: 0px;
    }
    .ai-bubble::after {
        content: "";
        position: absolute;
        top: 0;
        left: -8px;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 0 10px 10px 0;
        border-color: transparent #202c33 transparent transparent;
    }
    .bubble-timestamp {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.6);
        float: right;
        margin: 4px 0 0 8px;
        clear: right;
    }
    .tick-mark {
        color: #53bdeb; /* WhatsApp blue ticks */
        margin-left: 2px;
        font-size: 0.75rem;
    }

    /* ---- TYPING INDICATOR ---- */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 12px 16px;
    }
    .typing-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent);
        animation: typingBounce 1.2s infinite ease-in-out;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
        0%, 80%, 100% { transform: translateY(0) scale(0.75); opacity: 0.5; }
        40%           { transform: translateY(-6px) scale(1); opacity: 1; }
    }

    /* Old .chat-input-bar CSS removed */

    /* Transparent text input inside bar */
    div[data-testid="stTextInput"] {
        flex-grow: 1 !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        font-size: 1rem !important;
        font-family: 'Outfit', sans-serif !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--text-dim) !important;
    }

    /* Mic / Audio button */
    div[data-testid="stAudioInput"] button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(124,58,237,0.4) !important;
        transition: all 0.2s ease !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white' width='20px' height='20px'%3E%3Cpath d='M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z'/%3E%3Cpath d='M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 20px !important;
        color: transparent !important;
    }
    div[data-testid="stAudioInput"] button:hover {
        background-color: #6d28d9 !important;
        box-shadow: 0 6px 18px rgba(124,58,237,0.55) !important;
    }
    div[data-testid="stAudioInput"] button[aria-label*="Stop"],
    div[data-testid="stAudioInput"] button[data-testid="stAudioInputStopButton"] {
        background-color: #dc2626 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Crect x='6' y='6' width='12' height='12'/%3E%3C/svg%3E") !important;
        box-shadow: 0 4px 12px rgba(220,38,38,0.5) !important;
    }
    div[data-testid="stAudioInput"] label,
    div[data-testid="stAudioInput"] [role="toolbar"],
    div[data-testid="stAudioInput"] [class*="Waveform"],
    div[data-testid="stAudioInput"] span,
    div[data-testid="stAudioInput"] [data-testid="stMarkdownContainer"] {
        display: none !important;
    }

    /* Strip white card backgrounds from column wrappers */
    div[data-testid="stHorizontalBlock"],
    div[data-testid="stColumn"],
    div[class*="stElementContainer"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    /* ---- METRIC / RECOMMENDATION CARDS ---- */
    .metric-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.4rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.175,0.885,0.32,1.275);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent);
        box-shadow: 0 12px 30px rgba(124,58,237,0.2);
    }
    .metric-label {
        color: var(--text-muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 800;
    }
    .link-card { text-decoration: none !important; }
    .action-link {
        font-size: 0.75rem;
        color: var(--accent-2);
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* ---- THERAPY BOX ---- */
    .therapy-box {
        background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-mid) 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        color: var(--text-primary);
        box-shadow: 0 12px 28px rgba(0,0,0,0.35);
        animation: fadeSlideIn 0.5s ease;
    }

    /* ---- GLOBAL BUTTONS ---- */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        color: white;
        border: none;
        border-radius: 14px;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(124,58,237,0.35);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,58,237,0.5);
    }

    /* ---- FORMS & EXPANDERS ---- */
    [data-testid="stExpander"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-muted) !important;
    }
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* ---- TOAST ---- */
    [data-testid="stToast"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-glow) !important;
        color: var(--text-primary) !important;
        border-radius: 14px !important;
    }

    /* ---- WELLNESS SIDEBAR CARD ---- */
    .wellness-card {
        background: var(--accent-soft);
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 14px;
        padding: 1rem;
        margin-top: 0.5rem;
    }
    .wellness-label {
        font-size: 0.7rem;
        color: #a78bfa;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .wellness-value {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
    }

    /* ---- HAMBURGER sidebar toggle button ---- */
    #lyka-menu-btn {
        position: fixed;
        top: 14px;
        left: 16px;
        z-index: 1100;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(124,58,237,0.2);
        border: 1px solid var(--border-glow);
        cursor: pointer;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 5px;
        transition: all 0.22s ease;
        padding: 0;
        backdrop-filter: blur(10px);
    }
    #lyka-menu-btn:hover {
        background: rgba(124,58,237,0.45);
        transform: scale(1.08);
        border-color: var(--accent);
    }
    .hb-line {
        width: 18px;
        height: 2px;
        background: #a78bfa;
        border-radius: 2px;
        transition: all 0.22s ease;
    }
    #lyka-menu-btn.open .hb-line:nth-child(1) { transform: translateY(7px) rotate(45deg); }
    #lyka-menu-btn.open .hb-line:nth-child(2) { opacity: 0; }
    #lyka-menu-btn.open .hb-line:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

    /* Push chat header right to not overlap hamburger */
    .chat-header { padding-left: 64px !important; }

    /* ---- USER MESSAGE SEND ANIMATION ---- */
    @keyframes flyToRight {
        0%   { opacity: 0; transform: translateX(-40px) translateY(30px) scale(0.88); }
        55%  { opacity: 1; transform: translateX(8px) translateY(-4px) scale(1.02); }
        100% { opacity: 1; transform: translateX(0) translateY(0) scale(1); }
    }
    .user-row.new-msg .chat-bubble {
        animation: flyToRight 0.38s cubic-bezier(0.23, 1, 0.32, 1) forwards;
    }
    /* Standard pop for all other messages */
    .chat-row { animation: messagePop 0.25s ease; }

    /* ---- ENHANCED INPUT BOX (CSS Anchor Hack) ---- */
    div[data-testid="stVerticalBlock"]:has(.input-bottom-anchor):not(:has(div[data-testid="stVerticalBlock"] .input-bottom-anchor)) {
        position: fixed;
        bottom: 18px;
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 1200px;
        background: rgba(15, 20, 35, 0.96);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border: 1.5px solid rgba(139,92,246,0.28);
        border-radius: 36px;
        padding: 4px 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        z-index: 1000;
        box-shadow: 0 12px 40px rgba(0,0,0,0.55), 0 0 0 1px rgba(124,58,237,0.08);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlock"]:has(.input-bottom-anchor):not(:has(div[data-testid="stVerticalBlock"] .input-bottom-anchor)):focus-within {
        border-color: rgba(139,92,246,0.6);
        box-shadow: 0 12px 40px rgba(0,0,0,0.55), 0 0 0 3px rgba(124,58,237,0.12);
    }

    /* Maintain correct layout of horizontal block inside our hacked fixed container */
    div[data-testid="stVerticalBlock"]:has(.input-bottom-anchor):not(:has(div[data-testid="stVerticalBlock"] .input-bottom-anchor)) > div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Input field */
    div[data-testid="stTextInput"] {
        flex-grow: 1 !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        font-size: 1rem !important;
        font-family: 'Outfit', sans-serif !important;
        padding: 6px 0 !important;
        caret-color: var(--accent);
    }
    div[data-testid="stTextInput"] input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--text-dim) !important;
        font-style: italic;
    }

    /* Hide focus ring on the wrapper */
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        box-shadow: none !important;
        border: none !important;
    }

</style>
""", unsafe_allow_html=True)

# =====================================================
# HAMBURGER TOGGLE + THINKING INDICATOR JS
# =====================================================
components.html("""
<script>
(function() {

    var sidebarOpen = false;

    function getSidebar() {
        return window.parent.document.querySelector('[data-testid="stSidebar"]');
    }

    function openSidebar(sidebar) {
        sidebar.style.setProperty('display', 'block', 'important');
        void sidebar.offsetWidth; // Force Reflow
        sidebar.style.setProperty('transform', 'translateX(0)', 'important');
        sidebar.style.setProperty('width', '21rem', 'important');
        sidebar.style.setProperty('min-width', '21rem', 'important');
        sidebar.style.setProperty('visibility', 'visible', 'important');
        sidebar.style.transition = 'transform 0.28s cubic-bezier(0.4,0,0.2,1), width 0.28s';
        sidebarOpen = true;
    }

    function closeSidebar(sidebar) {
        sidebar.style.setProperty('transform', 'translateX(-150%)', 'important');
        sidebar.style.setProperty('width', '0', 'important');
        sidebar.style.setProperty('min-width', '0', 'important');
        sidebar.style.setProperty('visibility', 'hidden', 'important');
        sidebar.style.transition = 'transform 0.28s cubic-bezier(0.4,0,0.2,1), width 0.28s';
        setTimeout(function() {
            if (!sidebarOpen) {
                sidebar.style.setProperty('display', 'none', 'important');
            }
        }, 300);
        sidebarOpen = false;
    }

    // 1. Inject hamburger button
    var btn = document.createElement('button');
    btn.id    = 'lyka-menu-btn';
    btn.title = 'Toggle menu';
    btn.innerHTML = '<div class="hb-line"></div><div class="hb-line"></div><div class="hb-line"></div>';

    var inject = function() {
        var app = window.parent.document.querySelector('.stApp');
        if (!app) { setTimeout(inject, 250); return; }

        if (!window.parent.document.getElementById('lyka-menu-btn')) {
            app.appendChild(btn);
        }

        // Ensure sidebar starts hidden
        var sidebar = getSidebar();
        if (sidebar) {
            sidebar.style.transition = 'none';
            sidebar.style.setProperty('transform', 'translateX(-150%)', 'important');
            sidebar.style.setProperty('width', '0', 'important');
            sidebar.style.setProperty('min-width', '0', 'important');
            sidebar.style.setProperty('visibility', 'hidden', 'important');
            sidebar.style.setProperty('display', 'none', 'important');
            
            // Inject close button into sidebar
            if (!window.parent.document.getElementById('lyka-close-btn')) {
                var closeBtn = document.createElement('div');
                closeBtn.id = 'lyka-close-btn';
                closeBtn.innerHTML = '&times;';
                closeBtn.style.cssText = 'position: absolute; top: 12px; right: 20px; font-size: 32px; color: #f87171; cursor: pointer; z-index: 10000; line-height: 1; transition: transform 0.2s ease; font-family: sans-serif; font-weight: bold;';
                closeBtn.onmouseover = function() { this.style.transform = 'scale(1.2)'; };
                closeBtn.onmouseout = function() { this.style.transform = 'scale(1)'; };
                closeBtn.onclick = function() {
                    var sb = getSidebar();
                    closeSidebar(sb);
                    btn.classList.remove('open');
                };
                sidebar.appendChild(closeBtn);
            }
        }

        btn.addEventListener('click', function() {
            var sb = getSidebar();
            if (!sb) return;
            if (!sidebarOpen) {
                openSidebar(sb);
                btn.classList.add('open');
            } else {
                closeSidebar(sb);
                btn.classList.remove('open');
            }
        });

        // Close sidebar if user clicks OUTSIDE it
        window.parent.document.addEventListener('click', function(e) {
            if (!sidebarOpen) return;
            var sb = getSidebar();
            var b  = window.parent.document.getElementById('lyka-menu-btn');
            if (sb && !sb.contains(e.target) && b && !b.contains(e.target)) {
                closeSidebar(sb);
                btn.classList.remove('open');
            }
        });
    };
    inject();

})();
</script>
""", height=0)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <img src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png" width="60" style="filter: brightness(1.3) drop-shadow(0 2px 8px rgba(0,0,0,0.4));">
        <h2>LYKA AI</h2>
        <p style="color: rgba(255,255,255,0.6); font-size: 0.75rem; margin: 0;">Your AI Companion</p>
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
# CALLBACKS (Session State Fix)
# =====================================================

def handle_chat_input():
    if st.session_state.chat_input:
        st.session_state.temp_chat_value = st.session_state.chat_input
        st.session_state.chat_input = "" # Clear the widget
        if "staged_text" in st.session_state:
            st.session_state.staged_text = "" # Clear staged emoji text

def handle_therapy_input():
    if st.session_state.therapy_input:
        st.session_state.temp_therapy_value = st.session_state.therapy_input
        st.session_state.therapy_input = "" # Clear the widget

# =====================================================
# RENDER FUNCTIONS
# =====================================================

def render_chat_interface():
    """Renders the WhatsApp-style split chat UI"""
    
    # WhatsApp Header (Pinned)
    st.markdown(f"""
    <div class="chat-header">
        <img class="chat-header-avatar" src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png">
        <div>
            <div class="chat-header-name">LYKA AI</div>
            <div class="chat-header-status">online</div>
        </div>
        <div class="chat-header-actions">
            <!-- 📞 is now an interactive streamlit button below -->
            <span title="Video Call">📹</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inject the interactive phone button into the header
    header_btn_container = st.container()
    with header_btn_container:
        st.markdown('<div class="emergency-btn-anchor"></div>', unsafe_allow_html=True)
        if st.button("📞", key="emergency_phone_btn", help="Setup Emotion Delivery (Notify Beloved One)"):
            st.session_state.show_emergency_form = not st.session_state.show_emergency_form

    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"]:has(.emergency-btn-anchor):not(:has(div[data-testid="stVerticalBlock"] .emergency-btn-anchor)) {
            position: fixed;
            top: 2px;
            right: 70px; /* Position it right next to the video call icon */
            z-index: 1002;
            width: auto !important;
        }
        div[data-testid="stVerticalBlock"]:has(.emergency-btn-anchor) button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            font-size: 1.35rem !important;
            color: #8b9bb4 !important;
            padding: 0 10px !important;
            min-height: 48px !important;
        }
        div[data-testid="stVerticalBlock"]:has(.emergency-btn-anchor) button:hover {
            color: #fff !important;
            transform: scale(1.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Add a spacer at the top for the header
    st.markdown('<div style="margin-top: 60px;"></div>', unsafe_allow_html=True)

    # Emotion Delivery Setup Form
    if st.session_state.get("show_emergency_form"):
        with st.container():
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.95); padding: 15px 20px 5px; border-radius: 12px 12px 0 0; border: 1px solid #8b5cf6; border-bottom: none;">
                <h3 style="color: #a78bfa; margin-top: 0; font-size: 1.3rem;">❤️ Emotion Delivery Setup</h3>
                <p style="color: #cbd5e1; font-size: 0.9rem;">Whenever LYKA detects critical stress or trauma, we can automatically notify your designated beloved one gently.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("emergency_contact_form", border=True):
                c1, c2 = st.columns(2)
                ec = st.session_state.emergency_contact or {}
                user_name = c1.text_input("Your Name", value=ec.get("user_name", ""))
                user_phone = c2.text_input("Your Phone Number", value=ec.get("user_phone", ""))
                
                c3, c4 = st.columns(2)
                beloved_name = c3.text_input("Beloved One Name", value=ec.get("beloved_name", ""))
                beloved_phone = c4.text_input("Beloved Phone Number", value=ec.get("beloved_phone", ""))
                
                c5, c6 = st.columns(2)
                beloved_email = c5.text_input("Beloved Email (For Free Alerts)", value=ec.get("beloved_email", ""))
                
                rels = ["Mom", "Dad", "Sister", "Brother", "Girlfriend", "Boyfriend", "Friend", "Spouse"]
                current_rel = ec.get("relationship", "Mom")
                try: idx = rels.index(current_rel)
                except ValueError: idx = 0
                relationship = c6.selectbox("Relationship", rels, index=idx)
                
                sc1, sc2 = st.columns([1, 4])
                submit = sc1.form_submit_button("Save Profile", type="primary")
                if submit:
                    st.session_state.emergency_contact = {
                        "user_name": user_name,
                        "user_phone": user_phone,
                        "beloved_name": beloved_name,
                        "beloved_phone": beloved_phone,
                        "beloved_email": beloved_email,
                        "relationship": relationship
                    }
                    st.session_state.show_emergency_form = False
                    st.rerun()

            if st.button("Cancel & Close", key="close_emergency_form"):
                st.session_state.show_emergency_form = False
                st.rerun()
                
            st.markdown("<hr>", unsafe_allow_html=True)
    
    # ---------- Message History ----------
    total = len(st.session_state.messages)
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        time_str = message.get("time", datetime.now().strftime("%I:%M %p"))
        is_newest = (i == total - 1)

        if role == "user":
            # User bubbles on the RIGHT — apply fly animation on newest message
            extra_class = "new-msg" if is_newest else ""
            st.markdown(f"""
            <div class="chat-row user-row {extra_class}">
                <div class="chat-bubble user-bubble">
                    {content}
                    <div class="bubble-timestamp">{time_str} <span class="tick-mark">&#x2713;&#x2713;</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # AI bubbles on the LEFT
            bubble_placeholder = st.empty()

            if message.get("streaming") and is_newest:
                # Word-by-word streaming
                import time as _time
                words = content.split(" ")
                temp_text = ""
                for word in words:
                    temp_text += word + " "
                    bubble_placeholder.markdown(f"""
                    <div class="chat-row ai-row">
                        <div class="chat-bubble ai-bubble">
                            {temp_text}
                            <div class="bubble-timestamp">{time_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    _time.sleep(0.04)
                message["streaming"] = False

            bubble_placeholder.markdown(f"""
            <div class="chat-row ai-row">
                <div class="chat-bubble ai-bubble">
                    {content}
                    <div class="bubble-timestamp">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Typing Indicator
    if st.session_state.get("is_processing", False):
        st.markdown(f"""
        <div class="chat-row ai-row">
            <div class="chat-bubble ai-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Add a spacer at the bottom of the chat to make room for the fixed input bar
    st.markdown('<div style="min-height: 150px; width: 100%; display: block; color: transparent;">&nbsp;</div>', unsafe_allow_html=True)

    # Input Bar
    if st.session_state.get("is_processing", False):
        st.markdown('<div style="position:fixed;bottom:85px;left:50%;transform:translateX(-50%);width:62%;text-align:center;color:var(--text-muted);font-size:0.85rem;z-index:999;">LYKA is thinking...</div>', unsafe_allow_html=True)

    bottom_container = st.container()
    with bottom_container:
        st.markdown('<div class="input-bottom-anchor"></div>', unsafe_allow_html=True)
        col_input, col_mic = st.columns([11, 1])
    
        with col_input:
            st.text_input("Message", key="chat_input", on_change=handle_chat_input, label_visibility="collapsed", placeholder="Message LYKA...")
    
        with col_mic:
            st.audio_input("Mic", key="chat_mic", label_visibility="collapsed")

    components.html("<script>setTimeout(function() { window.parent.scrollTo({ top: window.parent.document.body.scrollHeight, behavior: 'smooth' }); }, 500);</script>", height=0)

    return None

def render_therapy_interface():
    """Renders the new Therapy Session Dashboard UI"""
    
    st.markdown("## 🛋️ Therapy Session Check-In")
    
    # Top Section: Input
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.4); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 2rem;">
        <h4 style="margin-top:0; color: #94a3b8; font-weight: 500;">How are you feeling right now?</h4>
    </div>
    """, unsafe_allow_html=True)

    # Input Section (WhatsApp Style)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # ---------- Therapy Input Section ----------
    st.markdown('<div style="min-height: 150px; width: 100%; display: block; color: transparent;">&nbsp;</div>', unsafe_allow_html=True)
    bottom_container = st.container()
    with bottom_container:
        st.markdown('<div class="input-bottom-anchor"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([10, 1])

        with col1:
            st.text_input("How are you feeling?", key="therapy_input", on_change=handle_therapy_input, label_visibility="collapsed", placeholder="Share your thoughts...")

        with col2:
            st.audio_input("Mic", key="therapy_mic", label_visibility="collapsed")

    components.html("<script>setTimeout(function() { window.parent.scrollTo({ top: window.parent.document.body.scrollHeight, behavior: 'smooth' }); }, 500);</script>", height=0)

    if use_camera:
        st.caption("📷 Facial Analysis Active")

    # Results Section
    # Only verify if we have a LATEST analysis that matches the current session interaction
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
            # Fix: If therapy_item is a dict, parse it correctly to avoid .replace crash
            therapy_item_str = str(therapy_item.get('name', therapy_item)) if isinstance(therapy_item, dict) else str(therapy_item)
            
            # Import THERAPY_DETAILS to get description
            from rl_engine.therapy_rl import THERAPY_DETAILS
            details = THERAPY_DETAILS.get(therapy_item_str, {
                "description": "No detailed information available.", 
                "link": "https://www.google.com/search?q=" + therapy_item_str.replace(' ', '+')
            })
            
            st.markdown(f"""
            <a href="{details['link']}" target="_blank" class="link-card">
                <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4);">
                    <div class="metric-label" style="color: #f472b6;">🧘 Therapy Strategy</div>
                    <div style="color: #f1f5f9; font-weight: 500; margin-bottom: 0.5rem;">{therapy_item_str}</div>
                    <div class="action-link">Learn More ↗</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
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
<div class="page-title">
    <h1>LYKA AI</h1>
    <p>Your safe space to talk, reflect, and feel better. Every conversation is a step toward peace.</p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = {}
if "emergency_contact" not in st.session_state:
    st.session_state.emergency_contact = None
if "show_emergency_form" not in st.session_state:
    st.session_state.show_emergency_form = False

# 0. Render Interface based on Mode
if interaction_mode == "Wholesome Conversation":
    render_chat_interface()
else:
    render_therapy_interface()

# 1. Check for inputs (from callbacks or audio)
prompt = None
if interaction_mode == "Wholesome Conversation":
    # Chat Logic
    if "temp_chat_value" in st.session_state and st.session_state.temp_chat_value:
        prompt = st.session_state.temp_chat_value
        st.session_state.temp_chat_value = ""
    
    # Check for direct audio input if available from the widget key (Streamlit 1.40+)
    if "chat_mic" in st.session_state and st.session_state.chat_mic:
        prompt = {"audio_bytes": st.session_state.chat_mic.read()}
else:
    # Therapy Logic
    if "temp_therapy_value" in st.session_state and st.session_state.temp_therapy_value:
        prompt = st.session_state.temp_therapy_value
        st.session_state.temp_therapy_value = ""
    
    if "therapy_mic" in st.session_state and st.session_state.therapy_mic:
        prompt = {"audio_bytes": st.session_state.therapy_mic.read()}

# 2. Check for persistent audio from a previous reset
if not prompt and st.session_state.get("pending_audio"):
    prompt = {"audio_bytes": st.session_state.pending_audio}
    st.session_state.pending_audio = None

# Process Input if prompt exists
if prompt:
    st.session_state.is_processing = True
    
    # --- COMMON AUDIO TRANSCRIBE LOGIC ---
    if isinstance(prompt, dict) and "audio_bytes" in prompt:
        audio_data = prompt["audio_bytes"]
        # We can keep the transcription spinner as it's a different message, 
        # but the user might prefer consistency. For now, let's keep it brief.
        with st.spinner("Transcribing..."):
            try:
                files = {"file": ("audio.wav", audio_data, "audio/wav")}
                transcribe_res = requests.post(f"{API_BASE_URL}/transcribe", files=files)
                if transcribe_res.status_code == 200:
                    prompt = transcribe_res.json().get("text")
                else:
                    st.error("Could not transcribe audio.")
                    prompt = None
            except Exception as e:
                st.error(f"Error during transcription: {e}")
                prompt = None

    # Proceed if we have a valid text prompt (either from input or transcription)
    if prompt:
        now_str = datetime.now().strftime("%I:%M %p")
        # Add user message to history with timestamp
        st.session_state.messages.append({"role": "user", "content": prompt, "time": now_str})
        
        # Process with Backend
        try:
            # Prepare payload
            payload = {
                "text": prompt, 
                "use_camera": use_camera,
                "session_id": st.session_state.user_session_id,
                "emergency_contact": st.session_state.get("emergency_contact")
            }
            # Make API Request
            response = requests.post(API_URL, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.latest_analysis = data
                
                # Get the conversational response
                conversational_response = data.get("conversational_response")
                
                if conversational_response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": conversational_response,
                        "analysis": data,
                        "streaming": True,
                        "time": datetime.now().strftime("%I:%M %p")
                    })
                else:
                    # Fallback
                    ai_response = f"I've analyzed your emotional state and detected a **{data.get('final_emotion', 'neutral')}** tone."
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_response,
                        "analysis": data,
                        "streaming": True
                    })
                
                # Check for Emergency Notification Delivery
                if data.get("emergency_notified"):
                    st.toast("🚨 Automatically dispatched care message to your beloved one!", icon="💌")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**[Emotion Delivery Activated]** 💌 \nI noticed you're feeling significantly distressed. I have automatically sent the following alert message to your designated contact:\n\n> *\"{data.get('simulated_message')}\"*",
                        "streaming": False,
                        "time": datetime.now().strftime("%I:%M %p")
                    })
                
                # Clear query params
                st.query_params.clear()
                
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
        finally:
            st.session_state.is_processing = False
            # Ensure we don't carry over the prompt into the next run
            if "temp_chat_value" in st.session_state:
                st.session_state.temp_chat_value = ""
            st.rerun()


# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    Developed for Adaptive AI Emotional Intelligence System • 2026
</div>
""", unsafe_allow_html=True)
