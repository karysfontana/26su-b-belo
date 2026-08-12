import logging
logger = logging.getLogger(__name__)
import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Restaurant Administration')

# --- Acting-as admin selector (needed for resolving claims / writing logs) ---
try:
    admins_resp = requests.get("http://web-api:4000/admin/admins")
    admins_resp.raise_for_status()
    admins_list = admins_resp.json()
    admin_options = {f"{a['firstname']} {a['lastname']}": a['adminID'] for a in admins_list}
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching admins: {e}")
    st.error("Could not load admin list.")
    admin_options = {}

if admin_options:
    acting_admin_name = st.selectbox("Acting as", list(admin_options.keys()))
    acting_admin_id = admin_options[acting_admin_name]
else:
    acting_admin_id = None

st.divider()

tab1, tab_merge, tab2, tab3, tab4, tab5 = st.tabs([
    "Merged Restaurants", "Merge Restaurants", "Restaurant Detail", "Create Restaurant",
    "Delete Restaurant", "Claims Queue"
])

# --- Tab 1: Merged restaurants ---
with tab1:
    st.subheader("Restaurants Marked as Merged")

    try:
        merged_resp = requests.get("http://web-api:4000/restaurant_admin/restaurants/merged")
        merged_resp.raise_for_status()
        merged_restaurants = merged_resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching merged restaurants: {e}")
        st.error("Could not load merged restaurants.")
        merged_restaurants = []

    if merged_restaurants:
        st.dataframe(pd.DataFrame(merged_restaurants), use_container_width=True, hide_index=True)
    else:
        st.info("No merged restaurants found.")

# --- Tab: Merge Restaurants ---
with tab_merge:
    st.subheader("Merge Two Restaurants")
    st.write("Merges one restaurant's reviews into a survivor restaurant, and marks the original as 'merged'.")

    merge_from_id = st.number_input("Restaurant ID to merge (will be marked 'merged')", min_value=1, step=1, key="merge_from")
    merge_into_id = st.number_input("Survivor Restaurant ID (receives the reviews)", min_value=1, step=1, key="merge_into")

    confirm_merge = st.checkbox("I'm sure I want to merge these restaurants", key="confirm_merge")

    if st.button("Merge Restaurants", disabled=not confirm_merge):
        if merge_from_id == merge_into_id:
            st.error("Cannot merge a restaurant into itself.")
        else:
            payload = {"mergeIntoId": merge_into_id}
            try:
                merge_resp = requests.put(f"http://web-api:4000/restaurants/{merge_from_id}", json=payload)
                merge_resp.raise_for_status()
                st.success(f"Restaurant {merge_from_id} merged into {merge_into_id}.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error merging restaurant {merge_from_id} into {merge_into_id}: {e}")
                st.error("Could not merge restaurants. Please try again.")

# --- Tab 2: Full restaurant detail + claims on that restaurant ---
with tab2:
    st.subheader("Look Up a Restaurant")

    lookup_id = st.number_input("Restaurant ID", min_value=1, step=1, key="lookup_id")

    if st.button("Look Up"):
        try:
            full_resp = requests.get(f"http://web-api:4000/restaurant_admin/restaurants/{lookup_id}/full")
            if full_resp.status_code == 404:
                st.warning("Restaurant not found.")
            else:
                full_resp.raise_for_status()
                restaurant = full_resp.json()

                st.write(f"**Name:** {restaurant['name']}")
                st.write(f"**Address:** {restaurant['street']}, {restaurant['city']}, {restaurant.get('state', '')}")
                st.write(f"**Price Range:** {restaurant.get('priceRange', 'N/A')}")
                st.write(f"**Status:** {restaurant.get('Status', 'N/A')}")
                st.write(f"**Partner:** {'Yes' if restaurant.get('isPartner') else 'No'}")

                st.write("**Cuisines:**")
                if restaurant.get('cuisines'):
                    st.dataframe(pd.DataFrame(restaurant['cuisines']), use_container_width=True, hide_index=True)
                else:
                    st.write("None listed.")

                st.write("**Neighborhoods:**")
                if restaurant.get('neighborhoods'):
                    st.dataframe(pd.DataFrame(restaurant['neighborhoods']), use_container_width=True, hide_index=True)
                else:
                    st.write("None listed.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching restaurant {lookup_id} detail: {e}")
            st.error("Could not load restaurant details.")

    st.divider()
    st.subheader("Claims Filed Against This Restaurant")

    if lookup_id:
        try:
            claims_resp = requests.get(f"http://web-api:4000/restaurant_admin/restaurants/{lookup_id}/claims")
            claims_resp.raise_for_status()
            claims = claims_resp.json()

            if claims:
                st.dataframe(pd.DataFrame(claims), use_container_width=True, hide_index=True)
            else:
                st.write("No claims on file for this restaurant.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching claims for restaurant {lookup_id}: {e}")
            st.error("Could not load claims.")

# --- Tab 3: Create restaurant ---
with tab3:
    st.subheader("Add a New Restaurant")

    with st.form("create_restaurant_form"):
        name = st.text_input("Name")
        street = st.text_input("Street Address")
        city = st.text_input("City")
        state = st.text_input("State", value="MA")
        country = st.text_input("Country", value="US")
        price_range = st.selectbox("Price Range", ["$", "$$", "$$$", "$$$$"])
        is_partner = st.checkbox("Partner Restaurant")
        manager_id = st.number_input("Manager ID", min_value=1, step=1)

        submitted = st.form_submit_button("Create Restaurant")

        if submitted:
            if not name or not street or not city:
                st.error("Name, street, and city are required.")
            else:
                payload = {
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "country": country,
                    "priceRange": price_range,
                    "isPartner": is_partner,
                    "managerID": manager_id
                }
                try:
                    create_resp = requests.post("http://web-api:4000/restaurant_admin/restaurants", json=payload)
                    create_resp.raise_for_status()
                    result = create_resp.json()
                    st.success(f"Restaurant created with ID {result['restaurantID']}.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error creating restaurant: {e}")
                    st.error("Could not create restaurant. Please try again.")

# --- Tab 4: Delete restaurant ---
with tab4:
    st.subheader("Delete a Restaurant")
    st.warning("This action is permanent and cannot be undone.")

    delete_id = st.number_input("Restaurant ID to delete", min_value=1, step=1, key="delete_id")
    force_delete = st.checkbox("Force delete (also removes reviews, reservations, claims, and other linked data)")
    confirm_delete = st.checkbox("I understand this cannot be undone", key="confirm_delete_restaurant")

    if st.button("Delete Restaurant", disabled=not confirm_delete):
        try:
            params = {"force": "true"} if force_delete else {}
            del_resp = requests.delete(f"http://web-api:4000/restaurant_admin/restaurants/{delete_id}", params=params)

            if del_resp.status_code == 409:
                st.error(del_resp.json().get('error', 'This restaurant has linked data. Try force delete.'))
            else:
                del_resp.raise_for_status()
                st.success(f"Restaurant {delete_id} deleted.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting restaurant {delete_id}: {e}")
            st.error("Could not delete restaurant. Please try again.")

# --- Tab 5: Claims queue (approve/reject) ---
with tab5:
    st.subheader("Pending Claims Queue")

    status_filter = st.selectbox("Filter by status", ["All", "pending", "approved", "rejected"], key="claims_status")

    params = {} if status_filter == "All" else {"status": status_filter}

    try:
        claims_resp = requests.get("http://web-api:4000/admin/claims", params=params)
        claims_resp.raise_for_status()
        claims_queue = claims_resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching claims queue: {e}")
        st.error("Could not load claims queue.")
        claims_queue = []

    if claims_queue:
        st.dataframe(pd.DataFrame(claims_queue), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Resolve a Claim")

        claim_ids = [c['claimID'] for c in claims_queue]
        selected_claim_id = st.selectbox("Select claim", claim_ids)
        resolution = st.radio("Resolution", ["approved", "rejected"], horizontal=True)

        if st.button("Submit Resolution", disabled=(acting_admin_id is None)):
            payload = {"status": resolution, "adminID": acting_admin_id}
            try:
                resolve_resp = requests.put(f"http://web-api:4000/admin/claims/{selected_claim_id}", json=payload)
                resolve_resp.raise_for_status()
                st.success(f"Claim {selected_claim_id} {resolution}.")
                st.rerun()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error resolving claim {selected_claim_id}: {e}")
                st.error("Could not resolve claim. Please try again.")
    else:
        st.info("No claims match this filter.")
