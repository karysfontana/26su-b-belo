

import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

OUT = []

def esc(s):
    """Escape single quotes for SQL string literals."""
    return str(s).replace("'", "''")

def sql_str(s):
    return f"'{esc(s)}'" if s is not None else "NULL"

def sql_val(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, datetime):
        return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
    return sql_str(v)

def insert(table, columns, rows):
    """Batch INSERT with multiple VALUES tuples for speed and readability."""
    OUT.append(f"\n-- {table}: {len(rows)} rows")
    col_list = ", ".join(columns)
    lines = []
    for row in rows:
        vals = ", ".join(sql_val(v) for v in row)
        lines.append(f"({vals})")
    OUT.append(f"INSERT INTO {table} ({col_list}) VALUES\n" + ",\n".join(lines) + ";")

DATE_START = datetime(2025, 6, 1)
DATE_END = datetime(2026, 8, 1)

def rand_datetime():
    return fake.date_time_between(start_date=DATE_START, end_date=DATE_END)

# Admin: IDs 1000-1005
admin_ids = list(range(1000, 1006))
admins = [(aid, fake.first_name(), fake.last_name()) for aid in admin_ids]
insert("Admin", ["adminID", "firstname", "lastname"], admins)

# User: IDs 1000-1056
user_ids = list(range(1000, 1057))
manager_user_ids = user_ids[:12]
customer_user_ids = user_ids[12:]

users = []
suspended_user_ids = set(random.sample(user_ids, 4))  # a handful of suspended accounts
for uid in user_ids:
    status = "Suspended" if uid in suspended_user_ids else "active"
    flaggedBy = random.choice(admin_ids) if uid in suspended_user_ids else None
    signup = fake.date_between(start_date=DATE_START, end_date=DATE_END)
    users.append((uid, status, signup, flaggedBy))
insert("User", ["UserID", "status", "signUpDate", "flaggedBy"], users)

# Manager: IDs 1000-1011
manager_ids = list(range(1000, 1012))
managers = [(mid, fake.first_name(), fake.last_name(), uid)
            for mid, uid in zip(manager_ids, manager_user_ids)]
insert("Manager", ["ManagerID", "firstname", "lastname", "userID"], managers)

# Customer: IDs 1000-1044
customer_ids = list(range(1000, 1045))
customers = [(cid, fake.first_name(), fake.last_name(), uid)
             for cid, uid in zip(customer_ids, customer_user_ids)]
insert("Customer", ["customerID", "firstname", "lastname", "userID"], customers)

# Menu: IDs 1000-1034
menu_ids = list(range(1000, 1035))
insert("Menu", ["menuID"], [(mid,) for mid in menu_ids])

# Cuisine_Tags 
CUISINES = ["Italian", "Mexican", "Chinese", "Japanese", "Indian", "Thai",
            "Mediterranean", "American", "French", "Korean", "Vietnamese",
            "Greek", "Spanish", "BBQ", "Seafood", "Vegan", "Pizza", "Bakery"]
cuisine_ids = list(range(1000, 1000 + len(CUISINES)))
cuisine_tags = []
for cid, name in zip(cuisine_ids, CUISINES):
    createdBy = random.choice(admin_ids) 
    cuisine_tags.append((cid, name, createdBy))
insert("Cuisine_Tags", ["cuisineID", "CuisineType", "createdBy"], cuisine_tags)


# Neighborhood_Tag
NEIGHBORHOODS = [("Back Bay", "Boston"), ("Beacon Hill", "Boston"), ("Fenway", "Boston"),
                  ("South End", "Boston"), ("North End", "Boston"), ("Jamaica Plain", "Boston"),
                  ("Dorchester", "Boston"), ("Allston", "Boston"), ("Brighton", "Boston"),
                  ("Cambridge", "Cambridge"), ("Somerville", "Somerville"), ("Quahog", "Quahog")]
neighborhood_ids = list(range(1000, 1000 + len(NEIGHBORHOODS)))
neighborhood_tags = [(nid, city, "MA", name, random.choice(admin_ids))
                      for nid, (name, city) in zip(neighborhood_ids, NEIGHBORHOODS)]
insert("Neighborhood_Tag", ["NeighborhoodID", "city", "State", "name", "CreatedBy"], neighborhood_tags)

# Restaurants: IDs 1000-1034
PRICE_TIERS = ["$", "$$", "$$$", "$$$$"]
restaurant_ids = list(range(1000, 1035))
merged_restaurant_ids = set(random.sample(restaurant_ids, 2)) 

restaurants = []
for rid, mid in zip(restaurant_ids, menu_ids):
    manager = random.choice(manager_ids)
    city, _ = random.choice(NEIGHBORHOODS)
    status = "merged" if rid in merged_restaurant_ids else "active"
    restaurants.append((
        rid,
        fake.company()[:40],
        datetime(2026, 1, 1, random.randint(7, 11), 0, 0),
        datetime(2026, 1, 1, random.randint(19, 23), 0, 0),
        random.choice(PRICE_TIERS),
        "US", "MA", city,
        fake.street_address()[:100],
        fake.boolean(chance_of_getting_true=60),
        status,
        manager,
        mid
    ))
insert("Restaurants",
       ["RestaurantID", "name", "openTime", "closeTime", "priceRange", "country",
        "state", "city", "street", "isPartner", "Status", "ManagerID", "MenuID"],
       restaurants)


# Menu_Item:
ITEM_NAMES = ["House Burger", "Caesar Salad", "Margherita Pizza", "Pad Thai", "Fish Tacos",
              "Ramen Bowl", "Chicken Tikka", "Veggie Wrap", "Grilled Salmon", "Steak Frites",
              "Mushroom Risotto", "BBQ Ribs", "Falafel Plate", "Sushi Roll", "Pho",
              "Tomato Soup", "Garlic Bread", "Cheesecake"]
menu_item_rows = []
item_counter = 0
for mid in menu_ids:
    for _ in range(random.randint(2, 4)):
        item_counter += 1
        price = round(random.uniform(6.99, 34.99), 2)
        menu_item_rows.append((item_counter, mid, price, random.choice(ITEM_NAMES)))
insert("Menu_Item", ["itemID", "menuID", "price", "name"], menu_item_rows)

# Restaurant_cuisine
rc_rows = []
rc_seen = set()
for rid in restaurant_ids:
    picks = random.sample(cuisine_ids, random.randint(3, 4))
    for cid in picks:
        if (cid, rid) not in rc_seen:
            rc_seen.add((cid, rid))
            rc_rows.append((cid, rid))
insert("Restaurant_cuisine", ["CuisineID", "RestaurantID"], rc_rows)

# Restaurant_Neighborhood
rn_rows = [(random.choice(neighborhood_ids), rid) for rid in restaurant_ids]
insert("Restaurant_Neighborhood", ["NeighborhoodID", "RestaurantID"], rn_rows)

# Reviews + Rating 
COMMENTS = [
    "Great food and fast service, will come back.",
    "Solid choice for a weeknight dinner.",
    "A bit pricey for the portion size.",
    "Loved the vibe, perfect for date night.",
    "Service was slow but the food made up for it.",
    "Best meal I've had in months.",
    "Wouldn't rush back, but not bad either.",
    "Cozy spot with a friendly staff.",
    "The seating was cramped but the food was excellent.",
    "Exceeded expectations, highly recommend.",
]
review_ids = list(range(1000, 1180))
flagged_review_ids = set(random.sample(review_ids, 6))

reviews = []
ratings = []
rating_counter = 0
for rvid in review_ids:
    cust = random.choice(customer_ids)
    rest = random.choice(restaurant_ids)
    status = "Removed" if rvid in flagged_review_ids else "active"
    flaggedBy = random.choice(admin_ids) if rvid in flagged_review_ids else None
    reviews.append((rvid, random.choice(COMMENTS), rand_datetime(), status, cust, flaggedBy, rest))
    for rtype in ["food", "service", "Vibe"]:
        rating_counter += 1
        ratings.append((rating_counter, rvid, random.randint(1, 5), rtype))

insert("Reviews", ["reviewID", "comment", "createdAt", "Status", "customerID", "flaggedBy", "RestaurantID"], reviews)
insert("Rating", ["RatingID", "reviewID", "rate", "ratingType"], ratings)

# Claim 
claim_ids = list(range(1000, 1015))
claims = []
for clid in claim_ids:
    submitted = rand_datetime()
    resolved_flag = random.random() > 0.4
    resolved = submitted + timedelta(days=random.randint(1, 14)) if resolved_flag else None
    status = random.choice(["approved", "rejected"]) if resolved_flag else "pending"
    admin_reviewed = random.choice(admin_ids) if resolved_flag else None
    claims.append((clid, submitted, resolved, status, admin_reviewed,
                    random.choice(restaurant_ids), random.choice(manager_ids)))
insert("Claim", ["claimID", "dateSubmitted", "dateResolved", "status", "adminReviewed", "restaurantID", "managerID"], claims)

# Log
LOG_ACTIONS = [
    "Suspended account for suspicious review activity",
    "Approved ownership claim",
    "Rejected ownership claim",
    "Merged duplicate restaurant listing",
    "Removed review reported for harassment",
    "Added new cuisine tag",
    "Added new neighborhood tag",
]
log_rows = [(rand_datetime(), random.choice(LOG_ACTIONS), random.choice(admin_ids)) for _ in range(40)]
insert("Log", ["date", "action", "adminID"], log_rows)

# Reservation 
reservation_ids = list(range(1000, 1140))
reservations = []
for resvid in reservation_ids:
    status = random.choice(["pending", "accepted", "declined", "completed", "no_show"])
    app_manager = random.choice(manager_ids) if status != "pending" else None
    reservations.append((
        resvid, rand_datetime(), fake.sentence()[:80], random.randint(1, 8),
        status, random.choice(customer_ids), app_manager, random.choice(restaurant_ids)
    ))
insert("Reservation", ["resvID", "date", "request", "partySize", "status", "CustomerID", "AppManagerID", "RestaurantID"], reservations)

# SeatingChart 
chart_ids = list(range(1000, 1090))
seating_charts = []
for chid in chart_ids:
    total = random.randint(8, 25)
    seating_charts.append((chid, total, fake.date_between(start_date=DATE_START, end_date=DATE_END),
                            random.randint(0, total), random.choice(restaurant_ids)))
insert("SeatingChart", ["chartID", "totalCovers", "date", "openTable", "RestaurantID"], seating_charts)

# WaitList
waitlist_ids = list(range(1000, 1070))
waitlist_rows = []
for wid in waitlist_ids:
    arrival = rand_datetime()
    seated_flag = random.random() > 0.3
    seated = arrival + timedelta(minutes=random.randint(5, 60)) if seated_flag else None
    waitlist_rows.append((wid, random.randint(1, 6), fake.first_name(), fake.last_name(),
                           arrival, seated, random.choice(manager_ids), random.choice(restaurant_ids)))
insert("WaitList", ["entryID", "partySize", "firstName", "lastName", "arrivalTime", "seatedTime", "ManagerEdit", "RestaurantID"], waitlist_rows)

# Follows 
follows_rows = []
follows_seen = set()
for uid in customer_user_ids:
    targets = random.sample([u for u in customer_user_ids if u != uid], min(3, len(customer_user_ids) - 1))
    for t in targets:
        if (uid, t) not in follows_seen:
            follows_seen.add((uid, t))
            follows_rows.append((uid, t))
insert("Follows", ["followerID", "followingID"], follows_rows)

# ReservedSeating 
rs_pairs = set()
rs_rows = []
sampled_resv = random.sample(reservation_ids, 85)
for resvid in sampled_resv:
    chid = random.choice(chart_ids)
    if (resvid, chid) not in rs_pairs:
        rs_pairs.add((resvid, chid))
        rs_rows.append((resvid, chid))
insert("ReservedSeating", ["resvID", "chartID"], rs_rows)

# seating_WaitList 
sw_pairs = set()
sw_rows = []
sampled_wait = random.sample(waitlist_ids, 50)
for wid in sampled_wait:
    chid = random.choice(chart_ids)
    if (chid, wid) not in sw_pairs:
        sw_pairs.add((chid, wid))
        sw_rows.append((chid, wid))
insert("seating_WaitList", ["chartID", "entryID"], sw_rows)

# flagged_restaurant 
fr_pairs = set()
fr_rows = []
sampled_rest = random.sample(restaurant_ids, 10)
for rid in sampled_rest:
    aid = random.choice(admin_ids)
    if (aid, rid) not in fr_pairs:
        fr_pairs.add((aid, rid))
        fr_rows.append((aid, rid))
insert("flagged_restaurant", ["adminID", "RestaurantID"], fr_rows)

# Write output
with open("belo_mock_data.sql", "w") as f:
    f.write("-- BELO Phase 3 mock data, generated via Faker\n")
    f.write("-- Safe to run AFTER your schema + Phase 2 seed file (IDs start at 1000)\n")
    f.write("USE BELO;\n")
    f.write("\n".join(OUT))
    f.write("\n")

print("Done. Wrote belo_mock_data.sql")
print(f"Total rows generated: {sum(len(x) for x in [admins, users, managers, customers, cuisine_tags, neighborhood_tags, restaurants, menu_item_rows, rc_rows, rn_rows, reviews, ratings, claims, log_rows, reservations, seating_charts, waitlist_rows, follows_rows, rs_rows, sw_rows, fr_rows])}")