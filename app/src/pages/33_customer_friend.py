import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"
customer_id = st.session_state['customer_id']

st.title("Your Friends")

try:
    profile_resp = requests.get(f"{API_URL}/customers/customers/{customer_id}")
    profile = profile_resp.json() if profile_resp.status_code == 200 else {}
    user_id = profile.get('userID')
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    user_id = None

if not user_id:
    st.warning("Couldn't load your profile.")
    st.stop()

# Who you follow
st.subheader("People You Follow")

try:
    follows_resp = requests.get(f"{API_URL}/users/users/{user_id}/follows")
    follows = follows_resp.json() if follows_resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    follows = []

if not follows:
    st.write("You're not following anyone yet.")
else:
    for f in follows:
        st.write(f"• {f.get('firstname', '')} {f.get('lastname', '')}")

st.write("---")

# Their recent reviews / ratings
st.subheader("Recent Reviews from Your Circle")

try:
    friends_resp = requests.get(f"{API_URL}/reviews/reviews/friends/{user_id}")
    friends_reviews = friends_resp.json() if friends_resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    friends_reviews = []

if not friends_reviews:
    st.write("None of the people you follow have posted reviews yet.")
else:
    for rv in friends_reviews:
        with st.container(border=True):
            st.write(f"**{rv['firstname']} {rv['lastname']}** reviewed **{rv['restaurantName']}**")
            st.write(rv['comment'])

            rating_cols = st.columns(3)
            for i, r in enumerate(rv.get('ratings', [])):
                with rating_cols[i % 3]:
                    st.metric(r['ratingType'], f"{r['rate']} ★")

            st.caption(rv['createdAt'])