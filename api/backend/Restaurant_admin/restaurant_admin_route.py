from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
restaurant_admin = Blueprint('restaurant_admin', __name__)
 
 
# List restaurants marked 'merged' 
@restaurant_admin.route('/restaurants/merged', methods=['GET'])
def get_merged_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Restaurants WHERE Status = 'merged'")
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_merged_restaurants: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
# List all claims filed against a specific restaurant 
@restaurant_admin.route('/restaurants/<int:restaurantID>/claims', methods=['GET'])
def get_restaurant_claims(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Claim WHERE restaurantID = %s ORDER BY dateSubmitted DESC',
                        (restaurantID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_claims: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#------------------------------------------------------------
# Full detail: restaurant + its cuisines + its neighborhood, bundled
# in one call (avoids 3 separate round trips from the frontend)
@restaurant_admin.route('/restaurants/<int:restaurantID>/full', methods=['GET'])
def get_restaurant_full(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        restaurant = cursor.fetchone()
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
 
        cursor.execute('''
            SELECT c.cuisineID, c.CuisineType
            FROM Restaurant_cuisine rc
            JOIN Cuisine_Tags c ON rc.CuisineID = c.cuisineID
            WHERE rc.RestaurantID = %s
        ''', (restaurantID,))
        restaurant['cuisines'] = cursor.fetchall()
 
        cursor.execute('''
            SELECT n.NeighborhoodID, n.name, n.city
            FROM Restaurant_Neighborhood rn
            JOIN Neighborhood_Tag n ON rn.NeighborhoodID = n.NeighborhoodID
            WHERE rn.RestaurantID = %s
        ''', (restaurantID,))
        restaurant['neighborhoods'] = cursor.fetchall()
 
        return jsonify(restaurant), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_full: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 

# Create a new restaurant listing.
@restaurant_admin.route('/restaurants', methods=['POST'])
def create_restaurant():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /restaurants route')
        data = request.get_json()
 
        for field in ['name', 'street', 'city', 'managerID']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        cursor.execute('INSERT INTO Menu () VALUES ()')
        new_menu_id = cursor.lastrowid
 
        cursor.execute('''
            INSERT INTO Restaurants
                (name, street, city, state, country, priceRange, isPartner, Status, ManagerID, MenuID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s, %s)
        ''', (
            data['name'], data['street'], data['city'],
            data.get('state', 'MA'), data.get('country', 'US'),
            data.get('priceRange', '$$'), data.get('isPartner', False),
            data['managerID'], new_menu_id
        ))
        new_restaurant_id = cursor.lastrowid
        get_db().commit()
 
        return jsonify({
            'message': 'Restaurant created',
            'restaurantID': new_restaurant_id,
            'menuID': new_menu_id
        }), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_restaurant: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 

# Permanently delete a restaurant listing (including reviews, reservations, etc.)
@restaurant_admin.route('/restaurants/<int:restaurantID>', methods=['DELETE'])
def delete_restaurant(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /restaurants/{restaurantID} route')
        force = request.args.get('force', 'false').lower() == 'true'
 
        cursor.execute('SELECT * FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Restaurant not found'}), 404
 
        if force:
            # Delete dependent rows first, in FK-safe order.
            # Rating cascades automatically via Reviews' ON DELETE CASCADE,
            # so it isn't listed separately here.
            cursor.execute('DELETE FROM Reviews WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM Reservation WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM SeatingChart WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM WaitList WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM Claim WHERE restaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM Restaurant_cuisine WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM Restaurant_Neighborhood WHERE RestaurantID = %s', (restaurantID,))
            cursor.execute('DELETE FROM flagged_restaurant WHERE RestaurantID = %s', (restaurantID,))
 
        cursor.execute('DELETE FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        get_db().commit()
 
        return jsonify({'message': f'Restaurant {restaurantID} deleted'}), 200
    except Error as e:
        get_db().rollback()
        current_app.logger.error(f'Database error in delete_restaurant: {str(e)}')
        if 'foreign key constraint fails' in str(e).lower():
            return jsonify({
                'error': 'This restaurant still has reviews, reservations, or other '
                         'linked data. Add ?force=true to the request to delete it '
                         'and everything attached to it, or resolve those first.'
            }), 409
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()