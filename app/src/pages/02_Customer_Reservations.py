import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('My Reservations')
st.write(f"### Hi, {st.session_state['first_name']}.")

# API endpoint assumes customer ID is stored in session state after login
customer_id = 1012
API_URL = f"http://web-api:4000/reservations/customers/{customer_id}/reservations"

# --- Fetch reservations ---
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    reservations = response.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching reservations: {e}")
    st.error("Could not load your reservations. Please try again later.")
    reservations = []

if reservations:
    df = pd.DataFrame(reservations)

    # --- Optional status filter ---
    status_options = ["All"] + sorted(df['status'].unique().tolist())
    status_filter = st.selectbox("Filter by status", status_options)

    if status_filter != "All":
        df = df[df['status'] == status_filter]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # --- Cancel a reservation ---
    st.subheader("Cancel a Reservation")
    resv_ids = df['resvID'].tolist()

    if resv_ids:
        cancel_id = st.selectbox("Select reservation to cancel", resv_ids)

        if st.button("Cancel Reservation"):
            try:
                cancel_resp = requests.delete(f"http://web-api:4000/reservations/{cancel_id}")
                cancel_resp.raise_for_status()
                st.success(f"Reservation {cancel_id} cancelled.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error cancelling reservation {cancel_id}: {e}")
                st.error("Could not cancel reservation. Please try again.")
    else:
        st.write("No reservations to cancel.")
else:
    st.info("You have no reservations yet.")