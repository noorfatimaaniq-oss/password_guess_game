import streamlit as st
import random
import time
import base64
import re

# ===================== Word Lists =====================
WORDS = {
    "Countries": {"easy": ['pakistan','india','brazil','canada'],
                  "medium": ['venezuela','argentina','singapore'],
                  "hard": ['kazakhstan','liechtenstein','luxembourg']},
    "Foods": {"easy": ['biryani','pizza','sushi','burger'],
              "medium": ['lasagna','paella','quesadilla'],
              "hard": ['bouillabaisse','ratatouille','coqauvin']},
    "Names": {"easy": ['noor','ali','fatima','omar'],
              "medium": ['alexander','christopher','isabella'],
              "hard": ['maximilian','catherine','frederick']},
    "Programming": {"easy": ['java','python','c++'],
                    "medium": ['javascript','typescript','kotlin'],
                    "hard": ['haskell','elixir','rustlang']}
}

CATEGORY_EMOJIS = {"Countries": "🌍", "Foods": "🍔", "Names": "👤", "Programming": "💻"}
MAX_ATTEMPTS = 7

# ===================== Password Strength Logic =====================
def password_strength(pw):
    score = 0
    if len(pw) >= 8:
        score += 1
    if re.search(r"[A-Z]", pw):
        score += 1
    if re.search(r"[a-z]", pw):
        score += 1
    if re.search(r"[0-9]", pw):
        score += 1
    if re.search(r"[@$!%*?&#]", pw):
        score += 1
    return score

def strength_label(score):
    if score <= 2:
        return "Weak 🔴", 30
    elif score <= 4:
        return "Medium 🟡", 65
    else:
        return "Strong 🟢", 100

# ===================== Sound Player =====================
def play_sound(file_path):
    try:
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.components.v1.html(
            f"<audio autoplay><source src='data:audio/mp3;base64,{b64}'></audio>",
            height=0
        )
    except:
        pass

# ===================== Session State =====================
for key in ["secret","attempts","start_time","scores","last_guess","username"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "scores" else ""

# ===================== UI =====================
st.markdown("<h1 style='text-align:center;'>🔐 Password Guessing Game</h1>", unsafe_allow_html=True)

st.session_state.username = st.text_input("👤 Enter your name:")

with st.expander("🎯 Game Settings", expanded=True):
    category = st.selectbox("Category", WORDS.keys())
    difficulty = st.selectbox("Difficulty", ["easy","medium","hard"])

    if st.button("🚀 Start Game"):
        st.session_state.secret = random.choice(WORDS[category][difficulty])
        st.session_state.attempts = 0
        st.session_state.start_time = time.time()
        st.session_state.last_guess = ""
        st.success(f"Game Started {CATEGORY_EMOJIS[category]} | Length: {len(st.session_state.secret)}")

# ===================== Guess Input =====================
guess = st.text_input("📝 Enter password guess:", value=st.session_state.last_guess)
st.session_state.last_guess = guess

# ===================== Strength Meter =====================
if guess:
    s = password_strength(guess)
    label, progress = strength_label(s)
    st.progress(progress)
    st.write(f"Strength: **{label}**")

# ===================== Buttons =====================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Guess"):
        if not st.session_state.secret:
            st.warning("Start the game first!")
        else:
            st.session_state.attempts += 1
            secret = st.session_state.secret
            attempts = st.session_state.attempts
            elapsed = int(time.time() - st.session_state.start_time)

            if guess == secret:
                remaining = MAX_ATTEMPTS - attempts
                score = remaining * 10 + max(0, 60 - elapsed)
                st.balloons()
                st.success(f"🎉 Correct! Score: {score}")
                st.session_state.scores.append(
                    (st.session_state.username, score, difficulty)
                )
                play_sound("win.mp3")
                st.session_state.secret = ""

            elif attempts >= MAX_ATTEMPTS:
                st.error(f"❌ Game Over! Password was: {secret}")
                play_sound("lose.mp3")
                st.session_state.secret = ""

            else:
                hint = ""
                for i in range(len(secret)):
                    if i < len(guess) and guess[i] == secret[i]:
                        hint += "✅"
                    else:
                        hint += "_"
                st.info(f"Hint: {hint} | Attempts: {attempts}")

with col2:
    if st.button("🛑 Give Up"):
        st.warning(f"Password was: {st.session_state.secret}")
        play_sound("giveup.mp3")
        st.session_state.secret = ""

# ===================== Leaderboard =====================
st.markdown("---")
if st.session_state.scores:
    st.subheader("🏆 Leaderboard")
    for i, s in enumerate(sorted(st.session_state.scores, key=lambda x: -x[1])[:5]):
        st.write(f"{i+1}. {s[0]} — {s[1]} pts ({s[2]})")
