import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Customer, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('Find Restaurants',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/01_Restaurant_Viz.py')

if st.button('View My Reservations',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/02_Customer_Reservations.py')

if st.button('View My Profile',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/03_Customer_Profile.py')

if st.button('Search Reviews',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/04_Customer_Reviews.py')

if st.button('Create a New Review',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/05_Customer_Create_Review.py')

if st.button('Edit a Review',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/06_Customer_Edit_Review.py')