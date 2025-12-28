import streamlit as st
import requests
import html

# --- CONFIG ---
BACKEND_URL = "https://inbox-intelligence.onrender.com"
st.set_page_config(page_title="Inbox Command Center", page_icon="⚡", layout="wide")

# --- AUTH LOGIC ---
if "token" in st.query_params:
    st.session_state["auth_token"] = st.query_params["token"]
    st.query_params.clear()
    st.rerun()

def api_get(endpoint):
    token = st.session_state.get("auth_token")
    if not token: return None
    try: return requests.get(f"{BACKEND_URL}{endpoint}", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    except: return None

def api_post(endpoint, payload):
    token = st.session_state.get("auth_token")
    if not token: return None
    try: return requests.post(f"{BACKEND_URL}{endpoint}", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=20)
    except: return None

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetric"] { background-color: #262730; border: 1px solid #444; padding: 10px; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #1E1E1E !important; border: 1px solid #333 !important; border-radius: 4px !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Command Center")
    if "auth_token" not in st.session_state:
        st.link_button("🔐 Login", f"{BACKEND_URL}/auth/login", type="primary", use_container_width=True)
    else:
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state["auth_token"]
            if "data" in st.session_state: del st.session_state["data"]
            st.rerun()
            
    if st.button("🔄 Sync Inbox", use_container_width=True):
        if "auth_token" in st.session_state:
            with st.spinner("Analyzing..."):
                res = api_get("/result")
                if res and res.status_code == 200:
                    st.session_state["data"] = res.json().get("categories", {})
                    st.toast("Synced!", icon="✅")
                    st.rerun()
                else: st.error("Sync failed.")
        else: st.warning("Login first.")

# --- MAIN DASHBOARD ---
if "data" not in st.session_state:
    st.markdown("## 👋 Inbox Intelligence")
    st.info("Login on the sidebar to start.")
else:
    cats = st.session_state["data"]
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Action", len(cats.get("🚨 Action Required", [])), delta="Urgent", delta_color="inverse")
    c2.metric("Apps", len(cats.get("⏳ Applications & Updates", [])))
    c3.metric("Uni", len(cats.get("🎓 University & Learning", [])))
    c4.metric("Promo", len(cats.get("🗑️ Promotions & Noise", [])))
    
    tabs = st.tabs(["🚨 Action", "⏳ Apps", "🎓 Uni", "🗑️ Promos"])
    keys = ["🚨 Action Required", "⏳ Applications & Updates", "🎓 University & Learning", "🗑️ Promotions & Noise"]

    for tab, key in zip(tabs, keys):
        with tab:
            emails = cats.get(key, [])
            if not emails: st.success("Caught up!")
            
            for mail in emails:
                sub = html.escape(mail.get("subject", "(No Subject)"))
                sender = html.escape(mail.get("from", "Unknown"))
                snippet = html.escape(mail.get("snippet", ""))
                msg_id = mail.get("id")
                
                with st.expander(f"{sender} | {sub}"):
                    st.markdown(f"_{snippet}..._")
                    st.divider()
                    
                    # ✅ THE REPLY WORKFLOW
                    user_intent = st.text_input("How should we reply?", placeholder="e.g. Accept the offer and ask about remote work...", key=f"intent_{msg_id}")
                    
                    if st.button("✨ Draft Reply", key=f"gen_{msg_id}"):
                        if user_intent:
                            with st.spinner("AI is writing..."):
                                res = api_post("/action/generate_reply", {"msg_id": msg_id, "intent": user_intent})
                                if res and res.status_code == 200:
                                    st.session_state[f"draft_{msg_id}"] = res.json()["reply"]
                                    st.rerun()
                    
                    # PREVIEW BOX (Only shows if draft exists)
                    if f"draft_{msg_id}" in st.session_state:
                        st.markdown("### 📝 Edit & Send")
                        final_body = st.text_area("Preview:", value=st.session_state[f"draft_{msg_id}"], height=150, key=f"edit_{msg_id}")
                        
                        col_send, col_discard = st.columns([1, 4])
                        with col_send:
                            if st.button("🚀 Send Now", key=f"send_{msg_id}", type="primary"):
                                with st.spinner("Sending..."):
                                    res = api_post("/action/send_custom", {"msg_id": msg_id, "body": final_body})
                                    if res and res.status_code == 200:
                                        st.toast("Sent! 🚀", icon="✅")
                                        del st.session_state[f"draft_{msg_id}"]
                                        st.rerun()
                                    else: st.error("Failed to send.")
                        with col_discard:
                            if st.button("❌ Discard", key=f"disc_{msg_id}"):
                                del st.session_state[f"draft_{msg_id}"]
                                st.rerun()
                    
                    st.divider()
                    # Trash & Open Actions
                    bt1, bt2 = st.columns([1, 4])
                    with bt1:
                        if st.button("🗑️ Trash", key=f"tr_{msg_id}"):
                            api_get(f"/action/trash/{msg_id}")
                            st.toast("Deleted!", icon="🗑️")
                            st.rerun()
                    with bt2:
                        st.link_button("↗ Gmail", f"https://mail.google.com/mail/u/0/#inbox/{msg_id}")
