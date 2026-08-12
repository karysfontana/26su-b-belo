import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Audit Log')

# --- Fetch admin list for the filter dropdown ---
try:
    admins_resp = requests.get("http://web-api:4000/admin/admins")
    admins_resp.raise_for_status()
    admins_list = admins_resp.json()
    admin_options = {"All": None}
    admin_options.update({f"{a['firstname']} {a['lastname']}": a['adminID'] for a in admins_list})
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching admins: {e}")
    st.error("Could not load admin list.")
    admin_options = {"All": None}

selected_admin_name = st.selectbox("Filter by admin", list(admin_options.keys()))
selected_admin_id = admin_options[selected_admin_name]

# --- Fetch logs ---
params = {} if selected_admin_id is None else {"adminID": selected_admin_id}

try:
    logs_resp = requests.get("http://web-api:4000/admin/logs", params=params)
    logs_resp.raise_for_status()
    logs = logs_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching logs: {e}")
    st.error("Could not load audit log.")
    logs = []

if logs:
    df = pd.DataFrame(logs)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No log entries found.")