import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Find Restaurants')

# API endpoints
API_URL = "http://web-api:4000/restaurants/restaurants"
CUISINE_TAGS_URL = "http://web-api:4000/restaurants/cuisinetags"

# --- Fetch cuisine tags for the filter dropdown ---
try:
    cuisine_resp = requests.get(CUISINE_TAGS_URL)
    cuisine_resp.raise_for_status()
    cuisine_tags = cuisine_resp.json()
    cuisine_options = ["All"] + sorted([c['CuisineType'] for c in cuisine_tags])
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching cuisine tags: {e}")
    cuisine_options = ["All"]

# --- Filters ---
col1, col2, col3 = st.columns(3)

with col1:
    cuisine_filter = st.selectbox("Cuisine", cuisine_options)

with col2:
    price_filter = st.selectbox("Price Range", ["All", "$", "$$", "$$$", "$$$$"])

with col3:
    city_filter = st.text_input("City", "")

# --- Build query params based on filters ---
params = {}
if cuisine_filter != "All":
    params['cuisine'] = cuisine_filter
if price_filter != "All":
    params['priceRange'] = price_filter
if city_filter:
    params['city'] = city_filter

# --- Fetch restaurants ---
try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    restaurants = response.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching restaurants: {e}")
    st.error("Could not load restaurants. Please try again later.")
    restaurants = []

if restaurants:
    df = pd.DataFrame(restaurants)

    # --- Sorting controls ---
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox("Sort by", options=df.columns.tolist(), index=df.columns.get_loc('name'))
    with sort_col2:
        sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

    df = df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No restaurants found matching your filters.")