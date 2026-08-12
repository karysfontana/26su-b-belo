import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests 
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Edit Details')

# API endpoint
API_URL = "http://web-api:4000"

manager_id = st.session_state.get("manager_id")

# Get restaurant ID from manager ID 
restaurant_id = st.session_state.get("restaurant_id")

if restaurant_id is None:
    # for the sake of viewing while bob data isn't set. 
    st.error("No restaurant is associated with this manager.")
    st.stop()
    # restaurant_id = 1000

# Helper functions to get data 
# Get restaurant data 
def get_restaurant(restaurant_id):
    response = requests.get(
        f"{API_URL}/restaurants/restaurants/{restaurant_id}"
    )

    if response.status_code == 200:
        return response.json()

    st.error(f"Could not load restaurant: {response.text}")
    return None

# Load restaurant data 
restaurant = get_restaurant(restaurant_id)

if restaurant is None:
    st.stop()

def get_cuisine(cuisine):
    response = requests.get(
        f"{API_URL}/restaurants/{cuisine}"
    )

    if response.status_code == 200: 
        return response.json()

    st.error(f"Could not load cuisine: {response.text}")
    return None
