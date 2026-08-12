import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Manager, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('View Waitlist',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/14_Waitlist.py')

if st.button('Add to Waitlist',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/15_Add_Waitlist.py')

if st.button('View Seating Chart',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/11_Prediction.py')

if st.button('View Reservations',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/12_API_Test.py')

if st.button('Edit Restaurant Information',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/17_Manager_Restaurant.py')
