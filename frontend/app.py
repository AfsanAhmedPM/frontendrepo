import streamlit as st
import requests
import html

BACKEND_URL = "https://inbox-intelligence.onrender.com"

st.set_page_config(page_title="Inbox Command Center", page_icon="⚡", layout="wide")

# --- AUTH LOGIC ---
# 1. Check if token came from URL (Redirect)
if "token" in st.query_params:
    st.session_state["auth_token"] = st.query_params["token"]
    # Clear URL to look clean
    st.query_params.clear()
    st.rerun()

# 2. Helper to make authenticated requests
def api_get(endpoint):
    token = st.session_state.get("auth_token")
    if not token:
        return None
    try:
        # ✅ Send Token in Header
        headers = {"Authorization": f"Bearer {token}"}
        return requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=15)
    except:
        return None

# --- UI ---
with st.sidebar:
    st.title("⚡ Command Center")
    
    if "auth_token" not in st.session_state:
        st.link_button("🔐 Login", f"{BACKEND_URL}/auth/login", type="primary", use_container_width=True)
    else:
        st.success(f"Logged In")
        if st.button("🚪 Logout"):
            del st.session_state["auth_token"]
            st.rerun()
            
    if st.button("🔄 Sync", use_container_width=True):
        res = api_get("/result")
        if res and res.status_code == 200:
            st.session_state["data"] = res.json().get("categories", {})
            st.rerun()
        elif res and res.status_code == 401:
            st.error("Session expired. Please login again.")
            del st.session_state["auth_token"]

# --- MAIN DISPLAY ---
if "data" in st.session_state:
    # ... (Your existing display logic for tabs/emails goes here) ...
    st.write(st.session_state["data"]) # Temp debug display
    
    # Example Trash Button Logic with Auth
    # if st.button("Trash"):
    #     api_get(f"/action/trash/{msg_id}")

else:
    st.title("👋 Inbox Intelligence")
    st.info("Login to access your Multi-User SaaS.")
