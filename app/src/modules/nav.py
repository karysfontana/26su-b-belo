# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: customer -----------------------------------------------------

def customer_home_nav():
    st.sidebar.page_link("pages/00_Customer_Home.py", label="Search Restaurants", icon="🔍")


def restaurant_viz_nav():
    st.sidebar.page_link("pages/01_Restaurant_Viz.py", label="Restaurant Viz", icon="📊")


def customer_reservations_nav():
    st.sidebar.page_link("pages/02_Customer_Reservations.py", label="My Reservations", icon="📅")


def customer_profile_nav():
    st.sidebar.page_link("pages/03_Customer_Profile.py", label="My Profile", icon="👤")


def customer_reviews_nav():
    st.sidebar.page_link("pages/04_Customer_Reviews.py", label="My Reviews", icon="⭐")


def customer_create_review_nav():
    st.sidebar.page_link("pages/05_Customer_Create_Review.py", label="Add a Review", icon="➕")


# 06_Customer_Edit_Review.py intentionally has no nav link — same pattern as
# the template's 16_NGO_Profile.py: reached via a button/session_state from
# 04_Customer_Reviews.py, not a standalone sidebar destination.


# ---- Role: manager -----------------------------------------------------

def manager_home_nav():
    st.sidebar.page_link("pages/10_Manager_Home.py", label="Manager Dashboard", icon="🍔")


def waitlist_nav():
    st.sidebar.page_link("pages/14_Waitlist.py", label="Waitlist", icon="🕒")


def add_waitlist_nav():
    st.sidebar.page_link("pages/15_Add_Waitlist.py", label="Add Walk-In", icon="➕")


def manager_restaurant_nav():
    st.sidebar.page_link("pages/17_Manager_Restaurant.py", label="Restaurant Details", icon="📝")


def manager_reservations_nav():
    st.sidebar.page_link("pages/32_manager_reservation.py", label="Reservations", icon="📅")


def seating_chart_nav():
    st.sidebar.page_link("pages/31_seatingchart.py", label="Seating Chart", icon="🪑")


# ---- Role: admin ------------------------------------------------

def LogsNav():
    st.sidebar.page_link("pages/23_Logs.py", label="Activity Log", icon="🗒️")


def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🖥️")


def admin_claims_nav():
    st.sidebar.page_link(
        "pages/24_Admin_Claims.py", label="Claims", icon="📋"
    )

def admin_accounts_nav():
    st.sidebar.page_link(
        "pages/22_Admin_Accounts_Review.py", label="Accounts", icon="👥"
    )

def admin_logs_nav():
    st.sidebar.page_link(
        "pages/23_Logs.py", label="Audit Logs", icon="📋"
    )

def customer_friends_nav():
    st.sidebar.page_link("pages/33_customer_friend.py", label="Friends reviews", icon="👥")

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=650)  

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "customer":
            customer_home_nav()
            restaurant_viz_nav()
            customer_reservations_nav()
            customer_profile_nav()
            customer_reviews_nav()
            customer_create_review_nav()
            customer_friends_nav()

        if st.session_state["role"] == "manager":
            manager_home_nav()
            manager_restaurant_nav()
            manager_reservations_nav()
            waitlist_nav()
            add_waitlist_nav()
            seating_chart_nav()

        # NOTE: confirm this matches exactly what Home.py sets for the
        # admin login button — it must be either "admin" or "administrator"
        # in BOTH places, not one of each, or this block silently never runs.
        if st.session_state["role"] == "admin":
            admin_home_nav()
            admin_claims_nav()
            admin_accounts_nav()
            admin_logs_nav()


    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")