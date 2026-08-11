from flask import Flask
from dotenv import load_dotenv
from flask.json.provider import DefaultJSONProvider
from backend.admin.admin_route import admin
from backend.waitlist.waitlist_route import waitlist
from backend.menu.menu_route import menu
from datetime import timedelta
from decimal import Decimal
import os
import logging

from backend.db_connection import init_app as init_db
from backend.Restaurant_admin.restaurant_admin_route import restaurant_admin
from backend.Restaurants.restaurants_routes import restaurants
from backend.customers.customers_routes import customers
from backend.Manager.manager_route import managers
from backend.Review.review_route import reviews
from backend.reservations.reservation_route import reservations
from backend.users.user_route import users

# Flask's default JSON encoder doesn't know how to turn a TIME column
# (which mysql-connector returns as a Python timedelta) or a DECIMAL
# column (returned as Decimal) into JSON. Without this, ANY route that
# does SELECT * on Restaurants (openTime/closeTime) or Menu_Item (price)
# crashes with "Object of type timedelta/Decimal is not JSON serializable".
class CustomJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(obj):
        if isinstance(obj, timedelta):
            return str(obj)          # e.g. "9:00:00"
        if isinstance(obj, Decimal):
            return float(obj)        # e.g. 14.99
        return DefaultJSONProvider.default(obj)
    
def create_app():
    app = Flask(__name__)
    app.json = CustomJSONProvider(app)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(restaurant_admin)
    app.register_blueprint(restaurants)
    app.register_blueprint(customers)
    app.register_blueprint(managers)
    app.register_blueprint(reviews)
    app.register_blueprint(reservations)
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(waitlist)
    app.register_blueprint(menu)

    return app
