import streamlit as st
import requests
import html

# --- CONFIGURATION ---
# ✅ UPDATE: Ensure this matches your live backend URL
BACKEND_URL = "https://inbox-intelligence.onrender.com"
st.set_page_config(page_title="Inbox Command Center", page_icon="⚡", layout="wide")

# --- AUTH & API HELPERS (The "Brains") ---
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

# --- CUSTOM CSS (YOUR UI) ---
st.markdown("""
    <style>
    /* Global Dark Theme Tweaks */
    .stApp { background-color: #0E1117; }
    
    /* Metrics Box Styling */
    div[data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 8px;
    }
    
    /* Remove default expander styling for cleaner look */
    .streamlit-expanderHeader {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (FIXED ALIGNMENT) ---
with st.sidebar:
    st.title("⚡ Command Center")
    st.caption("v3.0 • AI-Powered Triage")
    
    st.markdown("---")
    
    # 1. Action Buttons (Aligned)
    col1, col2 = st.columns(2)
    with col1:
        if "auth_token" not in st.session_state:
             # ✅ FIX: Use link_button for clean login
            st.link_button("🔐 Login", f"{BACKEND_URL}/auth/login", type="primary", use_container_width=True)
        else:
            if st.button("🚪 Logout", use_container_width=True):
                del st.session_state["auth_token"]
                if "data" in st.session_state: del st.session_state["data"]
                st.rerun()

    with col2:
        refresh_clicked = st.button("🔄 Sync", use_container_width=True)

    # 2. Refresh Logic (Toasts)
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
                    st.error("Sync Failed or Session Expired.")

    st.markdown("---")
    
    # 3. Search Filter
    st.markdown("### 🔍 Filter")
    search_query = st.text_input("Search", placeholder="Sender or Subject...", label_visibility="collapsed")
    
    st.markdown("---")
    
    # 4. Footer Status
    if "auth_token" in st.session_state:
        st.success("🟢 System Online")
    else:
        st.info("🟡 Waiting for Login")

# --- MAIN DASHBOARD ---
if "data" not in st.session_state:
    st.markdown("## 👋 Welcome to Inbox Intelligence")
    st.info("Login on the sidebar to activate the Command Center.")
else:
    categories = st.session_state["data"]
    
    # 1. TOP METRICS
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

    # 2. TABS & LOGIC
    tabs = st.tabs(["🚨 Action Required", "⏳ Applications", "🎓 University", "🗑️ Promotions"])
    
    backend_keys = [
        "🚨 Action Required", 
        "⏳ Applications & Updates", 
        "🎓 University & Learning", 
        "🗑️ Promotions & Noise"
    ]

    for tab, key in zip(tabs, backend_keys):
        with tab:
            email_list = categories.get(key, [])
            
            # Search Logic
            if search_query:
                q = search_query.lower()
                email_list = [e for e in email_list if q in e['subject'].lower() or q in e['from'].lower()]
                if not email_list:
                    st.caption("No matches found.")

            if not email_list and not search_query:
                st.success("🎉 Nothing here! You're caught up.")
            
            # 3. RENDER CARDS
            for mail in email_list:
                sub = html.escape(mail.get("subject", "(No Subject)"))
                sender = html.escape(mail.get("from", "Unknown"))
                snippet = html.escape(mail.get("snippet", ""))
                count = mail.get("sender_count", 1)
                msg_id = mail.get("id", "")
                
                # Dynamic Icon
                if "Action" in key: icon = "🔴"
                elif "Applications" in key: icon = "🟠"
                elif "University" in key: icon = "🔵"
                else: icon = "📓"

                count_str = f"({count})" if count > 1 else ""

                # Clean Header String
                header_text = f"{icon} {sender} {count_str} | {sub}"
                
                # ✅ FIX: Unique Key to prevent crashes
                unique_suffix = f"{msg_id}_{key}"
                
                with st.expander(header_text):
                    # --- YOUR ORIGINAL HTML STYLING ---
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 1.2em; font-weight: bold; color: white;">{sub}</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <span style="background: #333; padding: 2px 8px; border-radius: 4px; color: #bbb; font-size: 0.8em;">From: {sender}</span>
                        <span style="background: #333; padding: 2px 8px; border-radius: 4px; color: #bbb; font-size: 0.8em;">{key}</span>
                    </div>
                    <div style="color: #ccc; font-style: italic; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 15px;">
                        "{snippet}..."
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # --- SECRETARY MODE FEATURES ---
                    
                    # 1. INPUT
                    user_intent = st.text_input(
                        "How should we reply?", 
                        placeholder="e.g. Accept the offer and ask about remote work...", 
                        key=f"intent_{unique_suffix}"
                    )
                    
                    # 2. GENERATE BUTTON
                    if st.button("✨ Draft Reply", key=f"gen_{unique_suffix}"):
                        if user_intent:
                            with st.spinner("AI is writing..."):
                                res = api_post("/action/generate_reply", {"msg_id": msg_id, "intent": user_intent})
                                if res and res.status_code == 200:
                                    st.session_state[f"draft_{msg_id}"] = res.json()["reply"]
                                    st.rerun()
                                    
                    # 3. PREVIEW & SEND BOX
                    if f"draft_{msg_id}" in st.session_state:
                        st.markdown("### 📝 Edit & Send")
                        final_body = st.text_area(
                            "Preview:", 
                            value=st.session_state[f"draft_{msg_id}"], 
                            height=150, 
                            key=f"edit_{unique_suffix}"
                        )
                        
                        col_send, col_discard = st.columns([1, 4])
                        with col_send:
                            if st.button("🚀 Send Now", key=f"send_{unique_suffix}", type="primary"):
                                with st.spinner("Sending..."):
                                    res = api_post("/action/send_custom", {"msg_id": msg_id, "body": final_body})
                                    if res and res.status_code == 200:
                                        st.toast("Sent! 🚀", icon="✅")
                                        del st.session_state[f"draft_{msg_id}"]
                                        st.rerun()
                                    else: st.error("Failed.")
                        with col_discard:
                            if st.button("❌ Discard", key=f"disc_{unique_suffix}"):
                                del st.session_state[f"draft_{msg_id}"]
                                st.rerun()
                    
                    st.divider()

                    # --- FOOTER ACTIONS (Trash & Open) ---
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        if st.button("🗑️ Trash", key=f"tr_{unique_suffix}"):
                            api_get(f"/action/trash/{msg_id}")
                            st.toast("Deleted!", icon="🗑️")
                            st.rerun()
                    with c2:
                        st.link_button("↗ Open Gmail", f"https://mail.google.com/mail/u/0/#inbox/{msg_id}")
