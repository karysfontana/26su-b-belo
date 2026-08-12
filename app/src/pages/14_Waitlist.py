import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Waitlist')

# Manager's restaurant ID — assumed stored in session state at login
restaurant_id = st.session_state['restaurant_id']

include_seated = st.checkbox("Include already-seated parties (full history)")

params = {"includeSeated": "true"} if include_seated else {}

try:
    wl_resp = requests.get(
        f"http://web-api:4000/waitlist/restaurants/{restaurant_id}/waitlist",
        params=params
    )
    wl_resp.raise_for_status()
    waitlist_entries = wl_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching waitlist for restaurant {restaurant_id}: {e}")
    st.error("Could not load the waitlist. Please try again later.")
    waitlist_entries = []

if waitlist_entries:
    df = pd.DataFrame(waitlist_entries)
    df['arrivalTime'] = pd.to_datetime(df['arrivalTime'])
    df = df.sort_values(by='arrivalTime', ascending=True)

    # --- Date filter dropdown ---
    available_dates = sorted(df['arrivalTime'].dt.date.unique())
    date_options = ["All Dates"] + [d.strftime("%Y-%m-%d") for d in available_dates]
    selected_date = st.selectbox("Filter by date", date_options)

    if selected_date != "All Dates":
        selected_date_obj = pd.to_datetime(selected_date).date()
        df = df[df['arrivalTime'].dt.date == selected_date_obj]

    display_df = df[['entryID', 'firstName', 'lastName', 'partySize', 'arrivalTime', 'seatedTime']]

    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"No waitlist entries for {selected_date}.")
else:
    st.info("No one is currently waiting.")