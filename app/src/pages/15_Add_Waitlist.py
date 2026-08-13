import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Add to Waitlist')

# Manager's restaurant ID — assumed stored in session state at login
restaurant_id = st.session_state['restaurant_id']
manager_id = st.session_state.get('manager_id')  # optional, for ManagerEdit tracking

with st.form("add_waitlist_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name (optional)")
    party_size = st.number_input("Party Size", min_value=1, step=1, value=2)

    submitted = st.form_submit_button("Add to Waitlist")

    if submitted:
        if not first_name.strip():
            st.error("First name is required.")
        else:
            payload = {
                "restaurantID": restaurant_id,
                "firstName": first_name,
                "partySize": party_size
            }
            if last_name.strip():
                payload["lastName"] = last_name
            if manager_id:
                payload["managerID"] = manager_id

            try:
                add_resp = requests.post("http://web-api:4000/waitlist/waitlist", json=payload)
                add_resp.raise_for_status()
                result = add_resp.json()
                st.success(f"{first_name} added to the waitlist (entry #{result['entryID']}).")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error adding to waitlist: {e}")
                st.error("Could not add party to the waitlist. Please try again.")