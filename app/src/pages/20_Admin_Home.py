import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Admin Home')

# Flask API URL
API_URL = "http://web-api:4000/admin"

# Get the admins and all the claims
admins = requests.get(f"{API_URL}/admins").json()
claims = requests.get(f"{API_URL}/claims").json()

# Pick which admin we are acting as, and remember it for the other admin pages
names = {f"{a['firstname']} {a['lastname']}": a['adminID'] for a in admins}
choice = st.selectbox("Acting as", list(names.keys()))
admin_id = names[choice]
st.session_state["admin_id"] = admin_id

st.divider()

# Pending claims are not assigned to anyone yet, so that number is the same
# for every admin. Resolved claims are stamped with who handled them.
pending = [c for c in claims if c["status"] == "pending"]
mine = [c for c in claims if c["adminReviewed"] == admin_id]

col1, col2 = st.columns(2)
col1.metric("Claims waiting for review", len(pending))
col2.metric(f"Resolved by {choice}", len(mine))

st.divider()

st.write("### Claims waiting")
st.dataframe(
    pd.DataFrame(pending)[["claimID", "restaurantName", "dateSubmitted"]],
    use_container_width=True,
    hide_index=True
)