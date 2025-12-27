import streamlit as st
import requests
import html

# 1. CRITICAL: Point to your LIVE backend (No trailing slash)
BACKEND_URL = "https://inboxintelligence.onrender.com"
st.set_page_config(page_title="Inbox Command Center", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetric"] { background-color: #262730; border: 1px solid #444; padding: 10px; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #1E1E1E !important; border: 1px solid #333 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚡ Command Center")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url={BACKEND_URL}/auth/login">', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Sync", use_container_width=True):
            with st.spinner("Syncing..."):
                try:
                    res = requests.get(f"{BACKEND_URL}/result", timeout=15)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("status") == "success":
                            st.session_state["data"] = data["categories"]
                            st.toast("Synced!", icon="✅")
                            st.rerun()
                        else:
                            st.warning("Login required")
                except:
                    st.error("Backend sleeping. Try again in 1 min.")

    if "data" in st.session_state:
        st.success("🟢 Online")

if "data" in st.session_state:
    categories = st.session_state["data"]
    
    c_urgent = len(categories.get("🚨 Action Required", []))
    c_apps = len(categories.get("⏳ Applications & Updates", []))
    c_uni = len(categories.get("🎓 University & Learning", []))
    c_promo = len(categories.get("🗑️ Promotions & Noise", []))
    
    st.markdown("### 📊 Inbox Health")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Action", c_urgent, delta="Urgent", delta_color="inverse")
    m2.metric("Apps", c_apps)
    m3.metric("Uni", c_uni)
    m4.metric("Promos", c_promo)
    
    tabs = st.tabs(["🚨 Action", "⏳ Apps", "🎓 Uni", "🗑️ Promos"])
    keys = ["🚨 Action Required", "⏳ Applications & Updates", "🎓 University & Learning", "🗑️ Promotions & Noise"]
    
    for tab, key in zip(tabs, keys):
        with tab:
            for mail in categories.get(key, []):
                sub = html.escape(mail.get("subject", ""))
                sender = html.escape(mail.get("from", ""))
                snippet = html.escape(mail.get("snippet", ""))
                count = mail.get("sender_count", 1)
                
                header = f"{sender} ({count}) | {sub}" if count > 1 else f"{sender} | {sub}"
                
                with st.expander(header):
                    st.markdown(f"**{sub}**\n\n_{snippet}..._")
                    if mail.get("id"):
                        st.link_button("↗ Open Gmail", f"https://mail.google.com/mail/u/0/#inbox/{mail['id']}")
else:
    st.title("👋 Inbox Intelligence")
    st.info("Click 'Login' in the sidebar to start.")
