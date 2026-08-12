# BELO — CS 3200 Summer B 2026 Project

**Team:** Port Authority
**Members:** Richie Nguyen, Hosam Esawy, Karys Fontana, Nora Harr

BELO is a restaurant-reviewing application that lets users post reviews, make reservations, follow friends, and see the restaurants their friends have reviewed — a social-graph layer on top of a review platform. Ratings are broken into food, service, and vibe rather than one generic star score, so a review actually communicates *why* a place was good or bad.

## Overview

BELO serves three personas:

- **Customer/Reviewer** — browses and filters restaurants, writes reviews with food/service/vibe ratings, follows other users, and requests reservations.
- **Restaurant Owner/Manager** — edits restaurant details and menu items, manages incoming reservations and the walk-in waitlist, sets seating availability, and reviews feedback on their restaurant.
- **Platform Admin** — reviews and resolves ownership claims on restaurant listings, merges duplicate listings, removes reported reviews, suspends flagged accounts, and manages cuisine/neighborhood tags.

## Structure of the Repo

- `./app` — the Streamlit frontend
- `./api` — the Flask REST API, organized into Blueprints by resource:
  `Restaurant_admin`, `Restaurants`, `customers`, `Manager`, `Review`, `reservations`, `users`, `admin` (claims + logs), `waitlist`, `menu`, `seatingchart`
- `./database-files` — SQL scripts that build the schema and populate it with realistic mock data (via the Python Faker library)
- `./datasets` — not used in this project
- `./ml-src` — not used (BELO does not incorporate a machine learning model)
- `./docs` — project documentation inherited from the course template

### API note

Every blueprint is registered with a `url_prefix` matching its own name (e.g. `restaurants` blueprint → `url_prefix='/restaurants'`). Since each blueprint's individual routes already include their full path, this means most real endpoints are "doubled" — for example, the restaurant list lives at `/restaurants/restaurants`, not `/restaurants`. This is a known quirk of the current setup, not a bug in the routes themselves; when adding a new frontend call, check the actual registered path in `rest_entry.py` rather than assuming.

## Prerequisites

Docker Desktop installed and running. No local Python environment is required — everything executes inside containers.

## Setting Up and Running the Project

1. Clone the repo:
   ```
   git clone https://github.com/karysfontana/26su-b-belo.git
   cd 26su-b-belo
   ```

2. Create your `.env` file inside `api/`:
   ```
   cd api
   cp .env.template .env
   ```
   Set a real password for `MYSQL_ROOT_PASSWORD`. Confirm `DB_NAME=BELO`.

3. From the repo root:
   ```
   docker compose up -d
   ```
   MySQL automatically executes every `.sql` file in `database-files/` in alphabetical order on first run.

4. Open the app:
   ```
   http://localhost:8501
   ```
   The API is reachable directly at `http://localhost:4000` for testing individual routes.

### If you change the schema or mock data

MySQL only runs files in `database-files/` the *first* time its volume is created:
```
docker compose down -v
docker compose up -d
```

## Handling User Role Access and Control (RBAC)

BELO uses the same lightweight, no-real-authentication RBAC pattern as the course template: clicking a role button on the Home page writes a role string into `st.session_state`, and `SideBarLinks()` in `app/src/modules/nav.py` renders only the pages appropriate to that role.

| Button | Role string | Redirects to |
|---|---|---|
| Act as Christopher, a Customer | `customer` | `pages/00_Customer_Home.py` |
| Act as Megan, a Manager | `manager` | `pages/10_Manager_Home.py` |
| Act as Judy, a System Administrator | `admin` | `pages/20_Admin_Home.py` |

Each login sets a hardcoded demo ID (`customer_id`, `manager_id`, or `admin_id` = `1000`) corresponding to a real seeded record, so the logged-in persona's pages have real data to work with immediately.

## Machine Learning

Not used in this project. BELO's functionality is fully covered by standard CRUD operations across its REST API.

## Known Limitations

- **`POST /claims`** does not exist yet — claims can be viewed and resolved via the API, but there is currently no way to file a new ownership claim through the app itself.
- The wireframe's original vision for an interactive map (customer home page, admin dashboard) was not implemented, since the schema does not store restaurant coordinates.

## Video Demo

[Link to be added]

## Team Contributions

- **Richie Nguyen** — `Restaurants`, `Restaurant_admin`, `customers`, `Manager`, `Review`, `reservations`, `users`, and `seatingchart` Flask blueprints; database schema and mock data generation; Helped with Streamlit pages for the Customer and Manager personas
- **Hosam Esawy** — `admin` (claims/logs), `waitlist`, and `menu` Flask blueprints; Streamlit pages for the Admin persona