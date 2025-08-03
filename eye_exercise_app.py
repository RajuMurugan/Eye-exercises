import streamlit as st
import time
import math
import platform
import os
import json
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="👁️ Eye Exercise Trainer", layout="wide")

# --- Beep Sound Function ---
def play_beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 300)
    else:
        os.system('echo -n "\a"; sleep 0.2')

# --- User Data Handling ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

def log_session(username):
    users = load_users()
    if username in users:
        users[username]['sessions'].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        save_users(users)

# --- Initialize session state for login ---
if 'username' not in st.session_state:
    st.session_state.username = ""

users = load_users()
st.sidebar.subheader("🔑 Login")

# --- Login/Logout Logic ---
if st.session_state.username == "":
    username_input = st.sidebar.text_input("Enter your Username:")
    if username_input:
        if username_input not in users:
            users[username_input] = {"sessions": []}
            save_users(users)
            st.sidebar.success("✅ New user created.")
        st.session_state.username = username_input
        st.rerun()
else:
    username = st.session_state.username
    st.sidebar.success(f"✅ Logged in as: {username}")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.username = ""
        st.rerun()

# --- Stop if not logged in ---
if st.session_state.username == "":
    st.warning("Please log in to access the app.")
    st.stop()

username = st.session_state.username

# --- Exercises List ---
exercises = [
    "Left to Right", "Right to Left", "Top to Bottom", "Bottom to Top",
    "Circle Clockwise", "Circle Anti-Clockwise", "Diagonal ↘", "Diagonal ↙",
    "Zig-Zag", "Blinking", "Near-Far Focus", "Figure Eight", "Square Path",
    "Appearing Dot Focus", "Micro Saccades", "Eye Relaxation", "W Shape"
]

# --- Session State ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- UI Settings ---
st.title("👁️ Eye Exercise Trainer")
mode_type = st.radio("Choose Mode", ["🕒 Automatic", "🎮 Controllable"], horizontal=True)
device = st.selectbox("💻 Device", ["Laptop/Desktop", "Mobile"])
canvas_width, canvas_height = (1000, 500) if device == "Laptop/Desktop" else (360, 300)
radius = 150 if device == "Laptop/Desktop" else 80
dot_size = 30 if device == "Laptop/Desktop" else 20
margin = 40
dark_mode = st.toggle("🌙 Dark Mode", value=False)
speed_mode = st.selectbox("🌟 Speed Mode", ["Relax", "Therapy", "Focus"])
speed_multiplier = {"Relax": 0.7, "Therapy": 1.0, "Focus": 1.3}[speed_mode]

# --- Display Area ---
placeholder = st.empty()
countdown = st.empty()

# --- Core Movement Function ---
def get_position(t, ex):
    x, y = canvas_width // 2, canvas_height // 2
    progress = abs(math.sin(2 * math.pi * t))

    if ex == "Left to Right":
        x = margin + int((canvas_width - 2 * margin) * progress)
    elif ex == "Right to Left":
        x = canvas_width - margin - int((canvas_width - 2 * margin) * progress)
    elif ex == "Top to Bottom":
        y = margin + int((canvas_height - 2 * margin) * progress)
    elif ex == "Bottom to Top":
        y = canvas_height - margin - int((canvas_height - 2 * margin) * progress)
    elif ex == "Circle Clockwise":
        angle = 2 * math.pi * t
        x = int(canvas_width // 2 + radius * math.cos(angle))
        y = int(canvas_height // 2 + radius * math.sin(angle))
    elif ex == "Circle Anti-Clockwise":
        angle = -2 * math.pi * t
        x = int(canvas_width // 2 + radius * math.cos(angle))
        y = int(canvas_height // 2 + radius * math.sin(angle))
    elif ex == "Diagonal ↘":
        x = margin + int((canvas_width - 2 * margin) * progress)
        y = margin + int((canvas_height - 2 * margin) * progress)
    elif ex == "Diagonal ↙":
        x = canvas_width - margin - int((canvas_width - 2 * margin) * progress)
        y = margin + int((canvas_height - 2 * margin) * progress)
    elif ex == "Zig-Zag":
        freq = 5
        x = int(margin + (canvas_width - 2 * margin) * t % 1)
        y = int(canvas_height // 2 + (radius // 1.5) * math.sin(freq * 2 * math.pi * t))
    elif ex == "Figure Eight":
        angle = 2 * math.pi * t
        x = int(canvas_width // 2 + radius * math.sin(angle))
        y = int(canvas_height // 2 + radius * math.sin(angle) * math.cos(angle))
    elif ex == "Square Path":
        side = int((t * 4) % 4)
        prog = (t * 4) % 1
        if side == 0:
            x = margin + int((canvas_width - 2 * margin) * prog)
            y = margin
        elif side == 1:
            x = canvas_width - margin
            y = margin + int((canvas_height - 2 * margin) * prog)
        elif side == 2:
            x = canvas_width - margin - int((canvas_width - 2 * margin) * prog)
            y = canvas_height - margin
        elif side == 3:
            x = margin
            y = canvas_height - margin - int((canvas_height - 2 * margin) * prog)
    elif ex == "Appearing Dot Focus":
        visible = int(t * 2) % 2 == 0
        return (canvas_width // 2, canvas_height // 2) if visible else (-100, -100)
    elif ex == "Micro Saccades":
        x = canvas_width // 2 + int(10 * math.sin(30 * math.pi * t))
        y = canvas_height // 2 + int(10 * math.cos(25 * math.pi * t))
    elif ex == "Eye Relaxation":
        x = int(canvas_width // 2 + radius * math.sin(2 * math.pi * t))
        y = int(canvas_height // 2 + radius * math.sin(2 * math.pi * t / 2))
    elif ex == "W Shape":
        phase = (t * 4) % 4
        p = phase % 1
        if phase < 1:
            x = margin + int((canvas_width - 2 * margin) * p / 2)
            y = margin + int((canvas_height - 2 * margin) * p)
        elif phase < 2:
            x = canvas_width // 2 + int((canvas_width - 2 * margin) * p / 2)
            y = canvas_height - margin - int((canvas_height - 2 * margin) * p)
        elif phase < 3:
            x = canvas_width // 2 + int((canvas_width - 2 * margin) * p / 2)
            y = margin + int((canvas_height - 2 * margin) * p)
        else:
            x = canvas_width - margin - int((canvas_width - 2 * margin) * p / 2)
            y = canvas_height - margin - int((canvas_height - 2 * margin) * p)
    return x, y

# --- Draw Dot ---
def draw_dot(x, y):
    html = f"""
    <div style="position: relative; width: {canvas_width}px; height: {canvas_height}px;
                background-color: {'#111' if dark_mode else '#e0f7fa'}; border-radius: 12px;">
        <div style="position: absolute; left: {x}px; top: {y}px;
                    width: {dot_size}px; height: {dot_size}px;
                    background-color: red; border-radius: 50%;"></div>
    </div>"""
    placeholder.markdown(html, unsafe_allow_html=True)

# --- Automatic Mode ---
def run_automatic():
    for i, ex in enumerate(exercises):
        st.subheader(f"Now: {ex} ({i+1}/{len(exercises)})")
        play_beep()
        start = time.time()
        while time.time() - start < 30:
            elapsed = time.time() - start
            t = (elapsed / 30) * speed_multiplier
            x, y = get_position(t, ex)
            draw_dot(x, y)
            countdown.markdown(f"Time left: **{int(30 - elapsed)}s**")
            time.sleep(0.05 / speed_multiplier)
        placeholder.empty()
        countdown.empty()
    st.success("🎉 Routine completed!")
    log_session(username)

# --- Controllable Mode ---
def run_manual():
    with st.sidebar:
        st.subheader("🔧 Controls")
        if st.button("Start/Resume"):
            st.session_state.is_running = True
        if st.button("Stop"):
            st.session_state.is_running = False
        if st.button("Next"):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(exercises)
        if st.button("Previous"):
            st.session_state.current_index = (st.session_state.current_index - 1) % len(exercises)
        sel = st.selectbox("Jump to", exercises, index=st.session_state.current_index)
        if sel != exercises[st.session_state.current_index]:
            st.session_state.current_index = exercises.index(sel)

    if st.session_state.is_running:
        ex = exercises[st.session_state.current_index]
        st.subheader(f"Current: {ex}")
        play_beep()
        start = time.time()
        while time.time() - start < 30 and st.session_state.is_running:
            elapsed = time.time() - start
            t = (elapsed / 30) * speed_multiplier
            x, y = get_position(t, ex)
            draw_dot(x, y)
            countdown.markdown(f"Time left: **{int(30 - elapsed)}s**")
            time.sleep(0.05 / speed_multiplier)
        placeholder.empty()
        countdown.empty()
        play_beep()
        log_session(username)

# --- Main Execution ---
if mode_type == "🕒 Automatic":
    if st.button("Start Automatic Routine"):
        run_automatic()
elif mode_type == "🎮 Controllable":
    run_manual()

# --- Display Progress ---
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Progress")
sessions = users[username]['sessions']
st.sidebar.write(f"Total Sessions: {len(sessions)}")
if sessions:
    st.sidebar.write("Last Session:", sessions[-1])
