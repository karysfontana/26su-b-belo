import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    BELO is a restaurant reviewing application that allows users to post reviews, 
    make reservations, follow their friends, and view the restaurants their friends reviewed.
    BELO centers reviews around your social graph: instead of trusting random strangers, 
    you can see ratings from your friends that are stored in the app, making recommendations
    far more reliable and relevant. Managers can also edit their restaurant information, 
    view reviews, and accept reservations.

    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
