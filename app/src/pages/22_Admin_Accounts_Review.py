import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Account Administration')
st.write(f"### Hi, {st.session_state['first_name']}.")

tab1, tab2, tab3 = st.tabs(["All Accounts", "Account Detail", "Suspend / Reinstate / Delete"])

# --- Tab 1: All accounts, filterable by status ---
with tab1:
    st.subheader("All User Accounts")

    status_filter = st.selectbox("Filter by status", ["All", "active", "suspended"], key="user_status_filter")
    params = {} if status_filter == "All" else {"status": status_filter}

    try:
        users_resp = requests.get("http://web-api:4000/users/users", params=params)
        users_resp.raise_for_status()
        users_list = users_resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching users: {e}")
        st.error("Could not load user accounts.")
        users_list = []

    if users_list:
        st.dataframe(pd.DataFrame(users_list), use_container_width=True, hide_index=True)
    else:
        st.info("No accounts match this filter.")

# --- Tab 2: Look up one account + who they follow ---
with tab2:
    st.subheader("Look Up an Account")

    lookup_id = st.number_input("User ID", min_value=1, step=1, key="user_lookup_id")

    if st.button("Look Up Account"):
        try:
            user_resp = requests.get(f"http://web-api:4000/users/users/{lookup_id}")
            if user_resp.status_code == 404:
                st.warning("Account not found.")
            else:
                user_resp.raise_for_status()
                user = user_resp.json()
                st.write(f"**User ID:** {user['UserID']}")
                st.write(f"**Status:** {user.get('status', 'N/A')}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user {lookup_id}: {e}")
            st.error("Could not load account.")

    st.divider()
    st.subheader("Accounts This User Follows")

    if lookup_id:
        try:
            follows_resp = requests.get(f"http://web-api:4000/users/users/{lookup_id}/follows")
            follows_resp.raise_for_status()
            follows = follows_resp.json()

            if follows:
                st.dataframe(pd.DataFrame(follows), use_container_width=True, hide_index=True)
            else:
                st.write("This user isn't following anyone.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching follows for user {lookup_id}: {e}")
            st.error("Could not load follows.")

# --- Tab 3: Suspend / reinstate / delete ---
with tab3:
    st.subheader("Change Account Status")

    target_id = st.number_input("User ID", min_value=1, step=1, key="status_change_id")
    new_status = st.selectbox("New Status", ["active", "suspended"], key="new_status_select")
    flagged_by = st.number_input("Flagged By (Admin ID, optional)", min_value=0, step=1, value=0, key="flagged_by")

    if st.button("Update Status"):
        payload = {"status": new_status}
        if flagged_by > 0:
            payload["flaggedBy"] = flagged_by

        try:
            update_resp = requests.put(f"http://web-api:4000/users/users/{target_id}", json=payload)
            if update_resp.status_code == 404:
                st.warning("Account not found.")
            else:
                update_resp.raise_for_status()
                st.success(f"User {target_id} status set to {new_status}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating status for user {target_id}: {e}")
            st.error("Could not update account status.")

    st.divider()
    st.subheader("Permanently Delete Account")
    st.warning("This action is permanent and cannot be undone.")

    delete_id = st.number_input("User ID to delete", min_value=1, step=1, key="user_delete_id")
    confirm_delete = st.checkbox("I understand this cannot be undone", key="confirm_delete_user")

    if st.button("Delete Account", disabled=not confirm_delete):
        try:
            del_resp = requests.delete(f"http://web-api:4000/users/users/{delete_id}")
            if del_resp.status_code == 404:
                st.warning("Account not found.")
            else:
                del_resp.raise_for_status()
                st.success(f"User {delete_id} deleted.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting user {delete_id}: {e}")
            st.error("Could not delete account.")