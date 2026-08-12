import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests 
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Edit Details')

# API endpoint
API_URL = "http://web-api:4000"

manager_id = st.session_state.get("managerID")

if manager_id is None: 
    #st.error("No managerID associated with this account.")
   # st.stop()
   manager_id = 1000

# Get restaurants associated with this manager
try:
    response = requests.get(
        f"{API_URL}/managers/managers/{manager_id}/restaurants",
        timeout=10
    )

    if response.status_code != 200:
        st.error(f"Failed to get restaurants: {response.status_code}")
        st.write(response.text)
        st.stop()

    manager_restaurants = response.json()

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to API: {e}")
    st.stop()


# Make sure we actually received restaurants
if not manager_restaurants:
    st.warning("No restaurants were found for this manager.")
    st.stop()

# Debug temporarily
st.write("Manager ID:", manager_id)
st.write("Restaurants returned by API:", manager_restaurants)
# API Helper functions 

# Get restaurants from managerID
def get_manager_restaurants(manager_id):
    try:
        response = requests.get(
            f"{API_URL}/managers/{manager_id}/restaurants",
            timeout=10
        )

        if response.status_code != 200:
            logger.error(
                "Failed to get manager restaurants: "
                f"{response.status_code} - {response.text}"
            )
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return None

# Get restaurant details
def get_restaurant(restaurant_id):
    try:
        response = requests.get(
            f"{API_URL}/restaurants/restaurants/{restaurant_id}",
            timeout=10
        )

        if response.status_code != 200:
            logger.error(
                "Failed to get restaurant: "
                f"{response.status_code} - {response.text}"
            )
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return None

# Get cuisine tags 
def get_restaurant_cuisines(restaurant_id):
    try:
        response = requests.get(
            f"{API_URL}/restaurants/{restaurant_id}/cuisines",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Could not load restaurant cuisines. "
            f"Server returned {response.status_code}."
        )
        logger.error(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API: {e}")
        logger.exception(e)

    return []

# Update restaurant details
def update_restaurant(restaurant_id, data):
    try:
        response = requests.put(
            f"{API_URL}/restaurants/{restaurant_id}",
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return True, response.json()

        logger.error(
            f"Restaurant update failed: "
            f"{response.status_code} - {response.text}"
        )

        try:
            error_message = response.json().get(
                "error",
                "Unknown error"
            )
        except Exception:
            error_message = response.text

        return False, error_message

    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return False, str(e)

restaurants = get_manager_restaurants(manager_id)

if not restaurants:
    st.info("You do not currently have any restaurants associated with your account.")
    st.stop()


restaurant_options = {
    restaurant["name"]: restaurant["RestaurantID"]
    for restaurant in restaurants
}

# Select restaurant 
selected_restaurant_name = st.selectbox(
    "Select a restaurant to edit",
    options=list(restaurant_options.keys())
)

restaurant_id = restaurant_options[selected_restaurant_name]


restaurant = get_restaurant(restaurant_id)

if restaurant is None:
    st.stop()

current_cuisines = get_restaurant_cuisines(restaurant_id)