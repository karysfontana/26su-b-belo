import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"
restaurant_id = st.session_state.get('restaurant_id')
manager_id = st.session_state.get('manager_id')

if not restaurant_id:
    st.warning("Pick a restaurant on the Manager Dashboard first.")
    st.stop()

st.title("Reservations")

try:
    resp = requests.get(f"{API_URL}/reservations/restaurants/{restaurant_id}/reservations")
    reservation_list = resp.json() if resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    reservation_list = []

status_filter = st.selectbox("Filter by status",
                               ["pending", "accepted", "declined", "completed", "no_show", "All"])

filtered = reservation_list if status_filter == "All" \
    else [r for r in reservation_list if r['status'] == status_filter]

if not filtered:
    st.write("No reservations match this filter.")
else:
    for r in filtered:
        with st.container(border=True):
            st.write(f"**{r['date']}** — Party of {r['partySize']}")
            st.caption(f"Status: {r['status']}")
            if r.get('request'):
                st.caption(f"Note: {r['request']}")

            if r['status'] == 'pending':
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("✓ Accept", key=f"accept_{r['resvID']}"):
                        requests.put(f"{API_URL}/reservations/reservations/{r['resvID']}",
                                     json={"status": "accepted", "appManagerID": manager_id})
                        st.rerun()
                with b_col2:
                    if st.button("✗ Decline", key=f"decline_{r['resvID']}"):
                        requests.put(f"{API_URL}/reservations/reservations/{r['resvID']}",
                                     json={"status": "declined", "appManagerID": manager_id})
                        st.rerun()