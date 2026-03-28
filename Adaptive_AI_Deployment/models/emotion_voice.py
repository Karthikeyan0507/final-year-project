import os
import base64
import tempfile
import numpy as np
import librosa
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "voice_emotion_model.pkl")

# ── Model cache: load once, reuse forever ────────────────────────────────────
_MODEL_CACHE = None

def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if os.path.exists(MODEL_PATH):
            _MODEL_CACHE = joblib.load(MODEL_PATH)
    return _MODEL_CACHE
# ─────────────────────────────────────────────────────────────────────────────

def _convert_to_wav(src_path: str) -> str:
    """
    Convert any audio format (WebM, OGG, etc.) to WAV using pydub.
    Returns the path to a temp WAV file.
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(src_path)
        wav_path = src_path.replace(os.path.splitext(src_path)[1], "_converted.wav")
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception as e:
        print(f"[VoiceEmotion] Audio conversion failed, trying original: {e}")
        return src_path  # Fallback: try the original file

def extract_features(file_path: str):
    """
    Extracts 53 audio features (40 MFCC + 12 Chroma + 1 RMS) at low sample rate
    for fast, accurate emotion detection.
    """
    try:
        # Reduced sample rate (16000 is sufficient for speech, 40% faster than 22050)
        y, sr = librosa.load(file_path, sr=16000, mono=True)

        # Trim silence with slightly aggressive top_db
        y, _ = librosa.effects.trim(y, top_db=25)

        if len(y) < 1000:
            # Audio too short after trimming
            return None

        # 40 MFCCs (up from 13 → much better accuracy)
        mfccs      = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfcc_mean  = np.mean(mfccs, axis=1)     # shape (40,)

        # Chroma (12 bins) — captures pitch/tonality
        chroma     = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean= np.mean(chroma, axis=1)    # shape (12,)

        # RMS Energy (1 value) — captures loudness/stress
        rms        = librosa.feature.rms(y=y)
        rms_mean   = np.array([np.mean(rms)])   # shape (1,)

        features = np.hstack([mfcc_mean, chroma_mean, rms_mean])  # (53,)
        return features

    except Exception as e:
        print(f"[VoiceEmotion] Feature extraction error: {e}")
        return None


def detect_voice_emotion(audio_b64: str) -> str:
    """
    Receives base64-encoded audio (any format from browser),
    converts → WAV, extracts features, and predicts emotion.
    Returns a label string like 'Sad', 'Happy', 'Trauma', etc.
    """
    if not audio_b64:
        return "Neutral"

    # 1. Decode base64
    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception as e:
        print(f"[VoiceEmotion] Base64 decode error: {e}")
        return "Neutral"

    # 2. Write to temp file (use .webm extension so pydub knows the format)
    raw_suffix = ".webm"
    wav_path   = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=raw_suffix) as tmp:
        tmp.write(audio_bytes)
        raw_path = tmp.name

    try:
        # 3. Convert to WAV
        wav_path = _convert_to_wav(raw_path)

        # 4. Extract features
        features = extract_features(wav_path)
        if features is None:
            return "Neutral"

        # 5. Predict using cached model
        model = _get_model()
        if model is None:
            print("[VoiceEmotion] Model not found.")
            return "Neutral"

        return model.predict(features.reshape(1, -1))[0]

    except Exception as e:
        print(f"[VoiceEmotion] Detection error: {e}")
        return "Neutral"

    finally:
        # Cleanup temp files
        for path in [raw_path, wav_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
