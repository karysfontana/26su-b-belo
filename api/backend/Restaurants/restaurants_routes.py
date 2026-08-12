from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
restaurants = Blueprint('restaurants', __name__)
 
 
#List/filter restaurants by cuisine, price, and city
@restaurants.route('/restaurants', methods=['GET'])
def get_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /restaurants route')
        cuisine = request.args.get('cuisine')
        price_range = request.args.get('priceRange')
        city = request.args.get('city')
 
        query = '''
            SELECT DISTINCT r.RestaurantID, r.name, r.priceRange, r.city,
                   r.isPartner, r.Status
            FROM Restaurants r
            LEFT JOIN Restaurant_cuisine rc ON r.RestaurantID = rc.RestaurantID
            LEFT JOIN Cuisine_Tags c ON rc.CuisineID = c.cuisineID
            WHERE r.Status = 'active'
        '''
        params = []
        if cuisine:
            query += ' AND c.CuisineType = %s'
            params.append(cuisine)
        if price_range:
            query += ' AND r.priceRange = %s'
            params.append(price_range)
        if city:
            query += ' AND r.city = %s'
            params.append(city)
 
        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurants: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Get details for one restaurant
@restaurants.route('/restaurants/<int:restaurantID>', methods=['GET'])
def get_restaurant(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        theData = cursor.fetchone()
 
        if not theData:
            return jsonify({'error': 'Restaurant not found'}), 404
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# List a restaurant's current cuisine tags
@restaurants.route('/restaurants/<int:restaurantID>/cuisines', methods=['GET'])
def get_restaurant_cuisines(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT c.cuisineID, c.CuisineType
            FROM Restaurant_cuisine rc
            JOIN Cuisine_Tags c ON rc.CuisineID = c.cuisineID
            WHERE rc.RestaurantID = %s
        ''', (restaurantID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_cuisines: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# 2.2 (Bob): Edit a restaurant's hours, address, price range (edits the Restaurants to merge too)
@restaurants.route('/restaurants/<int:restaurantID>', methods=['PUT'])
def update_restaurant(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /restaurants/{restaurantID} route')
        data = request.get_json()
 
        cursor.execute('SELECT * FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Restaurant not found'}), 404
 
        # --- 3.2: admin merge branch ---
        if 'mergeIntoId' in data:
            survivor_id = data['mergeIntoId']
            cursor.execute(
                'UPDATE Reviews SET RestaurantID = %s WHERE RestaurantID = %s',
                (survivor_id, restaurantID)
            )
            cursor.execute(
                "UPDATE Restaurants SET Status = 'merged' WHERE RestaurantID = %s",
                (restaurantID,)
            )
            get_db().commit()
            return jsonify({'message': f'Restaurant {restaurantID} merged into {survivor_id}'}), 200
 
        # --- 2.2: normal field edit branch ---
        allowed_fields = {'name': 'name', 'openTime': 'openTime', 'closeTime': 'closeTime',
                           'street': 'street', 'priceRange': 'priceRange'}
        update_fields, params = [], []
        for key, column in allowed_fields.items():
            if key in data:
                update_fields.append(f'{column} = %s')
                params.append(data[key])
 
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
 
        params.append(restaurantID)
        query = f'UPDATE Restaurants SET {", ".join(update_fields)} WHERE RestaurantID = %s'
        cursor.execute(query, params)
        get_db().commit()
 
        return jsonify({'message': f'Restaurant {restaurantID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_restaurant: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#------------------------------------------------------------
# Get a list of all cuisine tags
@restaurants.route('/cuisinetags', methods=['GET'])
def get_cuisine_tags():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Cuisine_Tags')
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_cuisine_tags: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#Create a new cuisine tag
@restaurants.route('/cuisinetags', methods=['POST'])
def create_cuisine_tag():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /cuisinetags route')
        data = request.get_json()
 
        for field in ['name', 'createdBy']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        cursor.execute(
            'INSERT INTO Cuisine_Tags (CuisineType, createdBy) VALUES (%s, %s)',
            (data['name'], data['createdBy'])
        )
        get_db().commit()
        new_id = cursor.lastrowid
 
        return jsonify({'message': 'Cuisine tag created', 'cuisineID': new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_cuisine_tag: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Get a list of all neighborhood tags
@restaurants.route('/neighborhoodtags', methods=['GET'])
def get_neighborhood_tags():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Neighborhood_Tag')
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_neighborhood_tags: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Create a new neighborhood tag (admin)
@restaurants.route('/neighborhoodtags', methods=['POST'])
def create_neighborhood_tag():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /neighborhoodtags route')
        data = request.get_json()
 
        for field in ['name', 'city', 'state', 'createdBy']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        cursor.execute(
            'INSERT INTO Neighborhood_Tag (city, State, name, CreatedBy) VALUES (%s, %s, %s, %s)',
            (data['city'], data['state'], data['name'], data['createdBy'])
        )
        get_db().commit()
        new_id = cursor.lastrowid
 
        return jsonify({'message': 'Neighborhood tag created', 'neighborhoodID': new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_neighborhood_tag: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Remove a cuisine tag from this restaurant (manager)
@restaurants.route('/restaurants/<int:restaurantID>/cuisines/<int:cuisineID>', methods=['DELETE'])
def remove_restaurant_cuisine(restaurantID, cuisineID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /restaurants/{restaurantID}/cuisines/{cuisineID} route')
        cursor.execute(
            'DELETE FROM Restaurant_cuisine WHERE RestaurantID = %s AND CuisineID = %s',
            (restaurantID, cuisineID)
        )
        get_db().commit()
        return jsonify({'message': 'Cuisine tag unlinked from restaurant'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in remove_restaurant_cuisine: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


#Link an existing cuisine tag to this restaurant
@restaurants.route('/restaurants/<int:restaurantID>/cuisines', methods=['POST'])
def add_restaurant_cuisine(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /restaurants/{restaurantID}/cuisines route')
        data = request.get_json()
 
        if 'cuisineID' not in data:
            return jsonify({'error': 'Missing required field: cuisineID'}), 400
 
        cuisine_id = data['cuisineID']
 
        cursor.execute('SELECT * FROM Restaurants WHERE RestaurantID = %s', (restaurantID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Restaurant not found'}), 404
 
        cursor.execute('SELECT * FROM Cuisine_Tags WHERE cuisineID = %s', (cuisine_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Cuisine tag not found'}), 404
 
        cursor.execute(
            'SELECT * FROM Restaurant_cuisine WHERE RestaurantID = %s AND CuisineID = %s',
            (restaurantID, cuisine_id)
        )
        if cursor.fetchone():
            return jsonify({'error': 'This cuisine is already linked to this restaurant'}), 409
 
        cursor.execute(
            'INSERT INTO Restaurant_cuisine (CuisineID, RestaurantID) VALUES (%s, %s)',
            (cuisine_id, restaurantID)
        )
        get_db().commit()
 
        return jsonify({'message': 'Cuisine tag linked to restaurant'}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_restaurant_cuisine: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 