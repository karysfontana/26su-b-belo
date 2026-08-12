import logging
logger = logging.getLogger(__name__)
from datetime import datetime, time
import streamlit as st
import requests 
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header('Edit Details')

# Manager's restaurant ID — assumed stored in session state at login
restaurant_id = st.session_state['restaurant_id']

# API endpoint
API_URL = "http://web-api:4000"

# Get restaurant details 
if restaurant_id is None:
    st.error(
        "No restaurant has been selected. "
        "Please return to the Manager menu and select a restaurant."
    )
    st.stop()

st.write("Selected Restaurant ID:", restaurant_id)

try:
    response = requests.get(
        f"{API_URL}/restaurants/restaurants/{restaurant_id}",
        timeout=10
    )
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {e}")
    st.stop()


if response.status_code != 200:
    st.error(
        f"Could not load restaurant details. "
        f"API returned {response.status_code}"
    )
    st.code(response.text)
    st.stop()

restaurant = response.json()

# Heading for restaurant 
st.subheader(
    restaurant.get("name", "Restaurant")
)
st.caption(
    f"Restaurant ID: {restaurant_id}"
)

# Get cuisine tags (current)
try:
    cuisine_response = requests.get(
        f"{API_URL}/restaurants/restaurants/"
        f"{restaurant_id}/cuisines",
        timeout=10
    )
    if cuisine_response.status_code == 200:
        current_cuisines = cuisine_response.json()
    else:
        current_cuisines = []
except requests.exceptions.RequestException:
    current_cuisines = []

# Get all cuisines 
try:
    all_cuisine_response = requests.get(
        f"{API_URL}/restaurants/cuisinetags",
        timeout=10
    )
    if all_cuisine_response.status_code == 200:
        all_cuisines = all_cuisine_response.json()
    else:
        all_cuisines = []
except requests.exceptions.RequestException:
    all_cuisines = []

# Current info. 
current_name = restaurant.get("name", "")
current_street = restaurant.get("street", "")
current_price = restaurant.get("priceRange", "$")

# Convert time for aesthetics (HH:MM)
try:
    current_open_time = datetime.strptime(
        str(restaurant.get("openTime", "09:00:00")),
        "%H:%M:%S"
    ).time()
except ValueError:
    current_open_time = time(9, 0)
try:
    current_close_time = datetime.strptime(
        str(restaurant.get("closeTime", "22:00:00")),
        "%H:%M:%S"
    ).time()
except ValueError:
    current_close_time = time(22, 0)

# Lookup cuisines
cuisine_lookup = {}

for cuisine in all_cuisines:
    cuisine_id = cuisine.get("cuisineID")
    cuisine_name = cuisine.get("CuisineType")
    if cuisine_id is not None and cuisine_name:
        cuisine_lookup[cuisine_name] = cuisine_id


# Current cuisine names
current_cuisine_names = []

for cuisine in current_cuisines:
    cuisine_name = cuisine.get("CuisineType")
    if cuisine_name:
        current_cuisine_names.append(cuisine_name)

# Edit restaurant form 
st.divider()
st.subheader("Restaurant Information")

with st.form("restaurant_edit_form"):
    col1, col2 = st.columns(2)
    # Basic info. 
    with col1:
        name = st.text_input(
            "Restaurant Name",
            value=current_name
        )
        street = st.text_input(
            "Street Address",
            value=current_street
        )
        price_options = [
            "$",
            "$$",
            "$$$",
            "$$$$"
        ]
        if current_price not in price_options:
            current_price = "$"
        price_range = st.selectbox(
            "Price Range",
            options=price_options,
            index=price_options.index(current_price)
        )
    # Hours
    with col2:
        open_time = st.time_input(
            "Opening Time",
            value=current_open_time
        )
        close_time = st.time_input(
            "Closing Time",
            value=current_close_time
        )
    # Cuisine
    st.divider()

    st.subheader("Cuisine")
    selected_cuisines = st.multiselect(
        "Cuisine Tags",
        options=list(cuisine_lookup.keys()),
        default=current_cuisine_names
    )
    # Save button
    st.divider()
    save = st.form_submit_button(
        "Save Changes",
        type="primary",
        use_container_width=True
    )

# Save changes
if save:
    if not name.strip():
        st.error("Restaurant name cannot be empty.")
        st.stop()
    if not street.strip():
        st.error("Street address cannot be empty.")
        st.stop()
    if open_time >= close_time:
        st.error(
            "Closing time must be later than opening time."
        )
        st.stop()
    # Update 
    update_data = {
        "name": name.strip(),
        "openTime": open_time.strftime("%H:%M:%S"),
        "closeTime": close_time.strftime("%H:%M:%S"),
        "street": street.strip(),
        "priceRange": price_range
    }
    try:
        update_response = requests.put(
            f"{API_URL}/restaurants/restaurants/{restaurant_id}",
            json=update_data,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        st.error(
            f"Error connecting to the API: {e}"
        )
        st.stop()
    if update_response.status_code != 200:
        try:
            error_message = update_response.json().get(
                "error",
                update_response.text
            )
        except Exception:
            error_message = update_response.text
        st.error(
            f"Could not update restaurant: "
            f"{error_message}"
        )
        st.stop()
