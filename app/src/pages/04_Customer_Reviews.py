import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Restaurant Reviews')

# --- Fetch restaurant list for the search/select dropdown ---
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

# Map restaurant name -> ID for the dropdown
restaurant_options = {r['name']: r['RestaurantID'] for r in restaurant_list}

selected_name = st.selectbox("Search for a restaurant", sorted(restaurant_options.keys()))
selected_id = restaurant_options[selected_name]

st.divider()

# --- Fetch reviews for the selected restaurant ---
try:
    reviews_resp = requests.get(f"http://web-api:4000/reviews/restaurants/{selected_id}/reviews")
    reviews_resp.raise_for_status()
    reviews = reviews_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching reviews for restaurant {selected_id}: {e}")
    st.error("Could not load reviews. Please try again later.")
    reviews = []

st.subheader(f"Reviews for {selected_name}")

if reviews:
    df = pd.DataFrame(reviews)
    df['avgRating'] = df['avgRating'].round(2)

    st.dataframe(
        df[['reviewID', 'comment', 'avgRating', 'createdAt', 'Status']],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --- Ratings breakdown for a selected review ---
    st.subheader("View Ratings Breakdown")
    review_id = st.selectbox("Select a review to see its food/service/vibe breakdown", df['reviewID'].tolist())

    try:
        detail_resp = requests.get(f"http://web-api:4000/reviews/reviews/{review_id}")
        detail_resp.raise_for_status()
        detail = detail_resp.json()

        st.write(f"**Comment:** {detail['comment']}")

        if detail.get('ratings'):
            ratings_df = pd.DataFrame(detail['ratings'])
            st.dataframe(ratings_df, use_container_width=True, hide_index=True)
        else:
            st.write("No rating breakdown available for this review.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching review {review_id} detail: {e}")
        st.error("Could not load review details.")
else:
    st.info(f"No reviews yet for {selected_name}.")