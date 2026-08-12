import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('My Profile')

# Customer ID stored in session state at login (see note below)
customer_id = 1000
API_URL = f"http://web-api:4000/customers/customers/{customer_id}"

# --- Fetch customer profile ---
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    customer = response.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching customer profile: {e}")
    st.error("Could not load your profile. Please try again later.")
    customer = None

if customer:
    st.write(f"### Hi, {customer['firstname']}.")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("First Name", value=customer['firstname'], disabled=True)
        st.text_input("Last Name", value=customer['lastname'], disabled=True)

    with col2:
        st.text_input("Account Status", value=customer['status'], disabled=True)
        st.text_input("Member Since", value=str(customer['signUpDate']), disabled=True)

    st.divider()

    # --- Edit profile ---
    st.subheader("Edit Profile")

    with st.form("edit_profile_form"):
        new_firstname = st.text_input("First Name", value=customer['firstname'])
        new_lastname = st.text_input("Last Name", value=customer['lastname'])
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            payload = {"firstname": new_firstname, "lastname": new_lastname}
            try:
                update_resp = requests.put(f"http://web-api:4000/customers/customers/{customer_id}", json=payload)
                update_resp.raise_for_status()
                st.success("Profile updated.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error updating customer profile: {e}")
                st.error("Could not update profile. Please try again.")

                st.divider()

    # --- Following list ---
    st.subheader("People You Follow")

    user_id = 1000  # the User table ID, distinct from customer_id

    try:
        follows_resp = requests.get(f"http://web-api:4000/users/users/{user_id}/follows")
        follows_resp.raise_for_status()
        follows = follows_resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching follows for user {user_id}: {e}")
        st.error("Could not load your following list.")
        follows = []

    if follows:
        follows_df = pd.DataFrame(follows)
        st.dataframe(follows_df, use_container_width=True, hide_index=True)
    else:
        st.write("You're not following anyone yet.")
else:
    st.info("No profile found.")

    