import streamlit as st
import requests
import datetime
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"
restaurant_id = st.session_state.get('restaurant_id')

if not restaurant_id:
    st.warning("Pick a restaurant on the Manager Dashboard first.")
    st.stop()

st.title("Seating Chart")

st.image("assets/seatingChart.png", caption="Restaurant Floor Plan", width=400)

selected_date = st.date_input("Date", value=datetime.date.today())

# Load (or offer to create) the chart for this date
try:
    resp = requests.get(f"{API_URL}/seatingchart/restaurants/{restaurant_id}/seatingcharts",
                         params={"date": selected_date})
    charts = resp.json() if resp.status_code == 200 else []
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    charts = []

chart = charts[0] if charts else None

if chart is None:
    st.info(f"No seating chart set up for {selected_date} yet.")
    with st.form("create_chart_form"):
        total_covers = st.number_input("Total tables/covers", min_value=1, max_value=100, value=20)
        if st.form_submit_button("Create Seating Chart for This Date"):
            requests.post(f"{API_URL}/seatingchart/seatingcharts", json={
                "restaurantID": restaurant_id,
                "date": str(selected_date),
                "totalCovers": total_covers,
                "openTable": total_covers
            })
            st.rerun()
    st.stop()

# Simple visual layout — round + rectangular tables, shaded by
# whether they're currently counted as "open" (available)
total = chart['totalCovers']
open_count = chart['openTable']
booked = total - open_count

st.write(f"**{selected_date}** — {open_count} of {total} tables available")

col_img, col_stats = st.columns([2, 1])
with col_img:
    st.image("assets/seatingChart.png", width=350)
with col_stats:
    st.metric("Available", open_count)
    st.metric("Booked", booked)
    st.metric("Total", total)

st.write("---")

# Manager adjusts total covers / how many are currently open
with st.form("update_chart_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_total = st.number_input("Total tables/covers", min_value=1, max_value=100, value=total)
    with col2:
        new_open = st.number_input("Currently available", min_value=0, max_value=new_total, value=min(open_count, new_total))

    if st.form_submit_button("Update Seating Chart"):
        requests.put(f"{API_URL}/seatingchart/seatingcharts/{chart['chartID']}", json={
            "totalCovers": new_total,
            "openTable": new_open
        })
        st.success("Seating chart updated!")
        st.rerun()