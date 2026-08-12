import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Edit My Reviews')

# Customer ID stored in session state at login
customer_id = 1000

# --- Fetch this customer's reviews ---
try:
    reviews_resp = requests.get("http://web-api:4000/reviews/reviews", params={"customerID": customer_id})
    reviews_resp.raise_for_status()
    my_reviews = reviews_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching customer reviews: {e}")
    st.error("Could not load your reviews. Please try again later.")
    my_reviews = []

if not my_reviews:
    st.info("You haven't written any reviews yet.")
    st.stop()

# --- Select which review to edit ---
review_options = {f"Review #{r['reviewID']} (Restaurant {r['RestaurantID']})": r['reviewID'] for r in my_reviews}
selected_label = st.selectbox("Select a review to edit", list(review_options.keys()))
selected_review_id = review_options[selected_label]

st.divider()

# --- Fetch full detail (comment + ratings breakdown) for the selected review ---
try:
    detail_resp = requests.get(f"http://web-api:4000/reviews/reviews/{selected_review_id}")
    detail_resp.raise_for_status()
    review_detail = detail_resp.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching review {selected_review_id} detail: {e}")
    st.error("Could not load review details.")
    st.stop()

# Turn ratings list into a dict keyed by ratingType for easy lookup
existing_ratings = {r['ratingType']: r['rate'] for r in review_detail.get('ratings', [])}

# --- Edit form ---
with st.form("edit_review_form"):
    new_comment = st.text_area("Your review", value=review_detail.get('comment', ''))

    st.write("Update your ratings:")
    col1, col2, col3 = st.columns(3)
    with col1:
        food_rating = st.slider("Food", 1, 5, int(existing_ratings.get('food', 3)))
    with col2:
        service_rating = st.slider("Service", 1, 5, int(existing_ratings.get('service', 3)))
    with col3:
        vibe_rating = st.slider("Vibe", 1, 5, int(existing_ratings.get('vibe', 3)))

    submitted = st.form_submit_button("Save Changes")

    if submitted:
        if not new_comment.strip():
            st.error("Review comment cannot be empty.")
        else:
            payload = {
                "comment": new_comment,
                "ratings": {
                    "food": food_rating,
                    "service": service_rating,
                    "vibe": vibe_rating
                }
            }
            try:
                put_resp = requests.put(f"http://web-api:4000/reviews/reviews/{selected_review_id}", json=payload)
                put_resp.raise_for_status()
                st.success("Review updated.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error updating review {selected_review_id}: {e}")
                st.error("Could not update review. Please try again.")

st.divider()

# --- Delete review ---
st.subheader("Delete This Review")
confirm_delete = st.checkbox("I'm sure I want to delete this review", key=f"confirm_delete_{selected_review_id}")

if st.button("Delete Review", disabled=not confirm_delete):
    try:
        del_resp = requests.delete(f"http://web-api:4000/reviews/reviews/{selected_review_id}")
        del_resp.raise_for_status()
        st.success("Review deleted.")
        st.rerun()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting review {selected_review_id}: {e}")
        st.error("Could not delete review. Please try again.")