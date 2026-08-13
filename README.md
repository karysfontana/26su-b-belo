# BELO — CS 3200 Summer B 2026 Project

**Team:** Port Authority
**Members:** Richie Nguyen, Hosam Esawy, Karys Fontana, Nora Harr

BELO is a restaurant-reviewing application that lets users post reviews, make reservations, follow friends, and see the restaurants their friends have reviewed — think a social-graph layer on top of a review platform. Ratings are broken into food, service, and vibe rather than one generic star score, so a review actually communicates *why* a place was good or bad.

## Overview

BELO serves three personas:

- **Customer/Reviewer** (modeled on Peter Griffin) — browses and filters restaurants, writes reviews with food/service/vibe ratings, follows other users, and requests reservations.
- **Restaurant Owner/Manager** (modeled on Bob Belcher) — edits restaurant details and menu items, manages incoming reservations and the walk-in waitlist, and reviews feedback on their restaurant.
- **Platform Admin** (modeled on Judy Hopps) — reviews and resolves ownership claims on restaurant listings, merges duplicate listings, removes reported reviews, suspends flagged accounts, and manages cuisine/neighborhood tags.


## Structure of the Repo

This repository is organized into the same six directories as the course template:

- `./app` — the Streamlit frontend
- `./api` — the Flask REST API, organized into Blueprints by database table/resource:
  `restaurants`, `restaurant_admin`, `customers`, `managers`, `reviews`, `reservations`, `users`, `admin` (claims + logs), `waitlist`, `menu`
- `./database-files` — SQL scripts that build the schema and populate it with realistic mock data (via the Python Faker library)
- `./datasets` — not used in this project
- `./ml-src` — not used in this project (BELO does not incorporate a machine learning model)
- `./docs` — project documentation inherited from the course template

## Prerequisites

You'll need Docker Desktop installed and running. No local Python environment is required to run the app — everything executes inside containers.

## Setting Up and Running the Project

1. Clone the repo:
   ```
   git clone https://github.com/karysfontana/26su-b-belo.git
   cd 26su-b-belo
   ```

2. Create your `.env` file inside the `api/` folder:
   ```
   cd api
   cp .env.template .env
   ```
   Then open `.env` and set a real password for `MYSQL_ROOT_PASSWORD`. Confirm `DB_NAME=BELO` to match the database created by our schema file.

3. From the repo root, start all three containers:
   ```
   docker compose up -d
   ```
   This builds and starts the Streamlit app, the Flask API, and the MySQL database. On first run, MySQL automatically executes every `.sql` file in `database-files/` in alphabetical order — our schema file, followed by our mock data file.

4. Open the app in your browser:
   ```
   http://localhost:8501
   ```
   The API is reachable directly at `http://localhost:4000` for testing individual routes.

### If you change the schema or mock data

MySQL only runs the files in `database-files/` the *first* time its data volume is created — editing a `.sql` file afterward has no effect until the volume is rebuilt:
```
docker compose down -v
docker compose up -d
```
The `-v` flag deletes the existing database volume so your updated files actually run again.

## Handling User Role Access and Control (RBAC)

BELO uses the same lightweight, no-real-authentication RBAC pattern as the course template: clicking a role button on the Home page writes a role string into Streamlit's `session_state`, and `SideBarLinks()` in `app/src/modules/nav.py` renders only the pages appropriate to that role. See the template's `docs/RBAC.md` for the full mechanics — our implementation follows it directly, just with BELO's three personas in place of the template's examples.

| Button | Role string | Redirects to |
|---|---|---|
| Act as a Customer/Reviewer | `customer` | `pages/00_Customer_Home.py` |
| Act as a Restaurant Owner/Manager | `manager` | `pages/10_Manager_Home.py` |
| Act as a Platform Admin | `admin` | `pages/20_Admin_Home.py` |

Rather than hardcoding specific IDs for each persona, our Home page pulls a real customer/manager/admin record from the API at login time — this keeps the login flow working correctly even after the database is reset and reseeded with fresh mock data.

## Machine Learning

Not used in this project. BELO's functionality is fully covered by standard CRUD operations across its REST API; no predictive model was needed or built.

## Known Limitations

A couple of gaps are visible in the current build, called out here rather than glossed over:

- **Seating chart / table-count management** (would support persona story 2.6) has no backend routes yet — this was scoped in our wireframes but not implemented in the API by our Phase 3 deadline.
- **Filing a new ownership claim** (`POST /claims`) is not yet implemented — claims can be viewed and resolved via the API, but the creation step is outstanding.

## Video Demo

[Link to be added]

## Team Contributions

- **Richie Nguyen** — `restaurants`, `restaurant_admin`, `customers`, `managers`, `reviews`, `reservations`, and `users` Flask blueprints; database schema and mock data generation
- **Hosam Esawy, Karys Fontana, Nora Harr** — `admin` (claims/logs), `waitlist`, and `menu` Flask blueprints