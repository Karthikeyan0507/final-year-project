import random
from backend.rl_engine.q_learning import QLearningEngine

# --- DEFINE OPTIONS ---
CBT_OPTIONS = [
    "Cognitive Behavioral Therapy (CBT) Techniques",
    "Dialectical Behavior Therapy (DBT) Skills", 
    "Stress Management Coaching",
    "Emotional Release Therapy",
    "Acceptance and Commitment Therapy (ACT)",
    "Shadow Work Journaling",
    "Compassion-Focused Therapy (CFT)",
    "Eye Movement Desensitization and Reprocessing (EMDR) Concepts",
    "Logotherapy (Finding Meaning)",
    "Interpersonal Therapy (IPT) Techniques",
    "Mindfulness-Based Cognitive Therapy (MBCT)",
    "Solution-Focused Brief Therapy (SFBT) Exercises"
]

THERAPY_DETAILS = {
    "Cognitive Behavioral Therapy (CBT) Techniques": {
        "description": "CBT focuses on identifying and changing negative thought patterns and behaviors to improve emotional regulation.",
        "link": "https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral"
    },
    "Dialectical Behavior Therapy (DBT) Skills": {
        "description": "DBT provides skills for mindfulness, emotion regulation, distress tolerance, and interpersonal effectiveness.",
        "link": "https://www.psychologytoday.com/us/therapy-types/dialectical-behavior-therapy"
    },
    "Stress Management Coaching": {
        "description": "Techniques and strategies designed to help individuals cope with stress more effectively.",
        "link": "https://www.helpguide.org/articles/stress/stress-management.htm"
    },
    "Emotional Release Therapy": {
        "description": "A therapeutic approach that aims to release pent-up emotions and tension from the body.",
        "link": "https://www.healthline.com/health/emotional-release-therapy"
    },
    "Acceptance and Commitment Therapy (ACT)": {
        "description": "ACT encourages people to embrace their thoughts and feelings rather than fighting or feeling guilty for them.",
        "link": "https://www.psychologytoday.com/us/therapy-types/acceptance-and-commitment-therapy"
    },
    "Shadow Work Journaling": {
        "description": "A practice of exploring the 'shadow' or hidden parts of the psyche to gain self-awareness and healing.",
        "link": "https://www.healthline.com/health/mental-health/shadow-work"
    },
    "Compassion-Focused Therapy (CFT)": {
        "description": "CFT aims to help those who struggle with shame and self-criticism by developing compassion for themselves.",
        "link": "https://www.compassionatemind.co.uk/about-cft"
    },
    "Eye Movement Desensitization and Reprocessing (EMDR) Concepts": {
        "description": "A psychotherapy treatment that was originally designed to alleviate the distress associated with traumatic memories.",
        "link": "https://www.emdria.org/about-emdr-therapy/"
    },
    "Logotherapy (Finding Meaning)": {
        "description": "A school of psychology that says humans are motivated by a 'will to meaning,' which is an inner pull to find meaning in life.",
        "link": "https://www.verywellmind.com/an-overview-of-logotherapy-4159308"
    },
    "Interpersonal Therapy (IPT) Techniques": {
        "description": "IPT focuses on improving the quality of a person's interpersonal relationships and social functioning.",
        "link": "https://www.psychologytoday.com/us/therapy-types/interpersonal-psychotherapy"
    },
    "Mindfulness-Based Cognitive Therapy (MBCT)": {
        "description": "MBCT combines cognitive therapy with mindfulness practices to help prevent relapse into depression.",
        "link": "https://www.psychologytoday.com/us/therapy-types/mindfulness-based-cognitive-therapy"
    },
    "Solution-Focused Brief Therapy (SFBT) Exercises": {
        "description": "SFBT focuses on a person's present and future circumstances and goals rather than past experiences.",
        "link": "https://www.psychologytoday.com/us/therapy-types/solution-focused-brief-therapy"
    },
    "Crisis Intervention & Stabilization": {
        "description": "Immediate, short-term psychological care designed to help individuals in a crisis return to their baseline level of functioning.",
        "link": "https://www.nami.org/About-Mental-Illness/Common-with-Mental-Illness/Risk-of-Suicide"
    },
    "Immediate Professional Support": {
        "description": "Connecting with a licensed therapist, counselor, or psychiatrist for urgent mental health needs.",
        "link": "https://www.psychologytoday.com/us/therapists"
    },
    "Grounding Techniques for Severe Distress": {
        "description": "Strategies to help you detach from emotional pain and reconnect with the present moment.",
        "link": "https://www.healthline.com/health/grounding-techniques"
    },
    "Social Connection Therapy": {
        "description": "Focuses on increasing social engagement and improving social skills to combat loneliness.",
        "link": "https://www.psychologytoday.com/us/blog/the-art-of-closeness/202102/the-power-of-connection-in-therapy"
    },
    "Community Building Exercises": {
        "description": "Activities designed to foster a sense of belonging and connection with others in a group setting.",
        "link": "https://www.mindtools.com/pages/article/newTMM_member_connection.htm"
    },
    "Relationship Skills Training": {
        "description": "Provides tools and strategies for communicating effectively and building healthy relationships.",
        "link": "https://www.gottman.com/about/the-gottman-method/"
    },
    "Positive Psychology Reinforcement": {
        "description": "The scientific study of what makes life most worth living, focusing on strengths rather than weaknesses.",
        "link": "https://positivepsychology.com/what-is-positive-psychology/"
    },
    "Sleep Hygiene Education": {
        "description": "Learning about habits and practices that are conducive to sleeping well on a regular basis.",
        "link": "https://www.sleepfoundation.org/sleep-hygiene"
    }
}

MEDITATION_OPTIONS = [
    "Advanced Box Breathing: Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Repeat 10 cycles.",
    "Progressive Muscle Relaxation (PMR): Systematically tense and release muscle groups.",
    "Visualizing the 'Inner Sanctuary': A detailed 15-minute journey to a safe space.",
    "NSDR (Non-Sleep Deep Rest): Protocols to reduce stress and improve neuroplasticity.",
    "Vipassana Mindfulness: Observing sensations without judgment.",
    "SKY Breath Meditation: Rhythmic breathing to harmonize body and mind.", 
    "Compassion-Focused Imagery: Visualizing a compassionate figure.",
    "Loving-Kindness (Metta) Meditation: Sending goodwill to self and others.",
    "Zen Walking Meditation (Kinhin): Mindful pacing and breathing.",
    "Body Scan Meditation: Deeply tuning into physical sensations.",
    "Trataka (Candle Gazing): Building focus and calming the active mind.",
    "So Hum Mantra Meditation: Silent repetition aligned with breath."
]

ACTIVITY_OPTIONS = [
    "Nature Walk (Forest Bathing)",
    "Journaling Emotional Reflections",
    "Engaging in Creative Art or Painting", 
    "Listening to Calming Frequency Music (432Hz)",
    "Cold Shower for Reset",
    "Gentle Stretching or Sunrise Yoga",
    "Writing a Letter (Burn after reading)",
    "Cooking or Baking a new, healthy recipe",
    "Doing a complex puzzle or playing sudoku",
    "Gardening or tending to indoor plants",
    "Reading a chapter of an uplifting book",
    "Deep-cleaning or organizing a small physical space"
]

MUSIC_OPTIONS = [
    "Weightless by Marconi Union (Ambient)",
    "Clair de Lune by Debussy (Classical)",
    "Strawberry Swing by Coldplay (Soft Pop)",
    "Breathe Me by Sia (Emotional)",
    "Holocene by Bon Iver (Indie Folk)",
    "Here Comes The Sun by The Beatles (Uplifting)",
    "Gymnopédies by Satie (Piano)",
    "Lofi Hip Hop Radio (Focus)",
    "Happy by Pharrell Williams (Pop)",
    "Walking on Sunshine by Katrina & The Waves (Upbeat)",
    "Take Five by Dave Brubeck (Smooth Jazz)",
    "River Flows in You by Yiruma (Contemporary Piano)",
    "Resonance by HOME (Synthwave Chill)",
    "Three Little Birds by Bob Marley (Reggae/Positive)",
    "Experience by Ludovico Einaudi (Moving Classical)"
]

MOVIE_OPTIONS = [
    "Inside Out (Understanding Emotions)",
    "The Pursuit of Happyness (Resilience)",
    "Good Will Hunting (Healing)",
    "Soul (Finding Purpose)",
    "Paddington 2 (Wholesome Comfort)",
    "Arrival (Intellectual Sci-Fi)",
    "My Neighbor Totoro (Calm Animation)",
    "Singin' in the Rain (Joyful/Musical)",
    "Ferris Bueller's Day Off (Fun)",
    "Spirited Away (Magical Escapism)",
    "Amélie (Quirky Joy/Appreciation)",
    "Up (Grief and New Adventures)",
    "Spider-Man: Into the Spider-Verse (Action/Visual Flow)",
    "Little Miss Sunshine (Family/Acceptance)"
]

GAME_OPTIONS = [
    "Journey (Meditative Exploration)",
    "Abzu (Underwater Relaxation)",
    "Gris (Emotional Healing)",
    "Animal Crossing (Cozy Socializing)",
    "Minecraft (Creative Zen)",
    "Stardew Valley (Farming Sim)",
    "Tetris Effect (Flow State)",
    "Sky: Children of the Light (Social Adventure)",
    "Super Mario Odyssey (Joyful Adventure)",
    "Just Dance (Physical Fun)",
    "The Sims 4 (Life Simulation/Control)",
    "Portal 2 (Humor/Puzzle Solving)",
    "The Legend of Zelda: Breath of the Wild (Open World Exploration)",
    "Slime Rancher (Cute/Colorful Farming)",
    "Unpacking (Zen Organization)"
]

# --- INITIALIZE RL ENGINES ---
# We use separate engines for each category so they learn independently
music_engine = QLearningEngine(MUSIC_OPTIONS)
movie_engine = QLearningEngine(MOVIE_OPTIONS)
game_engine = QLearningEngine(GAME_OPTIONS)


def choose_therapy(emotion, face_features=None):
    """
    Enhanced recommendation engine with Reinforcement Learning.
    Returns a dictionary with therapy, meditation, and activity suggestions.
    """
    emotion = emotion.lower()

    # --- GEOMETRIC FEATURE OVERRIDES ---
    if face_features:
        # Check for Drowsiness (Low EAR)
        ear = face_features.get("ear", 0.5)
        if ear < 0.22:
            return {
                "therapy": "Sleep Hygiene Education",
                "meditation": "NSDR (Non-Sleep Deep Rest)",
                "activity": "Power Nap (20 mins)",
                "music": music_engine.choose_action(emotion),
                "movie": movie_engine.choose_action(emotion),
                "game": game_engine.choose_action(emotion)
            }
        
        # Check for High Stress (High Brow Furrow / Low Ratio)
        brow_ratio = face_features.get("brow_ratio", 1.0)
        if brow_ratio < 0.55:
            # We enforce therapy but randomize entertainment
            therapy = "Stress Management Coaching"
            meditation = "Progressive Muscle Relaxation (PMR)"
            activity = "Gentle Neck & Shoulder Stretches"
            if emotion not in ["happy", "surprise"]:
                 return {
                    "therapy": therapy,
                    "meditation": meditation,
                    "activity": activity,
                    "music": music_engine.choose_action(emotion),
                    "movie": movie_engine.choose_action(emotion),
                    "game": game_engine.choose_action(emotion)
                 }

    # --- STANDARD LOGIC ---
    # Therapy/Meditation/Activity - Keep random for variety (or could add RL here too)
    
    if "crisis" in emotion or "worthless" in emotion:
        therapy = random.choice([
            "Crisis Intervention & Stabilization", "Immediate Professional Support", "Grounding Techniques for Severe Distress"
        ])
        activity = random.choice([
            "Call a supportive friend or family member", "Hold an ice cube (Sensory Grounding)", "Contact a local helpline"
        ])
    elif "lonely" in emotion or "isolated" in emotion:
        therapy = random.choice([
            "Social Connection Therapy", "Community Building Exercises", "Relationship Skills Training"
        ])
        activity = random.choice([
            "Reach out to an old friend", "Join an online community", "Visit a local coffee shop"
        ])
    elif "happy" in emotion or "positive" in emotion:
        therapy = "Positive Psychology Reinforcement"
        activity = "Share your joy with a friend"
    else:
        therapy = random.choice(CBT_OPTIONS)
        activity = random.choice(ACTIVITY_OPTIONS)

    # Use RL Engines for Entertainment
    # The engines will start random (exploration) and become smarter (exploitation)
    recommendations = {
        "therapy": therapy,
        "meditation": random.choice(MEDITATION_OPTIONS),
        "activity": activity,
        "music": music_engine.choose_action(emotion),
        "movie": movie_engine.choose_action(emotion),
        "game": game_engine.choose_action(emotion)
    }

    return recommendations

def update_recommendation_model(emotion, action, reward):
    """
    Update the appropriate RL engine based on the action received.
    """
    if action in MUSIC_OPTIONS:
        music_engine.update(emotion, action, reward)
        return "music"
    elif action in MOVIE_OPTIONS:
        movie_engine.update(emotion, action, reward)
        return "movie"
    elif action in GAME_OPTIONS:
        game_engine.update(emotion, action, reward)
        return "game"
    else:
        print(f"[RL] Action '{action}' not found in known lists. Skipping update.")
        return None
