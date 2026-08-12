import streamlit as st
import requests
from modules.nav import SideBarLinks
 
st.set_page_config(layout='wide')
SideBarLinks()
 
API_URL = "http://web-api:4000/admin"
 
st.title("Admin Action Log")
st.caption("Every admin action, most recent first.")
 

# Optional filter by admin
try:
    admins_resp = requests.get(f"{API_URL}/admins")
    admins = admins_resp.json() if admins_resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    admins = []
 
admin_options = {"All Admins": None}
admin_options.update({f"{a['firstname']} {a['lastname']}": a['adminID'] for a in admins})
 
selected_admin_name = st.selectbox("Filter by admin", list(admin_options.keys()))
selected_admin_id = admin_options[selected_admin_name]
 

# Log list
# ---------------------------------------------------------------
try:
    params = {} if selected_admin_id is None else {"adminID": selected_admin_id}
    logs_resp = requests.get(f"{API_URL}/logs", params=params)
    logs = logs_resp.json() if logs_resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    logs = []
 
st.write(f"**{len(logs)} log entries**")
 
if not logs:
    st.write("No log entries match this filter.")
else:
    for entry in logs:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(entry['action'])
            with col2:
                st.caption(entry['date'])
            st.caption(f"By {entry.get('firstname', '')} {entry.get('lastname', '')}")