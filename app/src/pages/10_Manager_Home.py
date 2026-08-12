import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Manager, {st.session_state['first_name']}.")

API_URL = "http://web-api:4000"
manager_id = st.session_state.get('manager_id')

# ---------------------------------------------------------------
# Restaurant picker — REQUIRED before any other manager page will
# work, since 17_Manager_Restaurant.py, 14_Waitlist.py, and
# 31_seatingchart.py all read restaurant_id from session_state.
# ---------------------------------------------------------------
try:
    resp = requests.get(f"{API_URL}/managers/managers/{manager_id}/restaurants")
    my_restaurants = resp.json() if resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    my_restaurants = []

if not my_restaurants:
    st.warning("No restaurants found for this manager account.")
    st.stop()

restaurant_names = {r['name']: r['RestaurantID'] for r in my_restaurants}

current_id = st.session_state.get('restaurant_id')
default_name = next((name for name, rid in restaurant_names.items() if rid == current_id),
                     list(restaurant_names.keys())[0])

selected_name = st.selectbox("Which restaurant are you managing?",
                               list(restaurant_names.keys()),
                               index=list(restaurant_names.keys()).index(default_name))
st.session_state['restaurant_id'] = restaurant_names[selected_name]

st.write('### What would you like to do today?')

if st.button('View Waitlist',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/14_Waitlist.py')

if st.button('Add to Waitlist',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/15_Add_Waitlist.py')

if st.button('View / Edit Seating Chart',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/31_seatingchart.py')

# NOTE: there is no dedicated "Manager Reservations" page in the repo yet
# (the old button here pointed at 12_API_Test.py, a template leftover).
# Removed until a real reservations page exists — add it back once one
# is built, pointing at the correct file.

if st.button('View Reservations',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/32_manager_reservation.py')

if st.button('Edit Restaurant Information',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/17_Manager_Restaurant.py')