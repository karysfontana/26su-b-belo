import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Write a Review')

# Customer ID stored in session state at login
customer_id = st.session_state['customer_id']

# --- Fetch restaurant list for the dropdown ---
try:
    rest_resp = requests.get("http://web-api:4000/restaurants/restaurants")
    rest_resp.raise_for_status()
    restaurant_list = rest_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching restaurants: {e}")
    st.error("Could not load restaurant list. Please try again later.")
    restaurant_list = []

if not restaurant_list:
    st.info("No restaurants available.")
    st.stop()

restaurant_options = {r['name']: r['RestaurantID'] for r in restaurant_list}

# --- Review form ---
with st.form("new_review_form"):
    selected_name = st.selectbox("Restaurant", sorted(restaurant_options.keys()))
    comment = st.text_area("Your review", placeholder="Tell others about your experience...")

    st.write("Rate your experience:")
    col1, col2, col3 = st.columns(3)
    with col1:
        food_rating = st.slider("Food", 1, 5, 3)
    with col2:
        service_rating = st.slider("Service", 1, 5, 3)
    with col3:
        vibe_rating = st.slider("Vibe", 1, 5, 3)

    submitted = st.form_submit_button("Submit Review")

    if submitted:
        if not comment.strip():
            st.error("Please write a comment before submitting.")
        else:
            selected_id = restaurant_options[selected_name]
            payload = {
                "customerID": customer_id,
                "restaurantID": selected_id,
                "comment": comment,
                "ratings": {
                    "food": food_rating,
                    "service": service_rating,
                    "vibe": vibe_rating
                }
            }
            try:
                post_resp = requests.post("http://web-api:4000/reviews/reviews", json=payload)
                post_resp.raise_for_status()
                st.success(f"Review submitted for {selected_name}!")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error submitting review: {e}")
                st.error("Could not submit review. Please try again.")