import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Edit Details')

# Flask API URL
API_URL = "http://localhost:4000"

restaurant_id = st.session_state.get("restaurant_id")

if restaurant_id is None:
    st.error("No restaurant is associated with this manager.")
    st.stop()

# Helper function to get restaurant data 
def get_restaurant(restaurant_id):
    response = requests.get(
        f"{API_URL}/restaurants/{restaurant_id}"
    )

    if response.status_code == 200:
        return response.json()

    st.error(f"Could not load restaurant: {response.text}")
    return None

# Load restaurant data 
restaurant = get_restaurant(restaurant_id)

if restaurant is None:
    st.stop()

current_cuisines = get_restaurant_cuisines(restaurant_id)
all_cuisines = get_all_cuisines()