import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from datetime import date, time, datetime
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('My Reservations')
st.write(f"### Hi, {st.session_state['first_name']}.")

# API endpoint assumes customer ID is stored in session state after login
customer_id = st.session_state['customer_id']
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
                cancel_resp = requests.delete(f"http://web-api:4000/reservations/reservations/{cancel_id}")
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

st.divider()

# --- Create a new reservation ---
st.subheader("Make a New Reservation")

# Fetch restaurant list for the dropdown
try:
    rest_resp = requests.get("http://web-api:4000/restaurants/restaurants")
    rest_resp.raise_for_status()
    restaurant_list = rest_resp.json()
    restaurant_options = {r['name']: r['RestaurantID'] for r in restaurant_list}
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching restaurants: {e}")
    st.error("Could not load restaurant list.")
    restaurant_options = {}

if restaurant_options:
    with st.form("create_reservation_form"):
        selected_name = st.selectbox("Restaurant", sorted(restaurant_options.keys()))
        resv_date = st.date_input("Date", min_value=date.today())
        resv_time = st.time_input("Time", value=time(19, 0))
        party_size = st.number_input("Party Size", min_value=1, step=1, value=2)
        special_request = st.text_area("Special Requests (optional)", placeholder="e.g. window seat, allergies...")

        submitted = st.form_submit_button("Request Reservation")

        if submitted:
            selected_id = restaurant_options[selected_name]
            resv_datetime = datetime.combine(resv_date, resv_time)

            payload = {
                "date": resv_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "partySize": int(party_size),
                "customerID": customer_id,
                "restaurantID": selected_id
            }
            if special_request.strip():
                payload["request"] = special_request.strip()

            try:
                create_resp = requests.post("http://web-api:4000/reservations/reservations", json=payload)
                create_resp.raise_for_status()
                result = create_resp.json()
                st.success(f"Reservation requested (ID {result['resvID']}). It's pending approval.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error creating reservation: {e}")
                st.error("Could not create reservation. Please try again.")
else:
    st.info("No restaurants available to book.")