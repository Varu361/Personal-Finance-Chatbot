# Personal-Finance-Chatbot
import streamlit as st
from datetime import datetime
import json
import requests

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8000/chat"

# --- Page config ---
st.set_page_config(page_title="Personal Finance Chatbot", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f0f4f8 0%, #d9e6f6 100%); font-family: 'Segoe UI', sans-serif; }
.chat-container { max-height: 70vh; overflow-y: auto; padding: 10px; margin-bottom: 70px; }
.user-message { background: linear-gradient(135deg, #a8e6cf, #dcedc1); padding: 12px 18px; border-radius: 18px 18px 0px 18px; margin: 8px 0; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.assistant-message { background: linear-gradient(135deg, #ffffff, #f0f0f0); padding: 12px 18px; border-radius: 18px 18px 18px 0px; margin: 8px 0; display: inline-block; border: 1px solid #e5e7eb; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.sticky-input { position: fixed; bottom: 0; left: 0; width: 75%; background: rgba(255,255,255,0.9); padding: 10px 20px; box-shadow: 0 -3px 8px rgba(0,0,0,0.1); backdrop-filter: blur(8px); }
.profile-card { background: rgba(255,255,255,0.6); border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); backdrop-filter: blur(10px); }
.stButton > button { background-color: #2563eb !important; color: white !important; border-radius: 8px !important; border: none; padding: 8px 16px; }
.stButton > button:hover { background-color: #1d4ed8 !important; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- Helpers ---
def default_assistant():
    return {
        "role": "assistant",
        "content": (
            "👋 Hi — I'm FinBot, your personal finance assistant.\n\n"
            "I can help with savings, **taxes**, and **investment ideas**.\n"
            "💡 Try asking: 'How much should I save monthly?' or 'How can I reduce taxable income?'"
        ),
        "ts": datetime.utcnow().isoformat(),
    }

def clear_messages():
    st.session_state["messages"] = [default_assistant()]

def append_message(role, content):
    st.session_state["messages"].append({
        "role": role,
        "content": content,
        "ts": datetime.utcnow().isoformat()
    })

def fetch_response_from_backend(prompt: str, profile: dict) -> str:
    try:
        payload = {"prompt": prompt, "profile": profile}
        r = requests.post(BACKEND_URL, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json().get("response", "No response from backend.")
        else:
            return f"Error {r.status_code}: {r.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"

# --- Session state init ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [default_assistant()]

if "profile" not in st.session_state:
    st.session_state["profile"] = {"name": "", "age": 0, "income": 0.0, "risk": "Medium"}

if "input" not in st.session_state:
    st.session_state["input"] = ""

# --- Input handler ---
def handle_user_input():
    user_input = st.session_state.input
    if user_input.strip():
        append_message("user", user_input)
        backend_reply = fetch_response_from_backend(user_input, st.session_state["profile"])
        append_message("assistant", backend_reply)
    st.session_state.input = ""

# --- Sidebar ---
with st.sidebar:
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.header("👤 Profile & Settings")
    name = st.text_input("Name", value=st.session_state["profile"].get("name", ""))
    age = st.number_input("Age", min_value=0, max_value=120, value=int(st.session_state["profile"].get("age") or 0))
    income = st.number_input("Annual income (₹)", min_value=0.0, value=float(st.session_state["profile"].get("income") or 0.0), step=1000.0)
    risk = st.selectbox("Risk tolerance", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(st.session_state["profile"].get("risk", "Medium")))
    if st.button("💾 Save profile"):
        st.session_state["profile"] = {"name": name, "age": age, "income": income, "risk": risk}
        st.success("Profile saved!")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🧹 Clear conversation"):
        clear_messages()

    st.markdown("### 📂 Export")
    transcript_json = json.dumps(st.session_state["messages"], indent=2)
    st.download_button("⬇ Download transcript", data=transcript_json, file_name="chat_transcript.json", mime="application/json")

# --- Main Chat ---
st.title("💬 Personal Finance Chatbot")
st.write("Your AI-powered assistant for savings, taxes, and investments.")

# Chat messages
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Input bar
st.markdown("<div class='sticky-input'>", unsafe_allow_html=True)
st.text_input(
    "💭 Type a question about savings, taxes, or investments...",
    key="input",
    on_change=handle_user_input
)
st.markdown("</div>", unsafe_allow_html=True)

# Quick prompts
st.markdown("---")
st.subheader("⚡ Quick Prompts")
prompts = [
    "How much to save monthly for 6 months emergency fund?",
    "Tax-saving strategies for salaried employees",
    "Investment options for ₹10,000/month"
]
for p in prompts:
    if st.button(p, key=f"prompt_{p}"):
        append_message("user", p)
        backend_reply = fetch_response_from_backend(p, st.session_state["profile"])
        append_message("assistant", backend_reply)
