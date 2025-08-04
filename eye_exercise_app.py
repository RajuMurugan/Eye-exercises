import streamlit as st
import platform
import os
import time
import math
import yaml
import uuid
from datetime import datetime
import json
import streamlit.components.v1 as components

# --- Page Config ---
st.set_page_config(page_title="👁️ Eye Exercise Trainer", layout="wide")

# --- Constants ---
SESSION_TIMEOUT = 180  # seconds (3 min)
CONFIG_FILE = "config.yaml"
SESSION_FILE = "session_data.yaml"

# --- Beep Sound Function ---
def play_beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 300)
    else:
        os.system('echo -n "\a"; sleep 0.2')

# --- Load Config ---
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"⚠️ Error loading config.yaml: {e}")
        st.stop()

# --- Session Management ---
def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return yaml.safe_load(f)
    return {"active_users": {}}

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        yaml.safe_dump(data, f)

def update_session(mobile, device_id):
    session_data["active_users"][mobile] = {
        "device_id": device_id,
        "timestamp": time.time()
    }
    save_sessions(session_data)

def is_session_valid(mobile, device_id):
    user = session_data["active_users"].get(mobile)
    if not user:
        return False
    return (
        user["device_id"] == device_id and
        (time.time() - user["timestamp"]) < SESSION_TIMEOUT
    )

def logout_user():
    mobile = st.session_state.get("mobile", "")
    if mobile in session_data["active_users"]:
        session_data["active_users"].pop(mobile)
        save_sessions(session_data)
    st.session_state.logged_in = False
    st.session_state.mobile = ""
    st.session_state.device_id = str(uuid.uuid4())

# --- Init Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

# --- Load Config and Sessions ---
config = load_config()
users = config["credentials"]["users"]
session_data = load_sessions()

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔐 Login")
    mobile = st.text_input("📱 Mobile Number")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login"):
        if mobile in users and users[mobile]["password"] == password:
            if mobile in session_data["active_users"]:
                existing = session_data["active_users"][mobile]
                if (time.time() - existing["timestamp"]) < SESSION_TIMEOUT and existing["device_id"] != st.session_state.device_id:
                    st.error("⚠️ Already logged in from another device.")
                    st.stop()
            update_session(mobile, st.session_state.device_id)
            st.session_state.logged_in = True
            st.session_state.mobile = mobile
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("❌ Invalid mobile number or password")
    st.stop()

# --- Validate Session ---
mobile = st.session_state.get("mobile", "")
if not is_session_valid(mobile, st.session_state.device_id):
    logout_user()
    st.warning("⚠️ Session expired. Please login again.")
    st.rerun()

update_session(mobile, st.session_state.device_id)

# --- Logout Option ---
with st.sidebar:
    st.success(f"✅ Logged in as: {mobile}")
    remaining = SESSION_TIMEOUT - int(time.time() - session_data["active_users"][mobile]["timestamp"])
    st.info(f"⏳ Session active. Remaining: {remaining}s")
    if st.button("🚪 Logout"):
        logout_user()
        st.rerun()

# --- Eye Exercises ---
exercises = [
    "Left to Right", "Right to Left", "Top to Bottom", "Bottom to Top",
    "Circle Clockwise", "Circle Anti-Clockwise",
    "Diagonal ↘", "Diagonal ↙", "Diagonal ↖", "Diagonal ↗",
    "Zig-Zag", "Near-Far Focus", "Figure Eight", "Square Path",
    "Micro Saccades", "Eye Relaxation", "W Shape", "Random Jump"
]

# --- Settings ---
st.title("👁️ Eye Exercise Trainer (Fullscreen Mode)")
speed_mode = st.selectbox("🌟 Speed Mode", ["Relax", "Therapy", "Focus"])
speed_multiplier = {"Relax": 0.7, "Therapy": 1.0, "Focus": 1.3}[speed_mode]
dark_mode = st.toggle("🌙 Dark Mode", value=False)

canvas_width = 1920
canvas_height = 900
radius = 200
margin = 60
dot_size = 30

placeholder = st.empty()
countdown = st.empty()

# --- Position Logic ---
def get_position(t, ex):
    x, y = canvas_width // 2, canvas_height // 2
    progress = abs(math.sin(2 * math.pi * t))
    # (same as your existing logic)
    # Add all movement logics here (omitted for brevity)
    return x, y

# --- Draw Dot ---
def draw_dot(x, y, scale=1.0):
    size = int(dot_size * scale)
    html = f"""
    <div style="position: relative; width: {canvas_width}px; height: {canvas_height}px;
                background-color: {'#111' if dark_mode else '#e0f7fa'}; border: 4px solid #333;">
        <div style="position: absolute; left: {x}px; top: {y}px;
                    width: {size}px; height: {size}px;
                    background-color: red; border-radius: 50%; border: 1px solid black;"></div>
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
            pos = get_position(t, ex)
            draw_dot(pos[0], pos[1])
            countdown.markdown(f"⏳ {30 - int(elapsed)}s remaining")
            time.sleep(0.03 / speed_multiplier)
        placeholder.empty()
        countdown.empty()
    st.success("🎉 Routine Completed!")

# --- Start ---
if st.button("▶ Start Fullscreen Eye Exercise"):
    run_automatic()
