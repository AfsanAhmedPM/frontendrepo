import streamlit as st
import requests
import html
import time

# --- CONFIGURATION ---
BACKEND_URL = "https://inbox-intelligence.onrender.com"
st.set_page_config(page_title="Inbox Intelligence", page_icon="⚡", layout="wide")

# --- ANIMATION & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* 1. Global Fade In (Runs whenever page loads) */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .main-content {
        animation: fadeIn 0.8s ease-out forwards;
    }

    /* 2. Landing Page Styles */
    .landing-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 5vh;
    }
    
    .landing-title { 
        font-size: 3.5em; 
        font-weight: 800; 
        background: -webkit-linear-gradient(45deg, #ffffff, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-align: center;
        animation: fadeIn 1s ease-out;
    }
    
    /* 3. Text Shimmer Animation for the Subtitle */
    @keyframes shimmer {
        0% { background-position: -200% center; opacity: 0; }
        100% { background-position: 200% center; opacity: 1; }
    }
    
    .landing-subtitle { 
        font-size: 1.5em; 
        font-weight: 400;
        text-align: center; 
        margin-bottom: 40px;
        background: linear-gradient(90deg, #666, #fff, #666);
        background-size: 200% auto;
        color: #fff;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite; /* Keeps it alive */
    }

    /* 4. Feature Cards Hover Effect */
    .feature-card { 
        background-color: #161b22; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #30363d; 
        text-align: center; 
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    .feature-icon { font-size: 2em; margin-bottom: 10px; display: block; }
    .feature-title { font-size: 1.1em; font-weight: bold; color: white; margin-bottom: 5px; }
    .feature-desc { color: #8b949e; font-size: 0.9em; }

    /* Dashboard Tweaks */
    div[data-testid="stMetric"] { background-color: #262730; border: 1px solid #444; padding: 10px; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #1E1E1E !important; border: 1px solid #333 !important; border-radius: 4px !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- AUTH & API HELPERS ---
if "token" in st.query_params:
    st.session_state["auth_token"] = st.query_params["token"]

if "auth_token" in st.session_state:
    st.query_params["token"] = st.session_state["auth_token"]

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

# --- PART 1: THE LANDING PAGE 🛬 ---
def show_landing_page():
    # We wrap everything in a div with animation class
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    
    # Title
    st.markdown('<div class="landing-title">⚡ Inbox Intelligence</div>', unsafe_allow_html=True)
    
    # Animated Subtitle
    st.markdown(
        '<div class="landing-subtitle">Never miss job, interview, or placement emails.</div>', 
        unsafe_allow_html=True
    )
    
    # Button (Streamlit buttons can't be fully CSS styled easily, so we rely on container width)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 Enter Command Center", use_container_width=True, type="primary"):
            st.session_state["enter_app"] = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # End container

    # Features
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Use HTML for cards to allow Hover Effects
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card main-content" style="animation-delay: 0.2s;">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI Sorting</div>
            <div class="feature-desc">Separates Job Offers from Spam automatically.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card main-content" style="animation-delay: 0.4s;">
            <span class="feature-icon">✍️</span>
            <div class="feature-title">Ghostwriter</div>
            <div class="feature-desc">Draft professional replies in seconds.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card main-content" style="animation-delay: 0.6s;">
            <span class="feature-icon">🗑️</span>
            <div class="feature-title">Fast Clean</div>
            <div class="feature-desc">Delete junk instantly without opening it.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # Close Main Wrapper

# --- PART 2: THE MAIN DASHBOARD 💻 ---
def show_main_app():
    # Wrap Dashboard in Animation too
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚡ Command Center")
        st.caption("v3.0 • AI-Powered Triage")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if "auth_token" not in st.session_state:
                st.link_button("🔐 Login", f"{BACKEND_URL}/auth/login", type="primary", use_container_width=True)
            else:
                if st.button("🚪 Logout", use_container_width=True):
                    del st.session_state["auth_token"]
                    st.query_params.clear()
                    if "data" in st.session_state: del st.session_state["data"]
                    st.rerun()
        with col2:
            refresh_clicked = st.button("🔄 Sync", use_container_width=True)

        if refresh_clicked:
            if "auth_token" not in st.session_state:
                st.warning("Please login first.")
            else:
                with st.spinner("Analyzing inbox..."):
                    res = api_get("/result")
                    if res and res.status_code == 200:
                        data = res.json()
                        st.session_state["data"] = data.get("categories", {})
                        st.toast("Inbox successfully synced!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Sync Failed.")

        st.markdown("---")
        st.markdown("### 🔍 Filter")
        search_query = st.text_input("Search", placeholder="Sender or Subject...", label_visibility="collapsed")
        st.markdown("---")
        if "auth_token" in st.session_state:
            st.success("🟢 System Online")
        else:
            st.info("🟡 Waiting for Login")

    if "data" not in st.session_state:
        st.markdown("## 👋 Ready to work?")
        st.info("Connect your Gmail account on the left to activate the Command Center.")
    else:
        categories = st.session_state["data"]
        
        c_urgent = len(categories.get("🚨 Action Required", []))
        c_apps = len(categories.get("⏳ Applications & Updates", []))
        c_uni = len(categories.get("🎓 University & Learning", []))
        c_promo = len(categories.get("🗑️ Promotions & Noise", []))
        
        st.markdown("### 📊 Inbox Health")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Action Items", c_urgent, delta="Do Now", delta_color="inverse")
        m2.metric("Applications", c_apps, delta="Waiting")
        m3.metric("University", c_uni)
        m4.metric("Promotions", c_promo)
        
        st.divider()

        tabs = st.tabs(["🚨 Action Required", "⏳ Applications", "🎓 University", "🗑️ Promotions"])
        backend_keys = ["🚨 Action Required", "⏳ Applications & Updates", "🎓 University & Learning", "🗑️ Promotions & Noise"]

        for tab, key in zip(tabs, backend_keys):
            with tab:
                email_list = categories.get(key, [])
                if search_query:
                    q = search_query.lower()
                    email_list = [e for e in email_list if q in e['subject'].lower() or q in e['from'].lower()]

                if not email_list: st.success("🎉 Nothing here! You're caught up.")
                
                for mail in email_list:
                    sub = html.escape(mail.get("subject", "(No Subject)"))
                    sender = html.escape(mail.get("from", "Unknown"))
                    snippet = html.escape(mail.get("snippet", ""))
                    count = mail.get("sender_count", 1)
                    msg_id = mail.get("id", "")
                    
                    if "Action" in key: icon = "🔴"
                    elif "Applications" in key: icon = "🟠"
                    elif "University" in key: icon = "🔵"
                    else: icon = "📓"

                    count_str = f"({count})" if count > 1 else ""
                    header_text = f"{icon} {sender} {count_str} | {sub}"
                    unique_suffix = f"{msg_id}_{key}"
                    
                    with st.expander(header_text):
                        st.markdown(f"""
                        <div style="margin-bottom: 10px;"><span style="font-size: 1.2em; font-weight: bold; color: white;">{sub}</span></div>
                        <div style="margin-bottom: 15px; color: #ccc;">"{snippet}..."</div>
                        """, unsafe_allow_html=True)
                        
                        st.divider()
                        
                        user_intent = st.text_input("How should we reply?", placeholder="e.g. Accept offer...", key=f"intent_{unique_suffix}")
                        
                        if st.button("✨ Draft Reply", key=f"gen_{unique_suffix}"):
                            if user_intent:
                                with st.spinner("AI is writing..."):
                                    res = api_post("/action/generate_reply", {"msg_id": msg_id, "intent": user_intent})
                                    if res and res.status_code == 200:
                                        st.session_state[f"draft_{msg_id}"] = res.json()["reply"]
                                        st.rerun()
                                        
                        if f"draft_{msg_id}" in st.session_state:
                            st.markdown("### 📝 Edit & Send")
                            final_body = st.text_area("Preview:", value=st.session_state[f"draft_{msg_id}"], height=150, key=f"edit_{unique_suffix}")
                            
                            c1, c2 = st.columns([1, 4])
                            with c1:
                                if st.button("🚀 Send", key=f"snd_{unique_suffix}", type="primary"):
                                    with st.spinner("Sending..."):
                                        res = api_post("/action/send_custom", {"msg_id": msg_id, "body": final_body})
                                        if res and res.status_code == 200:
                                            st.toast("Sent! 🚀", icon="✅")
                                            del st.session_state[f"draft_{msg_id}"]
                                            st.rerun()
                                        else: st.error("Failed.")
                            with c2:
                                if st.button("❌ Discard", key=f"dsc_{unique_suffix}"):
                                    del st.session_state[f"draft_{msg_id}"]
                                    st.rerun()
                        
                        st.divider()
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            if st.button("🗑️ Trash", key=f"tr_{unique_suffix}"):
                                api_get(f"/action/trash/{msg_id}")
                                st.toast("Deleted!", icon="🗑️")
                                st.rerun()
                        with c2:
                            st.link_button("↗ Open Gmail", f"https://mail.google.com/mail/u/0/#inbox/{msg_id}")
    
    st.markdown('</div>', unsafe_allow_html=True) # Close Wrapper

# --- CONTROL FLOW ---
if "enter_app" not in st.session_state:
    show_landing_page()
else:
    show_main_app()
