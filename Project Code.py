import streamlit as st
import pandas as pd
import nltk
import string
import os
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# ----------------------------
# Setup
# ----------------------------
nltk.download("stopwords")

st.set_page_config(
    page_title="Emoji and Sticker Suggestion Model",
    layout="centered"
)

EMOTIONS = ["happy", "sad", "anger", "fear", "love", "surprise", "neutral"]
STICKER_DIR = "stickers"
os.makedirs(STICKER_DIR, exist_ok=True)

# ----------------------------
# Custom CSS (UI MAGIC ✨)
# ----------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
}

.main {
    background: transparent;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.title {
    text-align: center;
    font-size: 36px;
    font-weight: 800;
    color: #2c3e50;
}

.subtitle {
    text-align: center;
    color: #7f8c8d;
    margin-bottom: 30px;
}

.stButton>button {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    border-radius: 30px;
    padding: 0.6em 1.8em;
    font-size: 16px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #5a67d8, #6b46c1);
    transform: scale(1.02);
}

.emoji-box {
    font-size: 30px;
    text-align: center;
}

.emotion-badge {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 20px;
    background: #eef2ff;
    color: #4c51bf;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Preprocessing
# ----------------------------
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    return " ".join(tokens)

# ----------------------------
# Train model (cached)
# ----------------------------
@st.cache_data
def train_model():
    df = pd.read_csv("emotion_dataset.csv")
    df = df.dropna(subset=["text", "emotion"]).reset_index(drop=True)
    df["clean_text"] = df["text"].apply(preprocess_text)

    X = df["clean_text"]
    y = df["emotion"]

    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(X)

    X_train, _, y_train, _ = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42
    )

    model = MultinomialNB()
    model.fit(X_train, y_train)

    return model, vectorizer

model, vectorizer = train_model()

# ----------------------------
# Emoji mapping
# ----------------------------
emoji_df = pd.read_csv("emoji_mapping.csv")
emoji_dict = {}
for _, row in emoji_df.iterrows():
    emoji_dict.setdefault(row["emotion"], []).append(row["emoji_or_sticker"])

# ----------------------------
# Session sticker storage
# ----------------------------
if "sticker_dict" not in st.session_state:
    st.session_state.sticker_dict = {e: [] for e in EMOTIONS}

# ----------------------------
# Sidebar (clean)
# ----------------------------
st.sidebar.markdown("## 🖼 Sticker Manager")

emotion_choice = st.sidebar.selectbox("Emotion", EMOTIONS)
uploaded = st.sidebar.file_uploader(
    "Upload Sticker",
    type=["png", "jpg", "jpeg", "webp"]
)

if uploaded:
    path = os.path.join(STICKER_DIR, uploaded.name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())

    st.session_state.sticker_dict[emotion_choice].append(path)
    st.sidebar.success("Sticker added!")

# ----------------------------
# Main UI
# ----------------------------
st.markdown('<div class="title">Emoji and Sticker Suggestion Model</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand emotions. React beautifully.</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
user_text = st.text_area("💬 Type your message", height=120)

if st.button("Analyze Emotion"):
    if user_text.strip():
        clean = preprocess_text(user_text)
        vector = vectorizer.transform([clean])
        emotion = model.predict(vector)[0]

        st.markdown(f"""
        <div style="text-align:center;margin-top:15px;">
            <span class="emotion-badge">{emotion.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        emojis = emoji_dict.get(emotion, [])[:3]
        if emojis:
            st.markdown('<div class="emoji-box">' + " ".join(emojis) + '</div>', unsafe_allow_html=True)

        stickers = st.session_state.sticker_dict.get(emotion, [])
        if stickers:
            st.image(stickers[0], width=220)
        else:
            st.info("No sticker uploaded for this emotion yet.")
    else:
        st.warning("Please enter text")

st.markdown('</div>', unsafe_allow_html=True)
